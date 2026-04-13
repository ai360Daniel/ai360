# ============================================================
# 🔐 UTILIDADES DE USUARIOS
# ============================================================

import json
import hashlib
from datetime import datetime
# from google.cloud import storage

# storage_client = storage.Client()


def hash_password(password):
    """Devuelve el hash SHA-256 de una contraseña."""
    return hashlib.sha256(password.encode()).hexdigest()


def cargar_usuarios() -> list:
    """Carga la lista de usuarios desde GCS (usuarios.json)."""
    bucket_name = "guru_ai360"
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob("registros/usuarios.json")

    if not blob.exists():
        return []

    return json.loads(blob.download_as_text())


def guardar_usuarios(data):
    """Guarda la lista de usuarios en GCS (usuarios.json)."""
    bucket_name = "guru_ai360"
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob("registros/usuarios.json")

    blob.upload_from_string(
        json.dumps(data, ensure_ascii=False, indent=2),
        content_type="application/json"
    )


# ============================================================
# 🔎 VERIFICAR USUARIO
# ============================================================

def verificar_usuario(username, password):
    """
    Verifica si el usuario y la contraseña coinciden.
    Devuelve (True, rol) si es válido, o (False, None) si no lo es.
    """
    data = cargar_usuarios()
    password_hash = hash_password(password)

    for user in data:
        if user["username"] == username and user["password_hash"] == password_hash:
            user["ultimo_login"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            guardar_usuarios(data)
            return True, user.get("rol", "user")

    return False, None


# ============================================================
# ⚙️ GESTIÓN DE USUARIOS (ADMIN)
# ============================================================

def alta_usuario(admin_user, admin_password, username, password, nuevo_rol="user"):
    """
    Crea un nuevo usuario (solo si el rol del solicitante es admin).
    """
    estatus, rol = verificar_usuario(admin_user, admin_password)
    if not estatus or rol != "admin":
        raise PermissionError("Solo los administradores pueden dar de alta usuarios.")

    data = cargar_usuarios()

    if any(u["username"] == username for u in data):
        raise ValueError("Usuario ya existente.")

    user = {
        "username": username,
        "password_hash": hash_password(password),
        "rol": nuevo_rol,
        "fecha_creacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ultimo_login": None
    }

    data.append(user)
    guardar_usuarios(data)
    print(f"✅ Usuario '{username}' creado correctamente.")


def baja_usuario(admin_user, admin_password, username):
    """
    Elimina un usuario del sistema (solo admin).
    """
    estatus, rol = verificar_usuario(admin_user, admin_password)
    if not estatus or rol != "admin":
        raise PermissionError("Solo los administradores pueden eliminar usuarios.")

    data = cargar_usuarios()
    nuevo_data = [u for u in data if u["username"] != username]

    if len(data) == len(nuevo_data):
        raise ValueError("Usuario no encontrado.")

    guardar_usuarios(nuevo_data)
    print(f"🗑️ Usuario '{username}' eliminado correctamente.")


def renombrar_historial_usuario(admin_user, admin_password, username_antiguo, username_nuevo):
    """
    Renombra el archivo CSV de historial de un usuario en GCS cuando cambia su username.
    También renombra la carpeta de reportes asociada al usuario.
    """
    estatus, rol = verificar_usuario(admin_user, admin_password)
    if not estatus or rol != "admin":
        raise PermissionError("Solo los administradores pueden realizar esta acción.")

    bucket_name = "guru_ai360"
    bucket = storage_client.bucket(bucket_name)

    blob_antiguo = bucket.blob(f"registros/usuarios/{username_antiguo}_historial.csv")
    blob_nuevo = bucket.blob(f"registros/usuarios/{username_nuevo}_historial.csv")

    if blob_antiguo.exists():
        bucket.copy_blob(blob_antiguo, bucket, new_name=blob_nuevo.name)
        blob_antiguo.delete()
        print(f"📂 Historial renombrado de '{username_antiguo}' a '{username_nuevo}'.")
    else:
        print(f"⚠️ No se encontró historial para '{username_antiguo}', no se renombrará.")

    prefix_antiguo = f"reportes/{username_antiguo}/"
    blobs_antiguos = list(bucket.list_blobs(prefix=prefix_antiguo))

    if blobs_antiguos:
        for blob in blobs_antiguos:
            nombre_relativo = blob.name[len(prefix_antiguo):]
            nuevo_nombre = f"reportes/{username_nuevo}/{nombre_relativo}"
            bucket.copy_blob(blob, bucket, new_name=nuevo_nombre)
            blob.delete()
        print(f"📁 Carpeta de reportes renombrada de '{username_antiguo}' a '{username_nuevo}'.")
    else:
        print(f"⚠️ No se encontraron reportes para '{username_antiguo}', no se renombrará carpeta.")


def cambiar_usuario(admin_user, admin_password, username, password=None, nuevo_nombre=None, nuevo_rol=None):
    """
    Modifica los datos de un usuario (solo admin).
    Puede cambiar password, nombre de usuario o rol.
    """
    estatus, rol = verificar_usuario(admin_user, admin_password)

    if not estatus or rol != "admin":
        raise PermissionError("Solo los administradores pueden modificar usuarios.")

    data = cargar_usuarios()

    for u in data:
        if u["username"] == username:
            if password:
                u["password_hash"] = hash_password(password)
            if nuevo_nombre and nuevo_nombre != username:
                renombrar_historial_usuario(admin_user, admin_password, username, nuevo_nombre)
                u["username"] = nuevo_nombre
            if nuevo_rol:
                u["rol"] = nuevo_rol

            u["fecha_modificacion"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            guardar_usuarios(data)
            print(f"✏️ Usuario '{username}' actualizado correctamente.")
            return

    raise ValueError("Usuario no encontrado.")


def listar_usuarios(admin_user, admin_password):
    """
    Devuelve la lista de usuarios sin exponer contraseñas (solo admin).
    """
    estatus, rol = verificar_usuario(admin_user, admin_password)
    if not estatus or rol != "admin":
        raise PermissionError("Solo los administradores pueden listar usuarios.")

    data = cargar_usuarios()
    return [{k: v for k, v in u.items() if k != "password_hash"} for u in data]


def cambiar_contrasena(admin_user, admin_password, username, nueva_contrasena):
    """
    Permite cambiar la contraseña de un usuario (solo admin o el mismo usuario).
    """
    estatus, rol = verificar_usuario(admin_user, admin_password)

    if not estatus:
        raise PermissionError("Credenciales inválidas.")

    if rol != "admin" and admin_user != username:
        raise PermissionError("No tienes permiso para cambiar esta contraseña.")

    data = cargar_usuarios()

    for u in data:
        if u["username"] == username:
            u["password_hash"] = hash_password(nueva_contrasena)
            u["fecha_modificacion"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            guardar_usuarios(data)
            print(f"🔒 Contraseña del usuario '{username}' actualizada correctamente.")
            return

    raise ValueError("Usuario no encontrado.")