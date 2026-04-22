import os
import uvicorn
import hashlib
import time
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import storage

# Importaciones de tus archivos locales (Asegúrate que existan)
from models.usuario import Usuario
from services.usuario_service import UsuarioService

app = FastAPI(title="AI360 Backend Gold", description="Gestión completa de Usuarios y Dashboards")

# CONFIGURACIÓN DE CORS REFORZADA PARA FRONTEND
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]
)

usuario_service = UsuarioService()
BUCKET_NAME = "usuarios_plataforma_ai360"

# --- MODELOS DE DATOS (Sincronizados con App.tsx y Dashboard.tsx) ---

class LoginRequest(BaseModel):
    username: str
    password: str

class AltaUsuarioRequest(BaseModel):
    # Esto coincide con el { nuevo_usuario: {...} } de tu App.tsx
    nuevo_usuario: Usuario

class ModificarUsuarioRequest(BaseModel):
    admin_user: str
    admin_password: str
    username: str  # Usuario objetivo
    updates: dict

class BajaUsuarioRequest(BaseModel):
    admin_user: str
    admin_password: str
    target_user: str # Coincide con tu Dashboard.tsx

class CaptureRequest(BaseModel):
    username: str
    dashboard_type: str
    dashboard_url: str

# --- ENDPOINTS DE ADMINISTRACIÓN Y FLUJO ---

@app.post("/alta_usuario", tags=["Admin"])
def alta_usuario(request: AltaUsuarioRequest):
    """Crea un nuevo usuario en el sistema."""
    try:
        # El objeto 'Usuario' ya viene validado por Pydantic
        exito = usuario_service.alta_usuario(request.nuevo_usuario)
        if exito:
            return {"message": f"Usuario {request.nuevo_usuario.username} registrado con éxito"}
        raise HTTPException(status_code=400, detail="El usuario ya existe o los datos son inválidos")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/login", tags=["Usuarios"])
def login(request: LoginRequest):
    """Verifica credenciales y devuelve el rol."""
    valido, rol = usuario_service.verificar_usuario(request.username, request.password)
    if not valido:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    return {"message": "Login exitoso", "rol": rol}

@app.get("/listar_usuarios", tags=["Admin"])
def listar_usuarios(admin_user: str, admin_password: str):
    """Lista todos los usuarios (Solo para admins)."""
    try:
        usuarios = usuario_service.listar_usuarios(admin_user, admin_password)
        return {"usuarios": usuarios}
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/modificar_usuario", tags=["Admin"])
def modificar_usuario(request: ModificarUsuarioRequest):
    """Actualiza datos (como el rol) de un usuario existente."""
    try:
        exito = usuario_service.modificar_usuario(
            request.admin_user,
            request.admin_password,
            request.username,
            request.updates
        )
        if exito:
            return {"message": "Cambios guardados correctamente"}
        raise HTTPException(status_code=400, detail="No se pudo actualizar el usuario")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/baja_usuario", tags=["Admin"])
def baja_usuario(request: BajaUsuarioRequest):
    """Elimina un usuario del sistema."""
    try:
        exito = usuario_service.baja_usuario(
            request.admin_user,
            request.admin_password,
            request.target_user
        )
        if exito:
            return {"message": f"Usuario {request.target_user} eliminado de la base de datos"}
        raise HTTPException(status_code=400, detail="Error al procesar la baja")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- ENDPOINT DE CAPTURA (PNG/PDF) ---

@app.post("/generar_captura", tags=["Capturas"])
def generar_captura(request: CaptureRequest):
    """Simula o genera una captura del dashboard y la sube al Bucket."""
    try:
        # Generar nombre único para el archivo
        nombre_archivo = f"cap_{request.username}_{int(time.time())}.png"
        
        # Contenido binario de una imagen PNG mínima (1x1 transparente) 
        # Aquí es donde en el futuro integrarías Playwright o Selenium
        contenido_binario = (
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
            b'\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xff\xff'
            b'\x3f\x00\x05\xfe\x02\xfe\x0dc\x44\xaf\x00\x00\x00\x00IEND\xaeB`\x82'
        )

        # Subida a Google Cloud Storage
        client = storage.Client()
        bucket = client.get_bucket(BUCKET_NAME)
        blob = bucket.blob(f"capturas/{nombre_archivo}")
        blob.upload_from_string(contenido_binario, content_type='image/png')

        # Responder con el archivo para descarga inmediata en el navegador
        return Response(
            content=contenido_binario,
            media_type="image/png",
            headers={
                "Content-Disposition": f"attachment; filename={nombre_archivo}",
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en Storage: {str(e)}")

# --- INICIO DEL SERVIDOR ---

if __name__ == "__main__":
    # Cloud Run usa la variable de entorno PORT
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
