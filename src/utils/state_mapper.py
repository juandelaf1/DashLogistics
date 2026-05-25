# src/utils/state_mapper.py
"""
Módulo centralizado para mapear entre códigos de estado (CA, NY) y nombres completos.
Fuente de verdad para normalización de estados en todo el pipeline.
"""

# Mapeo oficial: State Code ↔ State Name
STATE_CODE_TO_NAME = {
    'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas',
    'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware',
    'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho',
    'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas',
    'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
    'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi',
    'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada',
    'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York',
    'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma',
    'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
    'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah',
    'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia',
    'WI': 'Wisconsin', 'WY': 'Wyoming'
}

# Mapeo inverso: State Name ↔ State Code (case-insensitive)
STATE_NAME_TO_CODE = {v.upper(): k for k, v in STATE_CODE_TO_NAME.items()}

# Ciudades representativas para cada estado (para weather API)
STATE_REPRESENTATIVE_CITIES = {
    'AL': 'Birmingham', 'AK': 'Anchorage', 'AZ': 'Phoenix', 'AR': 'Little Rock',
    'CA': 'Los Angeles', 'CO': 'Denver', 'CT': 'Hartford', 'DE': 'Wilmington',
    'FL': 'Miami', 'GA': 'Atlanta', 'HI': 'Honolulu', 'ID': 'Boise',
    'IL': 'Chicago', 'IN': 'Indianapolis', 'IA': 'Des Moines', 'KS': 'Wichita',
    'KY': 'Louisville', 'LA': 'New Orleans', 'ME': 'Portland', 'MD': 'Baltimore',
    'MA': 'Boston', 'MI': 'Detroit', 'MN': 'Minneapolis', 'MS': 'Jackson',
    'MO': 'Kansas City', 'MT': 'Billings', 'NE': 'Omaha', 'NV': 'Las Vegas',
    'NH': 'Manchester', 'NJ': 'Newark', 'NM': 'Albuquerque', 'NY': 'New York',
    'NC': 'Charlotte', 'ND': 'Fargo', 'OH': 'Columbus', 'OK': 'Oklahoma City',
    'OR': 'Portland', 'PA': 'Philadelphia', 'RI': 'Providence', 'SC': 'Columbia',
    'SD': 'Sioux Falls', 'TN': 'Memphis', 'TX': 'Houston', 'UT': 'Salt Lake City',
    'VT': 'Burlington', 'VA': 'Virginia Beach', 'WA': 'Seattle', 'WV': 'Charleston',
    'WI': 'Milwaukee', 'WY': 'Cheyenne'
}

# Coordenadas (latitud, longitud) para cada estado - para fallback weather API
STATE_COORDINATES = {
    'AL': (32.8067, -86.7113), 'AK': (64.2008, -152.2782), 'AZ': (33.7298, -111.4312),
    'AR': (34.9697, -92.3731), 'CA': (36.1163, -119.6674), 'CO': (39.0598, -105.3111),
    'CT': (41.5978, -72.7554), 'DE': (39.3185, -75.5244), 'FL': (27.9947, -81.7603),
    'GA': (33.0406, -83.6431), 'HI': (21.0943, -157.4983), 'ID': (44.2405, -114.2430),
    'IL': (40.3495, -88.9861), 'IN': (39.8494, -86.2583), 'IA': (42.0115, -93.2105),
    'KS': (38.5266, -96.7265), 'KY': (37.6681, -84.6701), 'LA': (31.1695, -91.8749),
    'ME': (44.6939, -69.3819), 'MD': (39.0639, -76.8021), 'MA': (42.2352, -71.0275),
    'MI': (43.3266, -84.5361), 'MN': (45.6945, -93.9196), 'MS': (32.7416, -89.6787),
    'MO': (38.4561, -92.2884), 'MT': (46.9219, -103.6006), 'NE': (41.4925, -99.9018),
    'NV': (38.8026, -116.4194), 'NH': (43.4525, -71.3127), 'NJ': (40.2206, -74.7597),
    'NM': (34.5199, -105.8701), 'NY': (42.1657, -74.9481), 'NC': (35.6301, -79.8064),
    'ND': (47.5289, -99.784), 'OH': (40.3888, -82.7649), 'OK': (35.5653, -96.9289),
    'OR': (43.8041, -120.5542), 'PA': (40.5908, -77.2098), 'RI': (41.6809, -71.5118),
    'SC': (34.0007, -81.1637), 'SD': (44.2998, -99.4388), 'TN': (35.7478, -86.6923),
    'TX': (31.9686, -99.9018), 'UT': (39.3210, -111.0937), 'VT': (44.0459, -72.7107),
    'VA': (37.4316, -78.6569), 'WA': (47.4009, -121.4905), 'WV': (38.5976, -80.4549),
    'WI': (44.2685, -89.6165), 'WY': (42.7559, -107.3025)
}


def normalize_state_code(state: str) -> str:
    """
    Normaliza cualquier entrada de estado a código de 2 letras (CA, NY, etc).
    
    Args:
        state: Puede ser código ('CA'), nombre completo ('California'), etc.
        
    Returns:
        Código de estado de 2 letras en mayúsculas (CA)
        
    Raises:
        ValueError: Si el estado no es reconocido
    """
    if not state:
        raise ValueError("Estado no puede estar vacío")
    
    state_clean = state.strip().upper()
    
    # Si ya es un código válido (2 letras)
    if len(state_clean) == 2 and state_clean in STATE_CODE_TO_NAME:
        return state_clean
    
    # Si es un nombre completo de estado
    if state_clean in STATE_NAME_TO_CODE:
        return STATE_NAME_TO_CODE[state_clean]
    
    raise ValueError(f"Estado no reconocido: {state}")


def get_city_for_state(state_code: str) -> str:
    """Obtiene la ciudad representativa para un estado."""
    state_code = normalize_state_code(state_code)
    return STATE_REPRESENTATIVE_CITIES.get(state_code, state_code)


def get_coordinates_for_state(state_code: str) -> tuple:
    """Obtiene (lat, lon) para un estado."""
    state_code = normalize_state_code(state_code)
    return STATE_COORDINATES.get(state_code, (None, None))


def get_state_name(state_code: str) -> str:
    """Obtiene el nombre completo del estado."""
    state_code = normalize_state_code(state_code)
    return STATE_CODE_TO_NAME.get(state_code, state_code)
