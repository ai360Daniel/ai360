"""
EJEMPLOS DE USO DE ENDPOINTS CON VALIDACIÓN DE ADMINISTRADOR

Este archivo muestra diferentes formas de usar los endpoints corregidos.
Se incluyen ejemplos con:
- requests (Python)
- cURL (Terminal)
- Swagger UI (Navegador)
"""

# ============================================================================
# 1. EJEMPLO CON PYTHON (usando biblioteca requests)
# ============================================================================

print("""
╔══════════════════════════════════════════════════════════════════════════╗
║ EJEMPLO 1: USANDO PYTHON CON REQUESTS                                   ║
╚══════════════════════════════════════════════════════════════════════════╝

Instala requests primero:
    pip install requests

""")

# Descomentar para usar si tienes requests instalado
"""
import requests
import json

BASE_URL = "http://localhost:8000"

# ====== ENDPOINT: DELETE /baja_usuario ======
print("🗑️ EJEMPLO 1: Eliminar un usuario")
print("-" * 70)

# Parámetros
admin_user = "admin"
admin_password = "admin123"  # ✅ Contraseña correcta
username_to_delete = "usuario_prueba"

# Hacer la solicitud DELETE
response = requests.delete(
    f"{BASE_URL}/baja_usuario",
    params={
        "admin_user": admin_user,
        "admin_password": admin_password,
        "username": username_to_delete
    }
)

print(f"Status Code: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

# Respuesta esperada (HTTP 200):
# {
#   "message": "Usuario eliminado exitosamente"
# }

print()
print("🔴 EJEMPLO 1B: Intentar eliminar con contraseña INCORRECTA")
print("-" * 70)

response = requests.delete(
    f"{BASE_URL}/baja_usuario",
    params={
        "admin_user": admin_user,
        "admin_password": "123456",  # ❌ Contraseña incorrecta
        "username": username_to_delete
    }
)

print(f"Status Code: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

# Respuesta esperada (HTTP 403):
# {
#   "detail": "Credenciales de administrador inválidas."
# }

# ====== ENDPOINT: PUT /modificar_usuario ======
print()
print("✏️️ EJEMPLO 2: Modificar un usuario")
print("-" * 70)

modificar_data = {
    "admin_user": "admin",
    "admin_password": "admin123",  # ✅ Contraseña correcta
    "username": "emilio",
    "updates": {
        "puesto": "Senior Analyst",
        "empresa": "Nueva Empresa",
        "accesos": ["guru", "tablero_movilidad"]
    }
}

response = requests.put(
    f"{BASE_URL}/modificar_usuario",
    json=modificar_data
)

print(f"Status Code: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

# Respuesta esperada (HTTP 200):
# {
#   "message": "Usuario modificado exitosamente"
# }

# ====== ENDPOINT: GET /listar_usuarios ======
print()
print("👥 EJEMPLO 3: Listar todos los usuarios")
print("-" * 70)

response = requests.get(
    f"{BASE_URL}/listar_usuarios",
    params={
        "admin_user": "admin",
        "admin_password": "admin123"  # ✅ Contraseña correcta
    }
)

print(f"Status Code: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

# Respuesta esperada (HTTP 200):
# {
#   "usuarios": [
#     {
#       "username": "admin",
#       "rol": "admin",
#       "correo": "admin@ai360.com",
#       ...
#     },
#     ...
#   ]
# }
"""

# ============================================================================
# 2. EJEMPLOS CON cURL (Terminal / Command Line)
# ============================================================================

print("""
╔══════════════════════════════════════════════════════════════════════════╗
║ EJEMPLO 2: USANDO cURL (Terminal)                                       ║
╚══════════════════════════════════════════════════════════════════════════╝

Ejecuta estos comandos en tu terminal (PowerShell, CMD o bash):

""")

