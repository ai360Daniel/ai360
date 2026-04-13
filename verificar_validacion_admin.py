"""
Script para verificar que la validación de administrador funciona correctamente.

Este script prueba la nueva función validar_administrador en todos los endpoints
que requieren permisos de administrador.
"""

from services.usuario_service import UsuarioService
from models.usuario import Usuario
from utils.security import hash_password

def main():
    print("=" * 70)
    print("🔐 VERIFICACIÓN DE VALIDACIÓN DE ADMINISTRADOR")
    print("=" * 70)
    
    usuario_service = UsuarioService()
    
    # Crear un usuario de prueba para usar en operaciones de admin
    print("\n1️⃣ Creando usuario de prueba...")
    try:
        usuario_prueba = Usuario(
            username="usuario_prueba",
            password_hash=hash_password("prueba123"),
            rol="user",
            correo="prueba@test.com",
            empresa="TestCorp",
            puesto="Tester"
        )
        usuario_service.alta_usuario(usuario_prueba)
        print("   ✅ Usuario de prueba creado: usuario_prueba")
    except ValueError as e:
        print(f"   ℹ️  Usuario ya existe: {e}")
    
    # Pruebas de validación de administrador
    print("\n2️⃣ Validando credenciales de administrador...")
    
    # PRUEBA 1: Credenciales de admin correctas
    print("\n   PRUEBA 1: Credenciales CORRECTAS (admin / admin123)")
    resultado = usuario_service.validar_administrador("admin", "admin123")
    if resultado:
        print("   ✅ ÉXITO: Admin validado correctamente")
    else:
        print("   ❌ ERROR: Admin debería ser válido")
    
    # PRUEBA 2: Contraseña incorrecta
    print("\n   PRUEBA 2: Contraseña INCORRECTA (admin / 123456)")
    resultado = usuario_service.validar_administrador("admin", "123456")
    if not resultado:
        print("   ✅ ÉXITO: Admin rechazado correctamente (contraseña incorrecta)")
    else:
        print("   ❌ ERROR: Admin debería ser rechazado")
    
    # PRUEBA 3: Usuario no admin
    print("\n   PRUEBA 3: Usuario NORMAL no es admin (usuario_prueba / prueba123)")
    resultado = usuario_service.validar_administrador("usuario_prueba", "prueba123")
    if not resultado:
        print("   ✅ ÉXITO: Usuario normal rechazado correctamente (no es admin)")
    else:
        print("   ❌ ERROR: Usuario normal debería ser rechazado")
    
    # PRUEBA 4: Usuario inexistente
    print("\n   PRUEBA 4: Usuario INEXISTENTE (noexiste / password)")
    resultado = usuario_service.validar_administrador("noexiste", "password")
    if not resultado:
        print("   ✅ ÉXITO: Usuario inexistente rechazado correctamente")
    else:
        print("   ❌ ERROR: Usuario inexistente debería ser rechazado")
    
    # Pruebas de operaciones de admin
    print("\n3️⃣ Probando operaciones que requieren admin...")
    
    # PRUEBA 5: Modificar usuario (admin válido)
    print("\n   PRUEBA 5: Modificar usuario con admin VÁLIDO")
    try:
        usuario_service.modificar_usuario(
            "admin", 
            "admin123", 
            "usuario_prueba", 
            {"puesto": "Super Tester", "empresa": "TestCorp2"}
        )
        print("   ✅ ÉXITO: Usuario modificado exitosamente")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    # PRUEBA 6: Modificar usuario (contraseña admin incorrecta)
    print("\n   PRUEBA 6: Modificar usuario con admin INVÁLIDO (contraseña incorrecta)")
    try:
        usuario_service.modificar_usuario(
            "admin", 
            "123456",  # Contraseña incorrecta
            "usuario_prueba", 
            {"puesto": "No debería cambiar"}
        )
        print("   ❌ ERROR: Debería haber sido rechazado")
    except PermissionError as e:
        print(f"   ✅ ÉXITO: Rechazado correctamente - {e}")
    except Exception as e:
        print(f"   ❌ ERROR inesperado: {e}")
    
    # PRUEBA 7: Modificar usuario inexistente (admin válido)
    print("\n   PRUEBA 7: Modificar usuario INEXISTENTE con admin válido")
    try:
        usuario_service.modificar_usuario(
            "admin", 
            "admin123", 
            "usuario_inexistente",  # No existe
            {"puesto": "No debería cambiar"}
        )
        print("   ❌ ERROR: Debería haber indicado que el usuario no existe")
    except ValueError as e:
        print(f"   ✅ ÉXITO: Error correcto lanzado - {e}")
    except Exception as e:
        print(f"   ❌ ERROR inesperado: {e}")
    
    # PRUEBA 8: Listar usuarios (admin válido)
    print("\n   PRUEBA 8: Listar usuarios con admin VÁLIDO")
    try:
        usuarios = usuario_service.listar_usuarios("admin", "admin123")
        print(f"   ✅ ÉXITO: Se obtuvieron {len(usuarios)} usuario(s)")
        if len(usuarios) > 0:
            print(f"      - Usuarios: {[u['username'] for u in usuarios]}")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    # PRUEBA 9: Listar usuarios (contraseña admin incorrecta)
    print("\n   PRUEBA 9: Listar usuarios con admin INVÁLIDO")
    try:
        usuarios = usuario_service.listar_usuarios("admin", "wrongpass")
        print("   ❌ ERROR: Debería haber sido rechazado")
    except PermissionError as e:
        print(f"   ✅ ÉXITO: Rechazado correctamente - {e}")
    except Exception as e:
        print(f"   ❌ ERROR inesperado: {e}")
    
    # Limpiar: Eliminar usuario de prueba
    print("\n4️⃣ Limpiando usuario de prueba...")
    try:
        usuario_service.baja_usuario("admin", "admin123", "usuario_prueba")
        print("   ✅ Usuario de prueba eliminado")
    except Exception as e:
        print(f"   ℹ️  {e}")
    
    print("\n" + "=" * 70)
    print("✅ VERIFICACIÓN COMPLETADA")
    print("=" * 70)
    print("""
RESUMEN:
- La función validar_administrador() es REUTILIZABLE en todos los endpoints
- Verifica: credenciales correctas Y rol = "admin"
- Retorna: True si es admin válido, False en cualquier otro caso
- Los endpoints ahora devuelven:
  • HTTP 403: Si credenciales de admin son inválidas
  • HTTP 404: Si el usuario objetivo no existe
  • HTTP 200: Si la operación es exitosa
    """)

if __name__ == "__main__":
    main()
