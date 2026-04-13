# 🔐 Validación de Administrador - Guía Completa

## ¿Qué se cambió?

Se corrigió la validación de administrador en **TODOS** los endpoints que requieren permisos de admin. Ahora existe una **función reutilizable** que valida correctamente las credenciales del administrador.

---

## 1️⃣ Nueva Función Reutilizable

### Ubicación
**Archivo:** `services/usuario_service.py`
**Función:** `validar_administrador(admin_user, admin_password)`

### Código
```python
def validar_administrador(self, admin_user: str, admin_password: str) -> bool:
    """
    Valida que las credenciales correspondan a un administrador válido.
    
    Validaciones realizadas:
        - Verifica que el usuario exista en el sistema
        - Verifica que la contraseña sea correcta (usando hash SHA-256)
        - Verifica que el rol del usuario sea "admin"
    
    Args:
        admin_user (str): Nombre de usuario administrador
        admin_password (str): Contraseña en texto plano
    
    Returns:
        bool: True si es admin válido, False en cualquier otro caso
    """
```

### ¿Por qué es reutilizable?
- ✅ Sin efectos secundarios (solo verifica, no modifica datos)
- ✅ Devuelve un valor booleano simple (True/False)
- ✅ Se puede usar en cualquier endpoint que requiera admin
- ✅ Comentarios claros explicando cada paso

---

## 2️⃣ Endpoints Actualizados

### Endpoints que usan validación de admin:

#### 1. **DELETE /baja_usuario** (Eliminar usuario)
- **Parámetros de QUERY:**
  - `admin_user`: Nombre del administrador
  - `admin_password`: Contraseña del administrador  
  - `username`: Usuario a eliminar

- **Ejemplos de respuesta:**
  ```
  ✅ HTTP 200 (Éxito):
  {"message": "Usuario eliminado exitosamente"}
  
  ❌ HTTP 403 (Admin inválido):
  {"detail": "Credenciales de administrador inválidas."}
  
  ❌ HTTP 404 (Usuario no existe):
  {"detail": "Usuario no encontrado."}
  ```

- **Ejemplo en Swagger UI:**
  ```
  /baja_usuario?admin_user=admin&admin_password=admin123&username=emilio
  ```

### 2. **PUT /modificar_usuario** (Modificar usuario)
- **Parámetros en BODY (JSON):**
  ```json
  {
    "admin_user": "admin",
    "admin_password": "admin123",
    "username": "emilio",
    "updates": {
      "puesto": "Analista Senior",
      "accesos": ["guru", "tablero_movilidad"]
    }
  }
  ```

- **Ejemplos de respuesta:**
  ```
  ✅ HTTP 200 (Éxito):
  {"message": "Usuario modificado exitosamente"}
  
  ❌ HTTP 403 (Admin inválido):
  {"detail": "Credenciales de administrador inválidas."}
  
  ❌ HTTP 404 (Usuario no existe):
  {"detail": "Usuario no encontrado."}
  ```

### 3. **GET /listar_usuarios** (Listar todos los usuarios)
- **Parámetros de QUERY:**
  - `admin_user`: Nombre del administrador
  - `admin_password`: Contraseña del administrador

- **Ejemplos de respuesta:**
  ```
  ✅ HTTP 200 (Éxito):
  {
    "usuarios": [
      {
        "username": "admin",
        "rol": "admin",
        "correo": "admin@ai360.com",
        "empresa": "AI360"
      },
      {
        "username": "emilio",
        "rol": "user",
        "correo": "emilio@empresa.com"
      }
    ]
  }
  
  ❌ HTTP 403 (Admin inválido):
  {"detail": "Credenciales de administrador inválidas."}
  ```

- **Ejemplo en Swagger UI:**
  ```
  /listar_usuarios?admin_user=admin&admin_password=admin123
  ```

---

## 3️⃣ Credenciales por Defecto

El sistema crea automáticamente un administrador por defecto al iniciar:

```
Usuario: admin
Contraseña: admin123
Rol: admin
```

---

## 4️⃣ Flujo de Validación

```
┌─────────────────────────────────────────┐
│ Cliente envía request con:              │
│ - admin_user = "admin"                  │
│ - admin_password = "admin123"           │
│ - username = "emilio" (usuario objetivo)│
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│ validar_administrador(admin_user,       │
│                       admin_password)   │
└──────────────────┬──────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
        ▼                     ▼
    ✅ VÁLIDO            ❌ INVÁLIDO
    (rol = admin)       (credenciales mal,
                         usuario no es admin,
                         usuario no existe)
        │                     │
        ▼                     ▼
    Continuar con       Lanzar exception
    la operación        PermissionError
        │                     │
        ▼                     ▼
    Buscar usuario      Endpoint retorna
    objetivo y          HTTP 403 + mensaje
    ejecutar acción
        │
    ┌───┴────┐
    │         │
    ▼         ▼
✅ Existe  ❌ No existe
    │         │
    ▼         ▼
Ejecutar  Lanzar exception
acción    ValueError
    │         │
    ▼         ▼
HTTP 200  HTTP 404
```

