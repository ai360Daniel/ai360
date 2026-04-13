from pydantic import BaseModel

class Servicio(BaseModel):
    """
    Modelo para representar un servicio en la plataforma AI360.

    Attributes:
        nombre_servicio (str): Nombre del servicio (ej: "Tablero Movilidad").
        link (str): URL o enlace al servicio.
    """
    nombre_servicio: str
    link: str