curl_examples = """
# ====== DELETE /baja_usuario ======
echo "🗑️ Eliminar un usuario (credenciales CORRECTAS)"
curl -X DELETE "http://localhost:8000/baja_usuario?admin_user=admin&admin_password=admin123&username=emilio"

echo.
echo "🔴 Intentar eliminar con MALA contraseña"
curl -X DELETE "http://localhost:8000/baja_usuario?admin_user=admin&admin_password=123456&username=emilio"

# ====== PUT /modificar_usuario ======
echo "✏️ Modificar un usuario"
curl -X PUT "http://localhost:8000/modificar_usuario" ^
  -H "Content-Type: application/json" ^
  -d "{\"admin_user\":\"admin\",\"admin_password\":\"admin123\",\"username\":\"emilio\",\"updates\":{\"puesto\":\"Senior\"}}"

# ====== GET /listar_usuarios ======
echo "👥 Listar todos los usuarios"
curl -X GET "http://localhost:8000/listar_usuarios?admin_user=admin&admin_password=admin123"

# ====== Ejemplo: Usuario no existe ======
echo "❌ Intentar modificar usuario que NO EXISTE"
curl -X PUT "http://localhost:8000/modificar_usuario" ^
  -H "Content-Type: application/json" ^
  -d "{\"admin_user\":\"admin\",\"admin_password\":\"admin123\",\"username\":\"no_existe\",\"updates\":{\"puesto\":\"Test\"}}"
"""

print(curl_examples)

# ============================================================================
# 3. EJEMPLOS CON SWAGGER UI
# ============================================================================

print("""
╔══════════════════════════════════════════════════════════════════════════╗
║ EJEMPLO 3: USANDO SWAGGER UI (Navegador)                                ║
╚══════════════════════════════════════════════════════════════════════════╝

1. Levanta el servidor:
   uvicorn main:app --reload

2. Abre en tu navegador:
   http://localhost:8000/docs

3. Busca los endpoints:
   ✏️ PUT /modificar_usuario
   🗑️ DELETE /baja_usuario
   👥 GET /listar_usuarios

4. Para cada endpoint:
   a) Haz clic en "Try it out"
   b) Completa los parámetros
   c) Haz clic en "Execute"

EJEMPLOS:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✏️ PUT /modificar_usuario
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Parámetros en BODY (JSON):
{
  "admin_user": "admin",
  "admin_password": "admin123",
  "username": "emilio",
  "updates": {
    "puesto": "Senior Analyst",
    "accesos": ["guru"]
  }
}

RespHttp 200 (Éxito):
{
  "message": "Usuario modificado exitosamente"
}

Respuesta HTTP 403 (Admin inválido):
{
  "detail": "Credenciales de administrador inválidas."
}

Respuesta HTTP 404 (Usuario no existe):
{
  "detail": "Usuario no encontrado."
}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🗑️ DELETE /baja_usuario
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Parámetros en QUERY:
- admin_user: admin
- admin_password: admin123
- username: emilio

Respuesta HTTP 200 (Éxito):
{
  "message": "Usuario eliminado exitosamente"
}

Respuesta HTTP 403 (Admin inválido):
{
  "detail": "Credenciales de administrador inválidas."
}

Respuesta HTTP 404 (Usuario no existe):
{
  "detail": "Usuario no encontrado."
}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👥 GET /listar_usuarios
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Parámetros en QUERY:
- admin_user: admin
- admin_password: admin123

Respuesta HTTP 200 (Éxito):
{
  "usuarios": [
    {
      "username": "admin",
      "rol": "admin",
      "correo": "admin@ai360.com",
      "empresa": "AI360",
      "puesto": "Administrador"
    },
    {
      "username": "emilio",
      "rol": "user",
      "correo": "emilio@empresa.com"
    }
  ]
}

Respuesta HTTP 403 (Admin inválido):
{
  "detail": "Credenciales de administrador inválidas."
}
""")

# ============================================================================
# 4. RESUMEN DE CAMBIOS
# ============================================================================

