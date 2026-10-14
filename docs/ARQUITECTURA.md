# Arquitectura Técnica — Logística Rural Colaborativa

---

## 1. ¿Es posible hacer algo real?

**Respuesta corta:** Sí, con fases.

**Respuesta larga:**

| Aspecto | Realidad | Riesgo |
|---------|----------|--------|
| Datos públicos España | Existen (INE, AEMET, IGN, MITMA) | Formato variable, algunos con API key |
| Colaborativo tipo Waze | Posible | **Problema del huevo y la gallina**: sin usuarios no hay datos, sin datos no hay usuarios |
| Algoritmo de rutas compartidas | Factible | OSRM + clustering, ya lo hicimos en USA |
| Impacto real (CO₂, desperdicio) | Medible con datos abiertos | La métrica es honesta aunque aproximada |

**El riesgo real no es técnico — es de adopción.** Construir la tecnología es posible. Conseguir que transportistas y productores la usen es lo difícil.

**Solución:** MVP técnico primero (demo con datos sintéticos + datos abiertos), validación con usuarios después.

---

## 2. Subagentes / Subsistemas

Cada subagente tiene: **contexto** (datos que maneja) + **skills** (lo que sabe hacer) + **output** (lo que produce).

### A1 — Ingestor de Datos (Data Pipeline)

| Contexto | Skills | Output |
|----------|--------|--------|
| Fuentes abiertas España (INE, AEMET, MITMA, MAPA, IGN, OSM, CNMC) | Web scraping, API REST, ETL, validación (Pydantic), SQLAlchemy | Base de datos normalizada (PostgreSQL) con todas las fuentes |

**Responsabilidades:**
- Obtener datos de fuentes oficiales españolas
- Estandarizar formatos (CSV, JSON, GeoJSON, API)
- Validar calidad y consistencia
- Actualización programada (cron, scheduler)
- Fallback ante caída de fuente

**Skills específicos:**
- `requests`, `beautifulsoup4`, `lxml` (scraping)
- `pandas`, `numpy` (transformación)
- `pydantic` (validación)
- `sqlalchemy` + `postgresql` (almacenamiento)

---

### A2 — Motor Geográfico y de Rutas (Geo Engine)

| Contexto | Skills | Output |
|----------|--------|--------|
| OpenStreetMap, IGN Cartociudad, PostGIS, OSRM | Routing (OSRM), cálculo de distancias, isócronas, clustering geoespacial (DBSCAN) | Matriz de distancias, rutas óptimas, zonas de cobertura, mapa de calor |

**Responsabilidades:**
- Calcular distancia y tiempo entre cualquier par de puntos en España
- Optimizar rutas multi-parada (TSP, VRP)
- Identificar clusters de productores para rutas compartidas
- Calcular isócronas de cobertura (ej: qué pueblos están a <30min de un punto de consolidación)

**Skills específicos:**
- `osrm` (routing engine)
- `geopandas`, `shapely`, `folium` (geo)
- `networkx`, `scipy.spatial` (optimización de rutas)
- `openrouteservice` API o OSRM self-hosted
- `PostGIS` (extensiones geográficas PostgreSQL)

---

### A3 — MarketPlace Colaborativo (Matching Engine)

| Contexto | Skills | Output |
|----------|--------|--------|
| Ofertas de espacio (transportistas), demanda de envío (productores), rutas disponibles | Algoritmo de matching, pricing dinámico, sistema de reputación | Conexiones óptimas oferta-demanda, precio sugerido, ranking de fiabilidad |

**Responsabilidades:**
- Emparejar productores con transportistas que ya hacen rutas compatibles
- Calcular precio justo basado en coste compartido
- Sistema de puntuación y reputación (como Wallapop / BlaBlaCar)
- Notificar ofertas y demandas cercanas

**Skills específicos:**
- `pandas`, `numpy` (procesamiento)
- `scikit-learn` (clustering, clasificación)
- `networkx` (grafo de conexiones)
- Redis (caché de ofertas activas, tiempo real)

