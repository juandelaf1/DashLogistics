# src/api/shipping_etl_api.py
import logging
import subprocess
import shlex
from pathlib import Path
from typing import Tuple

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
ETL_SCRIPT = ROOT / "src" / "etl" / "etl.py"

def run_etl_process(timeout: int = 600) -> Tuple[int, str, str]:
    """
    Ejecuta el script ETL en un proceso separado y devuelve (returncode, stdout, stderr).
    - timeout: segundos máximos a esperar por la ejecución.
    """
    if not ETL_SCRIPT.exists():
        msg = f"Script ETL no encontrado en: {ETL_SCRIPT}"
        logger.error(msg)
        return 1, "", msg

    cmd = f"python -u {shlex.quote(str(ETL_SCRIPT))}"
    logger.info(f"Lanzando ETL: {cmd}")
    try:
        proc = subprocess.run(
            shlex.split(cmd),
            capture_output=True,
            text=True,
            timeout=timeout
        )
        stdout = proc.stdout or ""
        stderr = proc.stderr or ""
        logger.info(f"ETL finalizado con código {proc.returncode}")
        if stdout:
            logger.info(f"ETL stdout: {stdout.strip()[:1000]}")
        if stderr:
            logger.warning(f"ETL stderr: {stderr.strip()[:1000]}")
        return proc.returncode, stdout, stderr
    except subprocess.TimeoutExpired as te:
        logger.exception("ETL excedió el tiempo máximo permitido")
        return 2, "", f"TimeoutExpired: {te}"
    except Exception as e:
        logger.exception("Error al ejecutar el ETL")
        return 3, "", str(e)

if __name__ == "__main__":
    code, out, err = run_etl_process()
    print(f"exit_code: {code}")
    if out:
        print("=== STDOUT ===")
        print(out)
    if err:
        print("=== STDERR ===")
        print(err)
