from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google.cloud import storage
import bcrypt
from PIL import Image
import io
import os

class UsuarioService:
    def __init__(self):
        self.usuarios = []  # En producción, usar una base de datos

    def crear_usuario(self, data):
        if any(u['username'] == data['username'] for u in self.usuarios):
            raise HTTPException(status_code=400, detail="Usuario ya existe")
        
        # Asumir que password_hash ya está hasheado por el frontend
        usuario = {
            "username": data["username"],
            "password_hash": data["password_hash"],
            "role": data["rol"],  # Mapear rol a role internamente
            "correo": data["correo"],
            "telefono": data["telefono"],
            "empresa": data["empresa"],
            "puesto": data["puesto"],
            "suscripcion": data["suscripcion"],
            "servicios": data["servicios"],
            "accesos": data["accesos"]
        }
        self.usuarios.append(usuario)
        return {"message": "Usuario creado"}

    def login(self, username, password):
        user = next((u for u in self.usuarios if u['username'] == username), None)
        if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            raise HTTPException(status_code=401, detail="Credenciales incorrectas")
        return {"message": "Login exitoso", "rol": user['role']}

    def listar_usuarios(self, admin_user, admin_password):
        admin = next((u for u in self.usuarios if u['username'] == admin_user), None)
        if not admin or admin['role'] != 'admin' or not bcrypt.checkpw(admin_password.encode('utf-8'), admin['password_hash'].encode('utf-8')):
            raise HTTPException(status_code=403, detail="No autorizado")
        return {"usuarios": [{"username": u["username"], "role": u["role"]} for u in self.usuarios]}

    def modificar_usuario(self, admin_user, admin_password, username, updates):
        admin = next((u for u in self.usuarios if u['username'] == admin_user), None)
        if not admin or admin['role'] != 'admin' or not bcrypt.checkpw(admin_password.encode('utf-8'), admin['password_hash'].encode('utf-8')):
            raise HTTPException(status_code=403, detail="No autorizado")
        user = next((u for u in self.usuarios if u['username'] == username), None)
        if not user:
            raise HTTPException(status_code=400, detail="Usuario no encontrado")
        user['role'] = updates['role']
        return {"message": "Cambios guardados correctamente"}

    def baja_usuario(self, admin_user, admin_password, target_user):
        admin = next((u for u in self.usuarios if u['username'] == admin_user), None)
        if not admin or admin['role'] != 'admin' or not bcrypt.checkpw(admin_password.encode('utf-8'), admin['password_hash'].encode('utf-8')):
            raise HTTPException(status_code=403, detail="No autorizado")
        user = next((u for u in self.usuarios if u['username'] == target_user), None)
        if not user:
            raise HTTPException(status_code=400, detail="Usuario no encontrado")
        self.usuarios.remove(user)
        return {"message": f"Usuario {target_user} eliminado correctamente"}

def generar_captura():
    # Crear un PNG dummy
    img = Image.new('RGB', (100, 100), color='red')
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    
    # Subir a Google Cloud Storage
    try:
        client = storage.Client()
        bucket = client.bucket("usuarios_plataforma_ai360")
        blob = bucket.blob("capturas/captura.png")
        blob.upload_from_file(buf, content_type='image/png')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error subiendo a GCS: {str(e)}")
    
    # Devolver como descarga
    response = Response(content=buf.getvalue(), media_type='image/png')
    response.headers["Content-Disposition"] = "attachment; filename=captura.png"
    return response

app = FastAPI()

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
def alta_usuario(data: dict):
    return usuario_service.crear_usuario(data['nuevo_usuario'])

@app.post("/login")
def login(data: dict):
    return usuario_service.login(data['username'], data['password'])

@app.get("/listar_usuarios")
def listar_usuarios(admin_user: str = Query(...), admin_password: str = Query(...)):
    return usuario_service.listar_usuarios(admin_user, admin_password)

@app.post("/modificar_usuario")
def modificar_usuario(data: dict):
    return usuario_service.modificar_usuario(data['admin_user'], data['admin_password'], data['username'], data['updates'])

@app.post("/baja_usuario")
def baja_usuario(data: dict):
    return usuario_service.baja_usuario(data['admin_user'], data['admin_password'], data['target_user'])

@app.post("/generar_captura")
def generar_captura_endpoint():
    return generar_captura()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
