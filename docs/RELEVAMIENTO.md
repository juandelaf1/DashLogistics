# Proyecto: Logística Colaborativa Rural — Relevamiento

---

## 1. Qué tenemos (legacy)

### DashLogistics (USA)
- Pipeline ETL con BTS FAF, USDA, OSRM, EIA
- Cost estimation engine (fuel + driver + maintenance)
- ML: regresión lineal para predicción de costos (R²=0.987)
- Dashboard Streamlit con mapas, 4 tabs
- Docker + CI

### SkyCast (clima)
- Ingesta de datos meteorológicos por API
- Detección de anomalías

**Aprendizaje:** Streamlit se queda corto para interacción real. La próxima plataforma debe ser Dash + Kepler.

---

## 2. El problema (España)

### El círculo vicioso logístico
```
Productor rural → Poca escala → Transporte caro → Precio final alto
                                       → Consumidor paga mucho
                                       → Productor gana poco
                                       → Comida se desperdicia (no renta moverla)
```

### Datos conocidos
- ~40% de la comida en España se desperdicia
- Una parte significativa es por logística, no por caducidad
- El 80% de los transportistas son autónomos o flotas <5 vehículos
- Los pueblos pequeños no tienen acceso a entregas rápidas/baratas

### La tesis
> Reducir el coste logístico del pequeño productor es la palanca más eficaz contra el desperdicio de comida.

---

## 3. La solución propuesta

### Concepto
Red colaborativa donde transportistas con espacio sobrante ofrecen capacidad a productores rurales, abaratando el coste por kg y rescatando comida que de otro modo se desperdiciaría.

### Triada de impacto
| Dimensión | Problema | Solución | KPI |
|-----------|----------|----------|-----|
| **Económica** | Transporte caro para pequeños | Rutas compartidas, espacio sobrante | €/kg ahorrado |
| **Social** | Pueblos sin acceso a entregas | Red colaborativa con conectividad rural | Productores alcanzados |
| **Ambiental** | Huella de carbono + desperdicio | Menos furgonetas vacías, comida rescatada | kg CO₂ evitados, kg comida salvada |

### Paralelo con modelos existentes
| Modelo | Qué hace | Diferencia |
|--------|----------|------------|
| **BlaBlaCar** | Conductores ofrecen asientos vacíos | Nosotros: espacio de carga en furgonetas/camiones |
| **Waze** | Tráfico colaborativo en tiempo real | Nosotros: oferta/demanda de capacidad logística |
| **Too Good To Go** | Rescata comida de restaurantes | Nosotros: rescata comida desde el origen (productor) |

---

## 4. Stack propuesto

| Capa | Tecnología | Por qué |
|------|------------|---------|
| Frontend | Dash + Kepler.gl | Mapas interactivos, rutas reales, rendimiento |
| Backend | FastAPI + Python | API ligera, async, ML integration |
| BD | PostgreSQL + PostGIS | Datos geoespaciales, rutas |
| Cache/Real-time | Redis | Tracking en tiempo real, sesiones |
| Container | Docker + docker-compose | Portable, deploy simple |
| ML | scikit-learn, optuna | Predicción de rutas, optimización |

---

## 5. Datos necesarios para España

### Públicos / Abiertos
| Fuente | Dato | Uso |
|--------|------|-----|
| **INE** | Población por municipio, densidad rural | Zonas de menor cobertura logística |
| **MITMA** | Movilidad, transporte de mercancías | Flujos de carga por provincia |
| **AEMET** | Datos meteorológicos | Alertas para rutas |
| **IGN / Cartociudad** | Mapas, calles, núcleos poblacionales | Geocodificación de puntos de entrega |
| **CNMC** | Estadísticas de paquetería y correos | Benchmark de mercado |

### A conseguir (colaborativos)
| Dato | Cómo |
|------|------|
| Productores rurales activos | Directorios cooperativas, DO, asociaciones |
| Transportistas autónomos | Encuestas, asociaciones (FENADISMER) |
| Precios reales de transporte | Colaboración de early adopters |
| Puntos de entrega rural | Geolocalización progresiva |

---

## 6. MVP — Fase 0

### Qué construimos primero
1. **Mapa colaborativo de España** con productores y transportistas registrados (simulado con datos abiertos)
2. **Calculadora de ahorro**: "Si compartes ruta, ahorras X€ y evitas Y kg CO₂"
3. **Demo visual** con rutas reales entre provincias usando datos de población y distancia

### Lo que NO construimos en MVP
- Tracking en tiempo real (fase 1)
- Pagos integrados (fase 2)
- App móvil (fase 2)

---

## 7. Preguntas abiertas

- [ ] ¿Nombre del proyecto? (LogiComparte, Rural.Go, ...)
- [ ] ¿MVP validado con usuarios reales o demo técnica primero?
- [ ] ¿Incluimos clima desde el inicio o es fase 2?
- [ ] ¿El trabajo final es este proyecto o este proyecto + algo más?
