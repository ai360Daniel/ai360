from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from models.usuario import Usuario
from services.usuario_service import UsuarioService

app = FastAPI(title="AI360 Backend", description="Backend para plataforma AI360")

usuario_service = UsuarioService()

class LoginRequest(BaseModel):
    username: str
    password: str

class AltaUsuarioRequest(BaseModel):
    nuevo_usuario: Usuario

class ModificarUsuarioRequest(BaseModel):
    admin_user: str
    admin_password: str
    username: str
    updates: dict

@app.post("/login")
def login(request: LoginRequest):
    """
    ¿Para qué sirve este endpoint?
    Permite a un usuario iniciar sesión en la plataforma AI360 verificando su nombre de usuario y contraseña.
    Si las credenciales son correctas, devuelve un mensaje de éxito y el rol del usuario (como "user" o "admin").

    Tipo de endpoint:
    POST - Se usa para enviar datos al servidor y verificar credenciales.
    Es el mismo tipo de petición que se usa cuando alguien hace login en una página.

    Parámetros:
    - BODY: Se envía como JSON en el cuerpo de la petición.
      Campos:
        * username: el nombre de usuario, por ejemplo "emilio".
        * password: la contraseña en texto plano, por ejemplo "123456".

    Cómo probarlo en Swagger UI:
    1. Levanta el servidor con uvicorn: uvicorn main:app --reload
    2. Abre el navegador en http://localhost:8000/docs
    3. Busca el endpoint POST /login y haz clic en él.
    4. Presiona el botón "Try it out".
    5. Completa el cuerpo JSON con:
       {"username": "emilio", "password": "123456"}
    6. Haz clic en "Execute".
    7. Debe mostrar la respuesta con:
       {"message": "Login exitoso", "rol": "user"}
    """
    valido, rol = usuario_service.verificar_usuario(request.username, request.password)
    if not valido:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    return {"message": "Login exitoso", "rol": rol}

