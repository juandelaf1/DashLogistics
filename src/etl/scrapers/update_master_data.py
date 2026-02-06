# src/etl/update_master_data.py
import pandas as pd
import requests
import logging
from io import StringIO
from pathlib import Path
from src.database import get_engine

pd.set_option("future.no_silent_downcasting", True)

BASE_DIR = Path(__file__).resolve().parents[2]
LOG_PATH = BASE_DIR / "logs" / "master_update.log"
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


def update_everything():
    """
    Actualiza la tabla maestra 'master_shipping_data' combinando:
    - CSV limpio local (data/clean/shipping_data_clean.csv)
    - Poblaciones desde Wikipedia
    - Precios de diesel desde la tabla 'fuel_prices' en la BD
    """
    engine = get_engine()
    logger.info("Iniciando actualización de la tabla maestra...")

    csv_path = BASE_DIR / "data" / "clean" / "shipping_data_clean.csv"
    if not csv_path.exists():
        logger.error(f"Archivo no encontrado en: {csv_path}")
        return

    try:
        # 1) Leer CSV limpio
        df_original = pd.read_csv(csv_path)
        if "state" not in df_original.columns:
            logger.error("El CSV no contiene la columna 'state'. Abortando.")
            return

        df_original["state"] = (
            df_original["state"].astype(str).str.strip().str.upper()
        )

        # 2) Obtener poblaciones desde Wikipedia
        wiki_url = "https://en.wikipedia.org/wiki/List_of_U.S._states_and_territories_by_population"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(wiki_url, headers=headers, timeout=15)
        resp.raise_for_status()

        tables = pd.read_html(StringIO(resp.text))

        if not tables:
            logger.warning("No se encontraron tablas en la página de Wikipedia.")
            df_wiki = pd.DataFrame(columns=["state", "new_population"])
        else:
            df_wiki = tables[0].copy()

            possible_name_cols = [
                c for c in df_wiki.columns
                if "state" in str(c).lower() or "name" in str(c).lower()
            ]
            possible_pop_cols = [
                c for c in df_wiki.columns
                if "population" in str(c).lower() or "pop" in str(c).lower()
            ]

            if possible_name_cols and possible_pop_cols:
                df_wiki = df_wiki[
                    [possible_name_cols[0], possible_pop_cols[0]]
                ].copy()
                df_wiki.columns = ["state", "new_population"]
            else:
                try:
                    df_wiki = df_wiki.iloc[:, [1, 2]].copy()
                    df_wiki.columns = ["state", "new_population"]
                except Exception:
                    df_wiki = pd.DataFrame(
                        columns=["state", "new_population"]
                    )

        # 2b) Limpiar y normalizar Wikipedia
        if not df_wiki.empty:
            df_wiki["state"] = (
                df_wiki["state"]
                .astype(str)
                .str.replace(r"\[.*\]", "", regex=True)
                .str.strip()
                .str.upper()
            )

            df_wiki["new_population"] = pd.to_numeric(
                df_wiki["new_population"]
                .astype(str)
                .str.replace(",", ""),
                errors="coerce",
            )
        else:
            logger.warning("df_wiki vacío tras el parsing.")

        # 3) Merge CSV con poblaciones
        df_final = pd.merge(df_original, df_wiki, on="state", how="left")

        if "population" in df_final.columns:
            df_final["population"] = df_final["new_population"].fillna(
                df_final["population"]
            )
        else:
            df_final["population"] = df_final["new_population"]

        df_final = df_final.drop(columns=["new_population"], errors="ignore")

        # 4) Añadir precios de diesel desde la BD
        try:
            df_diesel = pd.read_sql(
                "SELECT state, diesel FROM fuel_prices", engine
            )
            df_diesel["state"] = (
                df_diesel["state"].astype(str).str.strip().str.upper()
            )
            df_final = pd.merge(df_final, df_diesel, on="state", how="left")
        except Exception as e:
            logger.warning(
                f"No se pudo leer tabla 'fuel_prices' desde la BD: {e}"
            )

        # 5) Calcular métricas adicionales (VECTORIAL)
        if {"population", "diesel"}.issubset(df_final.columns):
            df_final["pop_per_dollar"] = (
                df_final["population"] / df_final["diesel"]
            )

            df_final.loc[
                (df_final["diesel"] == 0)
                | df_final["population"].isna()
                | df_final["diesel"].isna(),
                "pop_per_dollar",
            ] = None

        # 6) Guardar en la base de datos
        df_final.to_sql(
            "master_shipping_data",
            engine,
            if_exists="replace",
            index=False,
        )

        logger.info(
            "Éxito: Tabla 'master_shipping_data' actualizada correctamente."
        )
        print("[OK] Actualización maestra completada.")

    except requests.RequestException as re:
        logger.exception(
            f"Error de red al obtener datos externos: {re}"
        )
    except Exception as e:
        logger.exception(f"Error durante el proceso maestro: {e}")

        
if __name__ == "__main__":
    update_everything()
