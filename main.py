from fastapi import FastAPI, HTTPException, Query, Response, Body
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import storage
import bcrypt
from PIL import Image
import io
import os

# Configuración
BUCKET_NAME = "usuarios_plataforma_ai360"

app = FastAPI(title="AI360 Backend Senior")

# --- CONFIGURACIÓN DE CORS (Para que React no falle) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

# --- BASE DE DATOS VOLÁTIL (NOTA: En Senior se usaría Firestore/Cloud SQL) ---
# Por ahora mantendremos la lista, pero agregaremos un usuario ADMIN por defecto 
# para que nunca te quedes fuera al desplegar.
class DB:
    usuarios = [
        {
            "username": "admin",
            "password_hash": bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            "role": "admin"
        }
    ]

db = DB()

# --- SERVICIOS DE USUARIO ---
@app.post("/alta_usuario")
async def alta_usuario(payload: dict = Body(...)):
    data = payload.get("nuevo_usuario")
    if not data:
        raise HTTPException(status_code=400, detail="Faltan datos del usuario")
    
    if any(u['username'] == data['username'] for u in db.usuarios):
        raise HTTPException(status_code=400, detail="El nombre de usuario ya existe")

    password_hash = bcrypt.hashpw(
        data["password_hash"].encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')

    nuevo_usuario = {
        "username": data["username"],
        "password_hash": password_hash,
        "role": data.get("rol", "usuario_estandar"), # Estandarizado con tu Front
        "correo": data.get("correo", ""),
        "empresa": data.get("empresa", ""),
        "puesto": data.get("puesto", "")
    }

    db.usuarios.append(nuevo_usuario)
    return {"message": "Usuario creado con éxito", "username": data["username"]}

@app.post("/login")
async def login(data: dict = Body(...)):
    username = data.get("username")
    password = data.get("password")
    
    user = next((u for u in db.usuarios if u['username'] == username), None)
    
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")

    # Devolvemos 'role' para que tu Front lo lea correctamente
    return {
        "message": "Bienvenido",
        "username": user["username"],
        "role": user.get("role", "usuario_estandar")
    }

# --- GESTIÓN DE EQUIPO (ADMIN ONLY) ---
@app.get("/listar_usuarios")
async def listar_usuarios(admin_user: str = Query(...), admin_password: str = Query(...)):
    admin = next((u for u in db.usuarios if u['username'] == admin_user), None)
    if not admin or admin['role'] != 'admin' or not bcrypt.checkpw(admin_password.encode('utf-8'), admin['password_hash'].encode('utf-8')):
        raise HTTPException(status_code=403, detail="Acceso denegado: Se requieren permisos de administrador")

    return {"usuarios": [{"username": u["username"], "role": u["role"]} for u in db.usuarios]}

# --- EL ENDPOINT DE CAPTURAS/PDF (RESCATADO) ---
@app.post("/generar_captura")
async def generar_captura(data: dict = Body(...)):
    # Aquí es donde va tu lógica de captura de pantalla o generación de PDF
    # Por ahora, aseguramos la conexión con el Bucket que mencionaste
    try:
        username = data.get("username", "anonimo")
        tipo = data.get("dashboard_type", "reporte")
        
        # Simulamos la creación de un reporte (aquí iría tu código de FPDF)
        img = Image.new('RGB', (800, 600), color=(0, 31, 63)) # Azul AI360
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        img_bytes = buf.getvalue()

        # SUBIDA A TU BUCKET REAL
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(f"capturas/{username}_{tipo}.png")
        blob.upload_from_string(img_bytes, content_type='image/png')

        return Response(
            content=img_bytes,
            media_type='image/png',
            headers={"Content-Disposition": f"attachment; filename=reporte_{tipo}.png"}
        )
    except Exception as e:
        print(f"Error en GCS: {e}")
        raise HTTPException(status_code=500, detail="Error al guardar en Cloud Storage")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