@app.post("/alta_usuario")
def alta_usuario(request: AltaUsuarioRequest):
    """
    ¿Para qué sirve este endpoint?
    Permite crear un nuevo usuario en AI360 con toda su información (correo, empresa, etc.).
    No se necesita autorización de admin para usar este endpoint.

    Tipo de endpoint:
    POST - Se usa para enviar datos al servidor y crear un nuevo usuario en AI360.
    Es como registrar un usuario nuevo en la plataforma.

    Parámetros:
    - BODY: Se envía como JSON en el cuerpo de la petición.
      Debe contener:
        * nuevo_usuario: un objeto con los datos del usuario.
          Por ejemplo:
          {
            "username": "emilio",
            "password_hash": "hashed_pass",
            "rol": "user",
            "correo": "emilio@empresa.com",
            "empresa": "EmpresaX",
            "puesto": "Analista",
            "suscripcion": "basic",
            "accesos": ["guru"]
          }

    Cómo probarlo en Swagger UI:
    1. Levanta el servidor con uvicorn: uvicorn main:app --reload
    2. Abre el navegador en http://localhost:8000/docs
    3. Busca el endpoint POST /alta_usuario y haz clic en él.
    4. Presiona "Try it out".
    5. Copia el siguiente JSON en el campo del cuerpo:
       {"nuevo_usuario": {"username": "emilio", "password_hash": "hashed_pass", "rol": "user", "correo": "emilio@empresa.com", "empresa": "EmpresaX", "puesto": "Analista", "suscripcion": "basic", "accesos": ["guru"]}}
    6. Haz clic en "Execute".
    7. Debe mostrar la respuesta con:
       {"message": "Usuario creado exitosamente"}
    """
    try:
        usuario_service.alta_usuario(request.nuevo_usuario)
        return {"message": "Usuario creado exitosamente"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/servicios/{username}")
def obtener_servicios(username: str):
    """
    ¿Para qué sirve este endpoint?
    Devuelve la lista de servicios de AI360 a los que un usuario específico tiene acceso (como "guru", "tablero_movilidad", etc.).
    Útil para mostrar al usuario qué herramientas puede usar en la plataforma.

    Tipo de endpoint:
    GET - Se usa para pedir información al servidor sin modificar nada.
    Es como consultar qué servicios tiene asignados un usuario.

    Parámetros:
    - PATH: "username" va en la URL, por ejemplo /servicios/emilio.
      No se envía en el cuerpo, se coloca directamente en la ruta.

    Cómo probarlo en Swagger UI:
    1. Levanta el servidor con uvicorn: uvicorn main:app --reload
    2. Abre el navegador en http://localhost:8000/docs
    3. Busca el endpoint GET /servicios/{username} y haz clic en él.
    4. Presiona "Try it out".
    5. Escribe "emilio" en el campo username.
    6. Haz clic en "Execute".
    7. Debe mostrar la respuesta con:
       {"username": "emilio", "servicios": ["guru", "tablero_movilidad"]}
    """
    servicios = usuario_service.obtener_servicios_usuario(username)
    return {"username": username, "servicios": servicios}

@app.get("/servicios/{username}/{servicio}")
def verificar_acceso_servicio(username: str, servicio: str):
    """
    ¿Para qué sirve este endpoint?
    Verifica si un usuario específico tiene permiso para acceder a un servicio particular de AI360.
    Si no tiene acceso, bloquea la solicitud con un error 403.

    Tipo de endpoint:
    GET - Se usa para pedir al servidor que confirme si el usuario puede abrir un servicio.
    Es una consulta de permisos.

    Parámetros:
    - PATH: "username" y "servicio" van en la URL.
      Ejemplo: /servicios/emilio/guru.
      "servicio" es el nombre del servicio que el usuario quiere usar.

    Cómo probarlo en Swagger UI:
    1. Levanta el servidor con uvicorn: uvicorn main:app --reload
    2. Abre el navegador en http://localhost:8000/docs
    3. Busca el endpoint GET /servicios/{username}/{servicio} y haz clic en él.
    4. Presiona "Try it out".
    5. Escribe "emilio" en username y "guru" en servicio.
    6. Haz clic en "Execute".
    7. Si tiene acceso, verá:
       {"username": "emilio", "servicio": "guru", "acceso": true}
    8. Si no tiene acceso, verá un error 403 con mensaje:
       {"detail": "Acceso denegado al servicio solicitado"}
    """
    tiene_acceso = usuario_service.validar_acceso_servicio(username, servicio)
    if not tiene_acceso:
        raise HTTPException(status_code=403, detail="Acceso denegado al servicio solicitado")
    return {"username": username, "servicio": servicio, "acceso": True}

@app.put("/modificar_usuario")
def modificar_usuario(request: ModificarUsuarioRequest):
    """
    ¿Para qué sirve este endpoint?
    Permite a un administrador modificar los datos de un usuario existente en AI360 (como cambiar contraseña, rol, accesos, etc.).
    Solo los administradores pueden usar este endpoint.

    Tipo de endpoint:
    PUT - Se usa para actualizar o modificar datos de un usuario existente.
    Es como editar el perfil de un usuario en AI360.

    Parámetros:
    - BODY: Se envía como JSON con los datos necesarios.
      Debe tener:
        * admin_user: nombre del administrador que hace el cambio.
        * admin_password: contraseña del administrador.
        * username: usuario que se va a modificar.
        * updates: un objeto con los campos que se desean cambiar.
      Ejemplo:
      {
        "admin_user": "admin",
        "admin_password": "admin123",
        "username": "emilio",
        "updates": {"puesto": "Analista", "accesos": ["guru"]}
      }

    Cómo probarlo en Swagger UI:
    1. Levanta el servidor con uvicorn: uvicorn main:app --reload
    2. Abre el navegador en http://localhost:8000/docs
    3. Busca el endpoint PUT /modificar_usuario y haz clic en él.
    4. Presiona "Try it out".
    5. Copia este JSON en el campo del cuerpo:
       {"admin_user": "admin", "admin_password": "admin123", "username": "emilio", "updates": {"puesto": "Analista", "accesos": ["guru"]}}
    6. Haz clic en "Execute".
    7. Debe mostrar:
       {"message": "Usuario modificado exitosamente"}
    """
    try:
        # Validar credenciales del administrador
        usuario_service.modificar_usuario(request.admin_user, request.admin_password, request.username, request.updates)
        return {"message": "Usuario modificado exitosamente"}
    except PermissionError as e:
        # Credenciales de admin inválidas → HTTP 403
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        # Usuario objetivo no existe → HTTP 404
        raise HTTPException(status_code=404, detail=str(e))

@app.delete("/baja_usuario")
def baja_usuario(admin_user: str, admin_password: str, username: str):
    """
    ¿Para qué sirve este endpoint?
    Permite a un administrador eliminar (dar de baja) a un usuario de la plataforma AI360.
    Solo los administradores pueden usar este endpoint.

    Tipo de endpoint:
    DELETE - Se usa para eliminar un usuario del sistema.
    Es como dar de baja a alguien en la plataforma AI360.

    Parámetros:
    - QUERY: Se envían en la URL después de ?.
      * admin_user: administrador que borra al usuario.
      * admin_password: contraseña del administrador.
      * username: nombre del usuario que se eliminará.
      Ejemplo: /baja_usuario?admin_user=admin&admin_password=admin123&username=emilio

    Cómo probarlo en Swagger UI:
    1. Levanta el servidor con uvicorn: uvicorn main:app --reload
    2. Abre el navegador en http://localhost:8000/docs
    3. Busca el endpoint DELETE /baja_usuario y haz clic en él.
    4. Presiona "Try it out".
    5. En los campos, escribe:
       * admin_user: admin
       * admin_password: admin123
       * username: emilio
    6. Haz clic en "Execute".
    7. Debe mostrar:
       {"message": "Usuario eliminado exitosamente"}
    """
    try:
        # Validar credenciales del administrador
        usuario_service.baja_usuario(admin_user, admin_password, username)
        return {"message": "Usuario eliminado exitosamente"}
    except PermissionError as e:
        # Credenciales de admin inválidas → HTTP 403
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        # Usuario objetivo no existe → HTTP 404
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/listar_usuarios")
def listar_usuarios(admin_user: str, admin_password: str):
    """
    ¿Para qué sirve este endpoint?
    Devuelve una lista de todos los usuarios registrados en AI360, sin mostrar contraseñas.
    Solo los administradores pueden ver esta lista para gestionar usuarios.

    Tipo de endpoint:
    GET - Se usa para pedir al servidor que devuelva la lista de usuarios registrados.
    Es una consulta de administración.

    Parámetros:
    - QUERY: Se envían en la URL después de ?.
      * admin_user: administrador que consulta la lista.
      * admin_password: contraseña del administrador.
      Ejemplo: /listar_usuarios?admin_user=admin&admin_password=admin123

    Cómo probarlo en Swagger UI:
    1. Levanta el servidor con uvicorn: uvicorn main:app --reload
    2. Abre el navegador en http://localhost:8000/docs
    3. Busca el endpoint GET /listar_usuarios y haz clic en él.
    4. Presiona "Try it out".
    5. Escribe "admin" en admin_user y "admin123" en admin_password.
    6. Haz clic en "Execute".
    7. Debe mostrar algo como:
       {"usuarios": [{"username": "emilio", "rol": "user", "correo": "emilio@empresa.com", ...}]}
    """
    try:
        # Validar credenciales del administrador
        usuarios = usuario_service.listar_usuarios(admin_user, admin_password)
        return {"usuarios": usuarios}
    except PermissionError as e:
        # Credenciales de admin inválidas → HTTP 403
        raise HTTPException(status_code=403, detail=str(e))