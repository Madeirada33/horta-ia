from pydantic import BaseModel

class DadosHorta(BaseModel):
    planta: str
    umidade_solo: float
    temperatura: float