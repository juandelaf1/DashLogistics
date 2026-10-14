# Modelo de Variables — Logística Rural Colaborativa

## 1. Clasificación por dimensión

### 📦 LOGÍSTICA (el núcleo)
| Variable | Relacionada con | Impacto en |
|----------|----------------|------------|
| Precio del transporte | Combustible, distancia, volumen | Coste final para productor y consumidor |
| Combustible (gasoil) | Precio global, impuestos, eficiencia vehículo | Coste de cada ruta |
| Tiempos de entrega | Distancia, tráfico, clima, estacionalidad | Satisfacción consumidor, planificación productor |
| Capacidad de carga disponible | nº vehículos, espacio ocioso, retornos vacíos | Precio del transporte compartido |
| Última milla rural | Densidad población, dispersión geográfica | Viabilidad de entrega en zonas poco pobladas |
| Coste por kg·km | Combustible + amortización + mantenimiento + mano de obra | Indicador principal de eficiencia |

### 🌍 AMBIENTAL
| Variable | Relacionada con | Impacto en |
|----------|----------------|------------|
| Desperdicio de comida | Logística ineficiente, sobreproducción | Pérdida económica, emisiones evitables |
| Huella de carbono total | Km recorridos, vehículos en ruta, ocupación | Sostenibilidad del modelo |
| Km vacíos | Rutas sin carga de retorno | CO₂ evitable, coste desperdiciado |
| Packaging / residuos | Tipo de producto, distancia | Huella indirecta |
| Inclemencias del tiempo | Clima adverso, rutas alternativas | Retrasos, pérdida de carga |

### 👥 ACTORES
| Variable | Intereses | Punto de dolor |
|----------|-----------|----------------|
| **Productor rural** | Vender su producción a precio justo | El transporte come su margen |
| **Consumidor final** | Recibir producto fresco a buen precio | Paga sobrecoste logístico |
| **Transportista autónomo** | Llenar su capacidad, evitar vueltas vacías | Falta de visibilidad de demanda |
| **Cooperativa / Asociación** | Agrupar oferta para abaratar costes | Fragmentación del sector |
| **Intermediario logístico** | Optimizar flota | Competencia con grandes operadores |
| **Ayuntamiento / Diputación** | Mantener actividad económica rural | Despoblación, falta de servicios |

### 🏘️ TERRITORIO (España Vaciada)
| Variable | Indicador | Dato fuente |
|----------|-----------|-------------|
| Densidad de población | hab/km² por municipio | INE |
| Distancia a núcleo logístico | km al almacén/plataforma más cercana | IGN / Cartociudad |
| Precio metro cuadrado (suelo/logística) | €/m² por provincia | Idealista, MITMA |
| Nº de productores activos | Altas en Seguridad Social Agraria | MAPA, SS |
| Nº de transportistas por zona | Censo de flotas <5 vehículos | MITMA, FENADISMER |
| Acceso a internet / cobertura | % hogares con banda ancha | CNMC |
| Pueblos en riesgo de despoblación | Categorización RETO | Ministerio Transición |

### 📊 ECONÓMICO
| Variable | Relacionada con | Medición |
|----------|----------------|----------|
| Precio final al consumidor | Coste logístico + margen productor + intermediarios | €/kg |
| Margen del productor | Precio venta - coste producción - coste transporte | % sobre precio final |
| Ahorro por ruta compartida | Coste individual - coste compartido | €/ruta |
| Incentivos fiscales | Subvenciones a logística rural, combustible | BOE, PGE |
| Puestos de trabajo creados | Conductores, gestores de plataforma, puntos de consolidación | Nº empleos directos + indirectos |
| Coste del metro cuadrado logístico | Precio suelo industrial rural vs urbano | €/m² |

### 🏛️ POLÍTICO / LEGAL
| Variable | Cómo afecta | Documento |
|----------|-------------|-----------|
| Legislación de transporte | Capacidad de carga, licencias, tiempos de conducción | Ley de Ordenación del Transporte |
| Incentivos a economía rural | Subvenciones, reducción de cotizaciones | PGE, fondos NextGen |
| Regulación de plataformas colaborativas | Tipo de relación laboral, seguros | Ley Rider, normativa europea |
| Política agroalimentaria | PAC, ayudas a producción local | PAC 2023-2027 |
| Estrategia contra despoblación | Planes de conectividad, incentivos fiscales | RETO |

### 🌦️ CLIMA (SkyCast integration)
| Variable | Relacionada con | Efecto |
|----------|----------------|--------|
| Temperatura extrema | Cadena de frío, pérdida de carga | Desperdicio adicional |
| Lluvia / nieve | Retrasos, rutas alternativas | Tiempos de entrega |
| Viento | Seguridad en carretera, combustible | Coste y riesgo |
| Estacionalidad | Cosechas, demanda de transporte | Disponibilidad de carga |

---

## 2. Relaciones causales clave

```
Precio combustible
       ↓
   Coste por km
       ↓
Precio del transporte ←→ Capacidad de carga disponible
       ↓                          ↓ (si hay red colaborativa)
Margen del productor          Coste compartido más bajo
       ↓
Precio final al consumidor ←→ Desperdicio de comida
                                  (lo que no se vende porque no compensa transportarlo)
       ↓
Población rural atendida ←→ Puestos de trabajo ←→ Precio metro cuadrado
                                  (⬆ actividad económica → ⬆ valor suelo)
       ↓
            Huella de carbono (km totales × emisión por km)
```

---

## 3. Preguntas que el modelo debería responder

- *Dado un conjunto de productores en una comarca, ¿cuál es el coste mínimo de transporte posible con rutas compartidas?*
- *¿Cuántos kg de comida se podrían rescatar si el transporte fuera un X% más barato?*
- *¿Qué rutas tienen mayor potencial de ahorro colaborativo?*
- *¿Dónde hay más espacio logístico ocioso que se podría activar?*
- *¿Cuánto CO₂ se evitaría por cada 10% de ocupación adicional en furgonetas de reparto?*
- *¿Qué incentivo público maximiza el impacto por euro invertido?*
- *¿Qué pueblo tiene más potencial de desarrollo logístico dada su posición y productores?*

---

## 4. Stack de datos para España

| Variable | Fuente | Formato | Acceso |
|----------|--------|---------|--------|
| Población municipal | INE (padrón) | CSV, API | Abierto |
| Precio suelo | Idealista / MITMA | API, informes | Parcial |
| Productores | MAPA (SIGPAC) | GeoJSON | Abierto |
| Transportistas | MITMA (censo) | Agregado | Limitado |
| Clima | AEMET | API REST | Abierto (con key) |
| Carreteras | IGN / OpenStreetMap | GeoJSON | Abierto |
| Incendios / sequía | MITECO | API, CSV | Abierto |
| Ayudas y subvenciones | BOE / NextGen | PDF, CSV | Manual |
