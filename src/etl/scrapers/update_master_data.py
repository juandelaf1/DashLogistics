import pandas as pd
import requests
import logging
from io import StringIO
from pathlib import Path
from src.database import get_engine

pd.set_option("future.no_silent_downcasting", True)

# Determina la raíz del proyecto de forma robusta
def find_project_root(start_path: Path = None) -> Path:
    """
    Asciende desde start_path hasta encontrar un marcador de proyecto.
    Marcadores: .git, pyproject.toml, setup.cfg, requirements.txt
    Si no se encuentra ninguno, devuelve un fallback basado en parents[3].
    """
    if start_path is None:
        start_path = Path(__file__).resolve()
    cur = start_path
    markers = {".git", "pyproject.toml", "setup.cfg", "requirements.txt"}
    for parent in [cur] + list(cur.parents):
        for m in markers:
            if (parent / m).exists():
                return parent
    try:
        return Path(__file__).resolve().parents[3]
    except Exception:
        return Path(__file__).resolve().parents[0]


PROJECT_ROOT = find_project_root()
LOG_PATH = PROJECT_ROOT / "logs" / "master_update.log"
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
    engine = None
    try:
        engine = get_engine()
    except Exception as e:
        logger.exception(f"No se pudo obtener engine de BD: {e}")
        return

    logger.info("Iniciando actualización de la tabla maestra...")

    csv_path = PROJECT_ROOT / "data" / "clean" / "shipping_data_clean.csv"
    if not csv_path.exists():
        logger.error(f"Archivo no encontrado en: {csv_path}")
        return

    try:
        # 1) Leer CSV limpio
        df_original = pd.read_csv(csv_path, encoding="utf-8")
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
                if df_wiki.shape[1] >= 3:
                    df_wiki = df_wiki.iloc[:, [1, 2]].copy()
                    df_wiki.columns = ["state", "new_population"]
                else:
                    df_wiki = pd.DataFrame(columns=["state", "new_population"])

        # 2b) Limpiar y normalizar Wikipedia  ✅ CORREGIDO AQUÍ
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
            if not df_diesel.empty:
                df_diesel["state"] = (
                    df_diesel["state"].astype(str).str.strip().str.upper()
                )
                df_final = pd.merge(df_final, df_diesel, on="state", how="left")
            else:
                logger.warning("Tabla 'fuel_prices' vacía en la BD.")
        except Exception as e:
            logger.warning(
                f"No se pudo leer tabla 'fuel_prices' desde la BD: {e}"
            )

        # 5) Métrica adicional
        if {"population", "diesel"}.issubset(df_final.columns):
            df_final["pop_per_dollar"] = None
            mask = (
                df_final["diesel"].notna()
                & (df_final["diesel"] != 0)
                & df_final["population"].notna()
            )
            df_final.loc[mask, "pop_per_dollar"] = (
                df_final.loc[mask, "population"]
                / df_final.loc[mask, "diesel"]
            )

        # 6) Guardar en la BD
        df_final.to_sql(
            "master_shipping_data",
            engine,
            if_exists="replace",
            index=False,
        )

        logger.info("Éxito: Tabla 'master_shipping_data' actualizada correctamente.")
        print("[OK] Actualización maestra completada.")

    except requests.RequestException as re:
        logger.exception(f"Error de red al obtener datos externos: {re}")
    except Exception as e:
        logger.exception(f"Error durante el proceso maestro: {e}")
    finally:
        if engine is not None:
            try:
                engine.dispose()
            except Exception:
                pass


if __name__ == "__main__":
    update_everything()