---

### A4 — Motor Climático (Weather Intelligence)

| Contexto | Skills | Output |
|----------|--------|--------|
| AEMET API, modelo histórico, predicciones a 7 días | Series temporales, anomalías, alertas meteorológicas, impacto en rutas | Alertas activas, predicción de retrasos por clima, ventana óptima de envío |

**Responsabilidades:**
- Consultar predicciones AEMET para rutas activas
- Detectar condiciones adversas (lluvia, nieve, calor extremo)
- Alertar a productores y transportistas sobre riesgos climáticos
- Histórico climático por municipio para planificación estacional

**Skills específicos:**
- API AEMET (OpenData, key required)
- `pandas`, `statsmodels` (series temporales)
- `prophet` o `sklearn` (predicción de anomalías)

---

### A5 — Analítica y ML (Insights Engine)

| Contexto | Skills | Output |
|----------|--------|--------|
| Todas las tablas de los demás agentes | Modelos predictivos (costes, demanda, ahorro), clustering (tipologías de usuarios), optimización (rutas, precios) | Predicciones, clusters, recomendaciones, KPIs de impacto |

**Responsabilidades:**
- Predecir coste de ruta (heredero del modelo de DashLogistics)
- Identificar productores con mayor potencial de ahorro
- Calcular impacto ambiental (CO₂ evitado, comida rescatada)
- Recomendar rutas consolidadas óptimas
- Generar informes de impacto (para presentación, ayudas, inversores)

**Skills específicos:**
- `scikit-learn`, `xgboost`, `optuna`
- `shap` (interpretabilidad)
- `statsmodels` (series temporales, econometría)

---

### A6 — Colaborativo / Tiempo Real (Waze Layer)

| Contexto | Skills | Output |
|----------|--------|--------|
| Eventos en tiempo real (incidencias, ofertas, alertas), sesiones de usuario, geolocalización activa | WebSockets, Redis Pub/Sub, colas de eventos, geofencing, gamificación | Feed en vivo de incidencias, alertas de proximidad, notificaciones push |

**Responsabilidades:**
- Recibir reports de usuarios: "retención en N-430", "gasoil más barato en Moral de Calatrava", "tengo 200kg libres de Écija a Madrid"
- Propagar a usuarios relevantes (geocercas, rutas cercanas)
- Mantener sesiones activas con WebSocket
- Gamificación: puntos por reportar, descuentos por participar
- Moderación de contenido (reportes falsos)

**Skills específicos:**
- `fastapi` + `websockets`
- `redis` (pub/sub, sesiones, colas)
- `geopy`, `shapely` (geocercas, proximidad)
- `PostgreSQL` + `PostGIS` (consultas geo rápidas)

---

### A7 — Frontend / Dashboard (Visualization Layer)

| Contexto | Skills | Output |
|----------|--------|--------|
| Todas las APIs de los agentes anteriores | Dash + Kepler.gl, Plotly, mapas interactivos, componentes dinámicos | Dashboard de monitoreo, mapa colaborativo, interfaz de productor/transportista |

**Responsabilidades:**
- Mapa interactivo con capas (productores, transportistas, rutas activas, incidencias)
- Perfil de productor (historial, costes, ahorro generado)
- Perfil de transportista (rutas, capacidad, ingresos extra)
- Panel de impacto (CO₂, kg rescatados, € ahorrados)

**Skills específicos:**
- `dash` + `kepler.gl` (core)
- `plotly` (gráficos)
- `flask` / `fastapi` (backend de soporte)
- `dash-leaflet` o `folium` (capas adicionales)

---

