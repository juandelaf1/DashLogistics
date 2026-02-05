from pydantic import BaseModel, Field, field_validator

class ShippingDataSchema(BaseModel):
    """Contrato para validar los datos de envío por estado"""
    rank: int = Field(ge=1) # El rank debe ser 1 o superior
    state: str
    postal: str = Field(min_length=2, max_length=2) # Siempre 2 letras (ej: NY)
    population: float = Field(gt=0) # No puede haber población 0 o negativa

    @field_validator('state')
    def state_to_upper(cls, v):
        """Asegura que el estado esté siempre en mayúsculas para los JOINs"""
        return v.strip().upper()