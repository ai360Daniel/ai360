from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
from models.usuario import Usuario
from services.storage_service import StorageService
from utils.security import hash_password

class UsuarioService:
    """
    Servicio para manejar la lógica de usuarios.
    """

    def __init__(self):
        self.storage = StorageService()
        self.usuarios_path = "registros/usuarios.json"
        self._asegurar_admin()

    def _asegurar_admin(self) -> None:
        """
        Crea un administrador por defecto si no existe ninguno.

        El admin por defecto sirve para poder comenzar a usar AI360 sin una base de datos externa.
        """
        usuarios = self.cargar_usuarios()
        if any(u.get("rol") == "admin" for u in usuarios):
            return

        administrador = Usuario(
            username="admin",
            password_hash=hash_password("admin123"),
            rol="admin",
            correo="admin@ai360.com",
            telefono=None,
            empresa="AI360",
            puesto="Administrador",
            suscripcion="enterprise",
            accesos=["guru", "tablero_movilidad", "score_vivienda", "precios_vivienda"],
            fecha_creacion=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ultimo_login=None,
            fecha_modificacion=None,
        )
        usuarios.append(administrador.dict())
        self.guardar_usuarios(usuarios)
        print("✅ Administrador por defecto creado: admin / admin123")

    def cargar_usuarios(self) -> List[Dict[str, Any]]:
        """
        Carga la lista de usuarios desde GCS.

        Returns:
            List[Dict[str, Any]]: Lista de usuarios.
        """
        return self.storage.cargar_datos(self.usuarios_path)

    def guardar_usuarios(self, usuarios: List[Dict[str, Any]]) -> None:
        """
        Guarda la lista de usuarios en GCS.

        Args:
            usuarios (List[Dict[str, Any]]): Lista de usuarios a guardar.
        """
        self.storage.guardar_datos(self.usuarios_path, usuarios)

    def verificar_usuario(self, username: str, password: str) -> Tuple[bool, Optional[str]]:
        """
        Verifica si el usuario y la contraseña coinciden.

        Args:
            username (str): Nombre de usuario.
            password (str): Contraseña en texto plano.

        Returns:
            Tuple[bool, Optional[str]]: (True, rol) si válido, (False, None) si no.
        """
        usuarios = self.cargar_usuarios()
        password_hash = hash_password(password)

        for user in usuarios:
            if user["username"] == username and user["password_hash"] == password_hash:
                user["ultimo_login"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.guardar_usuarios(usuarios)
                return True, user.get("rol", "user")

        return False, None

    def validar_administrador(self, admin_user: str, admin_password: str) -> bool:
        """
        Valida que las credenciales correspondan a un administrador válido.

        Esta función es reutilizable en todos los endpoints que requieren permisos de admin.

        Args:
            admin_user (str): Nombre de usuario administrador.
            admin_password (str): Contraseña del administrador en texto plano.

        Returns:
            bool: True si las credenciales son válidas y el usuario es admin, False si no.

        Validaciones realizadas:
            - Verifica que el usuario exista en el sistema
            - Verifica que la contraseña sea correcta (usando hash)
            - Verifica que el rol del usuario sea "admin"
        """
        # Validar credenciales del administrador
        usuarios = self.cargar_usuarios()
        password_hash = hash_password(admin_password)

        for user in usuarios:
            # Verificar que el usuario existe y la contraseña coincide
            if user["username"] == admin_user and user["password_hash"] == password_hash:
                # Verificar rol de administrador
                if user.get("rol") == "admin":
                    # Actualizar último login del admin
                    user["ultimo_login"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.guardar_usuarios(usuarios)
                    return True

        return False

    def alta_usuario(self, nuevo_usuario: Usuario) -> None:
        """
        Crea un nuevo usuario en AI360 sin requerir autorización de admin.

        Args:
            nuevo_usuario (Usuario): Datos del nuevo usuario.

        Raises:
            ValueError: Si el usuario ya existe.
        """
        usuarios = self.cargar_usuarios()

        if any(u["username"] == nuevo_usuario.username for u in usuarios):
            raise ValueError("Usuario ya existente.")

        user_dict = nuevo_usuario.dict()
        user_dict["fecha_creacion"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        usuarios.append(user_dict)
        self.guardar_usuarios(usuarios)
        print(f"✅ Usuario '{nuevo_usuario.username}' creado correctamente.")

    def baja_usuario(self, admin_user: str, admin_password: str, username: str) -> None:
        """
        Elimina un usuario (solo admin).

        Args:
            admin_user (str): Usuario admin.
            admin_password (str): Contraseña admin.
            username (str): Usuario a eliminar.

        Raises:
            PermissionError: Si las credenciales de admin no son válidas.
            ValueError: Si el usuario a eliminar no existe.
        """
        # Validar credenciales del administrador
        if not self.validar_administrador(admin_user, admin_password):
            raise PermissionError("Credenciales de administrador inválidas.")

        usuarios = self.cargar_usuarios()
        
        # Verificar que el usuario a eliminar existe
        usuario_encontrado = False
        for u in usuarios:
            if u["username"] == username:
                usuario_encontrado = True
                break
        
        if not usuario_encontrado:
            raise ValueError("Usuario no encontrado.")
        
        # Ejecutar acción solo si es admin: eliminar el usuario
        nuevo_usuarios = [u for u in usuarios if u["username"] != username]
        self.guardar_usuarios(nuevo_usuarios)
        print(f"🗑️ Usuario '{username}' eliminado correctamente.")

    def modificar_usuario(self, admin_user: str, admin_password: str, username: str, updates: Dict[str, Any]) -> None:
        """
        Modifica datos de un usuario (solo admin).

        Args:
            admin_user (str): Usuario admin.
            admin_password (str): Contraseña admin.
            username (str): Usuario a modificar.
            updates (Dict[str, Any]): Campos a actualizar.

        Raises:
            PermissionError: Si las credenciales de admin no son válidas.
            ValueError: Si el usuario a modificar no existe.
        """
        # Validar credenciales del administrador
        if not self.validar_administrador(admin_user, admin_password):
            raise PermissionError("Credenciales de administrador inválidas.")

        usuarios = self.cargar_usuarios()

        # Ejecutar acción solo si es admin: modificar el usuario
        for u in usuarios:
            if u["username"] == username:
                for key, value in updates.items():
                    if key == "password":
                        u["password_hash"] = hash_password(value)
                    else:
                        u[key] = value
                u["fecha_modificacion"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.guardar_usuarios(usuarios)
                print(f"✏️ Usuario '{username}' actualizado correctamente.")
                return

        # Si no encontró el usuario, lanzar error
        raise ValueError("Usuario no encontrado.")

    def listar_usuarios(self, admin_user: str, admin_password: str) -> List[Dict[str, Any]]:
        """
        Lista usuarios sin contraseñas (solo admin).

        Args:
            admin_user (str): Usuario admin.
            admin_password (str): Contraseña admin.

        Returns:
            List[Dict[str, Any]]: Lista de usuarios sin mostrar hashes de contraseña.

        Raises:
            PermissionError: Si las credenciales de admin no son válidas.
        """
        # Validar credenciales del administrador
        if not self.validar_administrador(admin_user, admin_password):
            raise PermissionError("Credenciales de administrador inválidas.")

        # Ejecutar acción solo si es admin: obtener lista de usuarios
        usuarios = self.cargar_usuarios()
        return [{k: v for k, v in u.items() if k != "password_hash"} for u in usuarios]

    def obtener_servicios_usuario(self, username: str) -> List[str]:
        """
        Obtiene la lista de servicios a los que tiene acceso un usuario.

        Args:
            username (str): Nombre de usuario.

        Returns:
            List[str]: Lista de nombres de servicios.
        """
        usuarios = self.cargar_usuarios()
        for u in usuarios:
            if u["username"] == username:
                return u.get("accesos", [])
        return []

    def validar_acceso_servicio(self, username: str, servicio: str) -> bool:
        """
        Verifica si un usuario tiene permisos para acceder a un servicio.

        Args:
            username (str): Nombre de usuario.
            servicio (str): Nombre del servicio solicitado.

        Returns:
            bool: True si el usuario tiene acceso, False si no.
        """
        usuarios = self.cargar_usuarios()
        for u in usuarios:
            if u["username"] == username:
                return servicio in u.get("accesos", [])
        return False