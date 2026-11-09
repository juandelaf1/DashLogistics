# PR: honest README + CI (rama `chore/honest-readme-ci`)

**Motivo:** alinear narrativa/métricas con evidencia real (P1). El “modelo ML” actual ajusta un coste derivado determinísticamente (circular) — R² alto no implica capacidad predictiva sobre costes reales. Ver `README.md` y `data/dashlogistics.db` (`ml_metrics`).

## Checklist sugerido
- [ ] CI `tests` en verde (local: `python -m pytest -q` → 17 passed, 1 warning pandas/SQLAlchemy no bloqueante).
- [ ] Revisar README/case study externo para no afirmar R²=0.987 como accuracy predictiva real.
- [ ] Sin cambios funcionales de producto; solo honestidad documental/CI.

## Merge
Rama protegida: merge vía PR cuando pase el status check requerido.