## 3. Arquitectura de datos

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           AGENTE 1: DATA PIPELINE                       │
│  INE ──► API/CSV ──┐                                                   │
│  AEMET ─► API ─────┤                                                   │
│  IGN ───► GeoJSON ─┤                                                   │
│  MITMA ─► CSV ─────┤──► Extractor ─► Transform ─► Load ─► PostgreSQL   │
│  OSM ───► Overpass ─┤                                                   │
│  MAPA ──► API/CSV ─┤                                                   │
│  CNMC ──► PDF/CSV ─┘                                                   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     PostgreSQL + PostGIS (Single Source of Truth)        │
├─────────────────────────────────────────────────────────────────────────┤
│  tab_municipios  │  tab_productores  │  tab_transportistas              │
│  tab_rutas       │  tab_incidencias  │  tab_ofertas                     │
│  tab_demandas    │  tab_clima        │  tab_reputacion                  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
            ┌──────────────┐ ┌──────────┐ ┌────────────────┐
            │ GEO ENGINE   │ │ MATCHING │ │    ML ENGINE   │
            │ (A2)         │ │ (A3)     │ │    (A5)        │
            │ distances    │ │ matches  │ │ predictions    │
            │ clusters     │ │ pricing  │ │ clusters       │
            │ isochrones   │ │ ranking  │ │ recommendations │
            └──────────────┘ └──────────┘ └────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
            ┌──────────────┐ ┌──────────┐ ┌────────────────┐
            │   WEATHER    │ │  WAZE    │ │  DASHBOARD     │
            │   (A4)       │ │  (A6)    │ │  (A7)          │
            │ alerts       │ │ events   │ │ visualizations │
            │ forecasts    │ │ realtime │ │ kepler.gl      │
            └──────────────┘ └──────────┘ └────────────────┘