---

## 5️⃣ Manejo de Excepciones

### En el Servicio (usuario_service.py)

```python
# Validar credenciales del administrador
if not self.validar_administrador(admin_user, admin_password):
    raise PermissionError("Credenciales de administrador inválidas.")

# Buscar y operar sobre usuario objetivo
# Si no existe:
raise ValueError("Usuario no encontrado.")
```

### En el Endpoint (main.py)

```python
try:
    usuario_service.baja_usuario(admin_user, admin_password, username)
    return {"message": "Usuario eliminado exitosamente"}
except PermissionError as e:
    # Credenciales de admin inválidas → HTTP 403
    raise HTTPException(status_code=403, detail=str(e))
except ValueError as e:
    # Usuario objetivo no existe → HTTP 404
    raise HTTPException(status_code=404, detail=str(e))
```

---

## 6️⃣ Códigos HTTP Utilizados

| Código | Significado | Cuándo ocurre |
|--------|-------------|---------------|
| **200** | ✅ Éxito | Operación completada correctamente |
| **403** | ❌ Prohibido | Credenciales de admin inválidas |
| **404** | ❌ No encontrado | El usuario objetivo no existe |
| **400** | ❌ Solicitud incorrecta | Otros errores de validación |

---

## 7️⃣ Comentarios en el Código

Todos los endpoints incluyen comentarios explicativos:

```python
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
```

---

## 8️⃣ Estructura del Proyecto Mantenida

```
main.py                          ← Endpoints (sin cambios en estructura)
models/
  └── usuario.py                 ← Modelo Usuario (sin cambios)
services/
  ├── usuario_service.py         ← ✅ ACTUALIZADO: Función validar_administrador + mejoras
  └── storage_service.py         ← ✅ ACTUALIZADO: Soporte para archivos locales
utils/
  └── security.py                ← Hash de contraseñas SHA-256 (sin cambios)
registros/
  └── usuarios.json              ← Almacenamiento local de usuarios
```

---

## 9️⃣ Mejoras en el Almacenamiento

El `StorageService` ahora soporta:

- ✅ Archivos locales en carpeta `registros/` (para desarrollo)
- ✅ Preparado para GCS en producción (solo descomenta líneas)
- ✅ Crea automáticamente la carpeta `registros/` si no existe
- ✅ Manejo de errores en lectura/escritura

---

## 🔟 Script de Verificación

Se incluye un script `verificar_validacion_admin.py` que prueba todas las validaciones:

```bash
python verificar_validacion_admin.py
```

**Pruebas incluidas:**
- ✅ Credenciales admin correctas
- ✅ Contraseña admin incorrecta
- ✅ Usuario normal (no admin)
- ✅ Usuario inexistente
- ✅ Modificar con admin válido
- ✅ Modificar con admin inválido
- ✅ Modificar usuario inexistente
- ✅ Listar con admin válido
- ✅ Listar con admin inválido

---

## 📋 Checklist de Cumplimiento

- ✅ Función reutilizable en services
- ✅ Verifica usuario exista
- ✅ Verifica contraseña correcta (usando hashing)
- ✅ Verifica rol = "admin"
- ✅ Reutilizada en ALL endpoints de admin
- ✅ HTTP 403 si admin inválido
- ✅ HTTP 404 si usuario objetivo no existe
- ✅ HTTP 200 si éxito
- ✅ Comentarios explicativos en el código
- ✅ Estructura del proyecto mantenida
- ✅ Fácil de entender para alguien en formación

---

## 🎓 Para Alguien en Formación

### Concepto Clave: DRY (Don't Repeat Yourself)

Antes teníamos el código de validación de admin duplicado en varias funciones:
```python
# ❌ ANTES: Repetido en cada función
estatus, rol = self.verificar_usuario(admin_user, admin_password)
if not estatus or rol != "admin":
    raise PermissionError(...)
```

Ahora lo centralizamos en una función:
```python
# ✅ AHORA: Reutilizable
if not self.validar_administrador(admin_user, admin_password):
    raise PermissionError(...)
```

**Ventajas:**
1. Código más limpio y legible
2. Si cambias la lógica de validación, cambias en UN solo lugar
3. Menos probabilidad de errores
4. Fácil de testear
5. Sigue el principio de Single Responsibility

---

## 🚀 Próximos Pasos (Opcional)

Para hacer el sistema aún más robusto:

1. **Agregar intentos fallidos**: Bloquear después de N intentos fallidos
2. **Tokens JWT**: En lugar de enviar credenciales en cada request
3. **Auditoría**: Registrar quién hizo qué y cuándo
4. **Rate limiting**: Limitar solicitudes por IP
5. **TLS/SSL**: Encriptar comunicación entre cliente y servidor