print("""
╔══════════════════════════════════════════════════════════════════════════╗
║ RESUMEN DE CAMBIOS                                                       ║
╚══════════════════════════════════════════════════════════════════════════╝

✅ ANTES (❌ No funcionaba):
   - Siempre retornaba "Solo los administradores pueden realizar esta acción"
   - La validación no usaba la función reutilizable
   - Códigos HTTP inconsistentes

✅ AHORA (✅ Funciona correctamente):
   - Función validar_administrador() en services/usuario_service.py
   - Verifica: usuario existe + contraseña correcta + rol = admin
   - HTTP 403: Credenciales de admin inválidas
   - HTTP 404: Usuario objetivo no existe
   - HTTP 200: Operación exitosa
   - Los endpoints usan la nueva función reutilizable
   - Comentarios claros en el código

✅ CREDENCIALES POR DEFECTO:
   usuario: admin
   contraseña: admin123

✅ TODO PROBADO:
   - Script verificar_validacion_admin.py al 100%
   - 9 pruebas unitarias pasadas

""")

# ============================================================================
# 5. CASOS DE USO
# ============================================================================

print("""
╔══════════════════════════════════════════════════════════════════════════╗
║ CASOS DE USO - EJEMPLOS REALES                                          ║
╚══════════════════════════════════════════════════════════════════════════╝

CASO 1: Un admin quiere cambiar el rol de un usuario
────────────────────────────────────────────────────
Request:
  PUT /modificar_usuario
  
Body:
{
  "admin_user": "admin",
  "admin_password": "admin123",
  "username": "emilio",
  "updates": {
    "rol": "admin",
    "puesto": "Administrador"
  }
}

Response (HTTP 200):
{
  "message": "Usuario modificado exitosamente"
}


CASO 2: Alguien intenta eliminar un usuario pero usa mala contraseña
──────────────────────────────────────────────────────────────────────
Request:
  DELETE /baja_usuario?admin_user=admin&admin_password=wrongpass&username=juan

Response (HTTP 403):
{
  "detail": "Credenciales de administrador inválidas."
}

→ El sistema detecta que la contraseña es incorrecta y rechaza la solicitud


CASO 3: Un admin intenta modificar un usuario que no existe
────────────────────────────────────────────────────────────
Request:
  PUT /modificar_usuario
  
Body:
{
  "admin_user": "admin",
  "admin_password": "admin123",
  "username": "usuario_inexistente",
  "updates": {"puesto": "Test"}
}

Response (HTTP 404):
{
  "detail": "Usuario no encontrado."
}

→ El sistema valida que el admin sea correcto (✅)
  pero después busca el usuario objetivo y lo encuentra vacío (❌)


CASO 4: Un usuario normal intenta eliminar a otro
──────────────────────────────────────────────────
Request:
  DELETE /baja_usuario?admin_user=emilio&admin_password=prueba123&username=juan

Response (HTTP 403):
{
  "detail": "Credenciales de administrador inválidas."
}

→ El sistema verifica que usuario "emilio" existe y contraseña es correcta
  PERO su rol es "user", no "admin", así que lo rechaza


CASO 5: Admin lista todos los usuarios y obtiene los datos
──────────────────────────────────────────────────────────
Request:
  GET /listar_usuarios?admin_user=admin&admin_password=admin123

Response (HTTP 200):
{
  "usuarios": [
    {
      "username": "admin",
      "rol": "admin",
      "correo": "admin@ai360.com",
      "empresa": "AI360",
      "puesto": "Administrador",
      "accesos": ["guru", "tablero_movilidad"],
      "suscripcion": "enterprise"
    },
    {
      "username": "emilio",
      "rol": "user",
      "correo": "emilio@empresa.com",
      "empresa": "EmpresaX",
      "puesto": "Analista",
      "accesos": ["guru"],
      "suscripcion": "basic"
    }
  ]
}

→ Nota: Las contraseñas (password_hash) NO se muestran por seguridad

""")
