from fastapi import FastAPI, HTTPException, Query, Response, Body
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import storage
import bcrypt
from PIL import Image
import io
import os

BUCKET_NAME = "usuarios_plataforma_ai360"

class UsuarioService:
    def __init__(self):
        # Admin por defecto para no quedarse fuera al desplegar
        self.usuarios = [
            {
                "username": "admin",
                "password_hash": bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                "role": "admin"
            }
        ]

    def crear_usuario(self, data):
        if any(u['username'] == data['username'] for u in self.usuarios):
            raise HTTPException(status_code=400, detail="El nombre de usuario ya existe")
        
        # Recibir password sin encriptar y hashearlo aquí
        password_hash = bcrypt.hashpw(
            data["password"].encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')
        
        usuario = {
            "username": data["username"],
            "password_hash": password_hash,
            "role": data.get("role", "usuario_estandar"),  # Por defecto usuario estándar
            "correo": data.get("correo", ""),
            "empresa": data.get("empresa", ""),
            "puesto": data.get("puesto", "")
        }
        self.usuarios.append(usuario)
        return {"message": "Usuario creado con éxito", "username": data["username"]}

    def login(self, username, password):
        user = next((u for u in self.usuarios if u['username'] == username), None)
        if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
        return {
            "message": "Bienvenido",
            "username": user["username"],
            "role": user.get("role", "usuario_estandar")
        }

    def listar_usuarios(self, admin_user, admin_password):
        admin = next((u for u in self.usuarios if u['username'] == admin_user), None)
        if not admin or admin['role'] != 'admin' or not bcrypt.checkpw(admin_password.encode('utf-8'), admin['password_hash'].encode('utf-8')):
            raise HTTPException(status_code=403, detail="Acceso denegado: Se requieren permisos de administrador")
        return {"usuarios": [{"username": u["username"], "role": u["role"]} for u in self.usuarios]}

    def modificar_usuario(self, admin_user, admin_password, username, updates):
        admin = next((u for u in self.usuarios if u['username'] == admin_user), None)
        if not admin or admin['role'] != 'admin' or not bcrypt.checkpw(admin_password.encode('utf-8'), admin['password_hash'].encode('utf-8')):
            raise HTTPException(status_code=403, detail="Acceso denegado: Se requieren permisos de administrador")
        user = next((u for u in self.usuarios if u['username'] == username), None)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        user['role'] = updates.get('role', user['role'])
        return {"message": "Usuario actualizado correctamente"}

    def baja_usuario(self, admin_user, admin_password, target_user):
        admin = next((u for u in self.usuarios if u['username'] == admin_user), None)
        if not admin or admin['role'] != 'admin' or not bcrypt.checkpw(admin_password.encode('utf-8'), admin['password_hash'].encode('utf-8')):
            raise HTTPException(status_code=403, detail="Acceso denegado: Se requieren permisos de administrador")
        user = next((u for u in self.usuarios if u['username'] == target_user), None)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        if user['username'] == "admin":
            raise HTTPException(status_code=400, detail="No se puede eliminar el usuario admin")
        self.usuarios.remove(user)
        return {"message": f"Usuario {target_user} eliminado correctamente"}

def generar_captura(username, dashboard_type):
    """Genera una captura de pantalla simulada y la sube a Google Cloud Storage"""
    try:
        # Crear imagen dummy con el color de AI360
        img = Image.new('RGB', (800, 600), color=(0, 31, 63))
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        img_bytes = buf.getvalue()

        # Subir a Google Cloud Storage
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(f"capturas/{username}_{dashboard_type}.png")
        blob.upload_from_string(img_bytes, content_type='image/png')

        # Devolver como descarga
        return Response(
            content=img_bytes,
            media_type='image/png',
            headers={"Content-Disposition": f"attachment; filename=reporte_{dashboard_type}.png"}
        )
    except Exception as e:
        print(f"Error en GCS: {e}")
        raise HTTPException(status_code=500, detail="Error al guardar en Cloud Storage")

app = FastAPI(title="AI360 Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

usuario_service = UsuarioService()

@app.post("/alta_usuario")
async def alta_usuario(payload: dict = Body(...)):
    data = payload.get("nuevo_usuario")
    if not data:
        raise HTTPException(status_code=400, detail="Faltan datos del usuario")
    return usuario_service.crear_usuario(data)

@app.post("/login")
async def login(data: dict = Body(...)):
    username = data.get("username")
    password = data.get("password")
    return usuario_service.login(username, password)

@app.get("/listar_usuarios")
async def listar_usuarios(admin_user: str = Query(...), admin_password: str = Query(...)):
    return usuario_service.listar_usuarios(admin_user, admin_password)

@app.post("/modificar_usuario")
async def modificar_usuario(data: dict = Body(...)):
    return usuario_service.modificar_usuario(
        data['admin_user'], 
        data['admin_password'], 
        data['username'], 
        data['updates']
    )

@app.post("/baja_usuario")
async def baja_usuario(data: dict = Body(...)):
    return usuario_service.baja_usuario(
        data['admin_user'], 
        data['admin_password'], 
        data['target_user']
    )

@app.post("/generar_captura")
async def generar_captura_endpoint(data: dict = Body(...)):
    username = data.get("username", "anonimo")
    dashboard_type = data.get("dashboard_type", "reporte")
    return generar_captura(username, dashboard_type)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
