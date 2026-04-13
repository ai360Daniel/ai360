from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Usuario(BaseModel):
    """
    Modelo para representar un usuario en el sistema.

    Attributes:
        username (str): Nombre de usuario único.
        password_hash (str): Hash de la contraseña.
        rol (str): Rol del usuario (ej: "user", "admin").
        correo (Optional[str]): Correo electrónico del usuario.
        telefono (Optional[str]): Número de teléfono.
        empresa (Optional[str]): Empresa donde trabaja.
        puesto (Optional[str]): Puesto o cargo.
        suscripcion (str): Tipo de suscripción (ej: "basic", "pro", "enterprise").
        accesos (List[str]): Lista de nombres de servicios a los que tiene acceso.
        fecha_creacion (Optional[str]): Fecha de creación del usuario.
        ultimo_login (Optional[str]): Fecha del último login.
        fecha_modificacion (Optional[str]): Fecha de última modificación.
    """
    username: str
    password_hash: str
    rol: str = "user"
    correo: Optional[str] = None
    telefono: Optional[str] = None
    empresa: Optional[str] = None
    puesto: Optional[str] = None
    suscripcion: str = "basic"
    accesos: List[str] = []
    fecha_creacion: Optional[str] = None
    ultimo_login: Optional[str] = None
    fecha_modificacion: Optional[str] = None