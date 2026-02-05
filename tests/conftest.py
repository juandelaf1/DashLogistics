import sys
from pathlib import Path

# Asegurar que `src/` esté en sys.path durante la ejecución de tests
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