```

---

## 4. Datos para España: catálogo completo

### Prioridad Alta (fundacionales)

| Dato | Fuente | Acceso | Formato | Frecuencia |
|------|--------|--------|---------|------------|
| Población por municipio | INE (padrón) | API gratuita, CSV | CSV, JSON | Anual |
| Coordenadas municipios | IGN / OSM | API abierta | GeoJSON, SHP | Estática |
| Distancias entre municipios | OSRM (self-hosted) | API pública o local | JSON | On-demand |
| Clima actual + predicción | AEMET OpenData | API con key gratuita | JSON, XML | Diaria |
| Precio gasoil por provincia | MITMA / Geoportal | API o web scraping | CSV, HTML | Semanal |

### Prioridad Media (enriquecimiento)

| Dato | Fuente | Acceso | Formato | Frecuencia |
|------|--------|--------|---------|------------|
| Censo de transportistas | MITMA (transporte) | Datos agregados públicos | PDF, CSV | Anual |
| Estadísticas agrarias | MAPA | API, CSV, Excel | CSV, XLSX | Anual |
| Precio suelo rural | Idealista / SIX | API (parcial gratuita) | JSON | Trimestral |
| Red viaria + tráfico | DGT / MITMA | Datos abiertos parciales | CSV, SHP | Anual |
| Cobertura internet | CNMC | Informes públicos | PDF, CSV | Anual |
| Ayudas y subvenciones | BOE / NextGen | PDF (manual) | PDF | Ad-hoc |

### Prioridad Baja (complementaria)

| Dato | Fuente | Acceso | Formato |
|------|--------|--------|---------|
| Comercio electrónico rural | CNMC / Observatorios | Informes agregados | PDF |
| Demanda de transporte por provincia | MITMA | Estadísticas | CSV |
| Paro agrario por municipio | SEPE | Datos abiertos | CSV |
| Índice de despoblación | RETO (MITECO) | Datos abiertos | GeoJSON |

---

## 5. Modelo colaborativo tipo Waze — diseño

### ¿Cómo funcionaría?

```
1. Un transportista anuncia: "Mañana salgo de Cáceres a Madrid a las 8am, capacidad libre: 300kg"
2. Productores cercanos reciben notificación: "Hay un transporte disponible en tu zona"
3. Un productor de queso reserva 50kg → se genera match
4. El transportista recoge el queso en ruta → coste compartido
5. Ambos ganan: transportista llena su capacidad, productor paga fracción
6. El sistema aprende: rutas repetitivas, confianza entre usuarios
```

### Capa Waze (tiempo real)

| Feature | Cómo funciona | Tecnología |
|---------|---------------|------------|
| Reportar incidente | Usuario marca en mapa: retención, accidente, radar | WebSocket + geocerca |
| Gasoil barato cercano | Usuario reporta precio en gasolinera | Geocerca + notificación push |
| Oferta de espacio activa | "Tengo 200kg libres desde Écija a Sevilla ahora" | Temporizador + expiración automática |
| Demanda urgente | "Necesito enviar 30kg hoy de un pueblo a la capital" | Matching instantáneo + alerta a transportistas |
| Reputación | Rating post-entrega (como BlaBlaCar) | Score compuesto (5 estrellas + nº viajes + antigüedad) |

### Problema del arranque en frío (cold start)

**El problema:** Sin usuarios no hay datos colaborativos. Sin datos colaborativos, la plataforma no es útil.

**Solución por fases:**

| Fase | Cómo se consiguen datos |
|------|------------------------|
| **0** | Datos abiertos + simulaciones (productores y transportistas sintéticos basados en datos reales del MAPA/MITMA) |
| **1** | Invitación a cooperativas y asociaciones agrarias (no personas, sino organizaciones) |
| **2** | Incentivos: primeras entregas gratis o a coste subvencionado |
| **3** | Crecimiento orgánico: el ahorro genera más usuarios |

---

## 6. ¿Qué skills necesita el equipo?

| Rol | Agentes que cubre | Skills clave |
|-----|-------------------|--------------|
| **Data Engineer** | A1, A2 | Python, SQL, ETL, APIs, PostgreSQL, Geo |
| **Backend Developer** | A3, A6 | FastAPI, Redis, WebSockets, Docker |
| **ML Engineer** | A4, A5 | scikit-learn, statsmodels, clustering, series temporales |
| **Frontend / Dashboard** | A7 | Dash, Kepler.gl, Plotly, HTML/CSS/JS |
| **DevOps** | Todos | Docker, CI/CD, deploy, monitoring |
| **Domain Expert** | Todos | Logística rural, cadena de frío, regulación española |

**¿Cuántas personas?**
- **Mínimo técnico:** 2 (Data Engineer + Backend/Frontend) — las skills se solapan
- **Recomendado:** 3 (Data Engineer + Backend + Dashboard/ML)
- **Tú solo:** viable, pero requiere tiempo. Priorizar A1 + A2 + A3 como base.

---

## 7. Hoja de ruta

| Fase | Qué | Agentes | Tiempo estimado |
|------|-----|---------|-----------------|
| **0** | Diseño del modelo de datos España + ingesta inicial fuentes abiertas | A1 | 2-3 semanas |
| **0.5** | Motor de rutas con OSRM (España) + clustering de productores | A2 | 1-2 semanas |
| **1** | MVP dashboard: mapa colaborativo con datos sintéticos + calculadora de ahorro | A7 (fase 1) | 2 semanas |
| **2** | Matching engine: conectar oferta y demanda de espacio | A3 | 2 semanas |
| **3** | Capa colaborativa (reportes, WebSocket, reputación) | A6 | 2-3 semanas |
| **4** | ML: predicción de costes, recomendación de rutas, impacto ambiental | A5 | 2 semanas |
| **5** | Clima: alertas, predicciones, integración con rutas | A4 | 1-2 semanas |

**Total estimado: ~12-16 semanas** para un MVP completo con datos reales.

---

## 8. Preguntas para decidir ahora

- [ ] ¿Arrancamos repo nuevo o usamos DashLogistics como base técnica?
- [ ] ¿Nombre del proyecto?
- [ ] ¿MVP demo técnica (datos públicos) o validación con usuarios reales primero?
- [ ] ¿Incluimos clima desde fase 1 o fase 4?
- [ ] ¿Plazo realista para el trabajo final?
