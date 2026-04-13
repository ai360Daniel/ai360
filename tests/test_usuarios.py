def test_modificar_usuario_success(client):
    response = client.put("/modificar_usuario", json={
        "admin_user": "admin",
        "admin_password": "123456",
        "username": "emilio",
        "updates": {
            "puesto": "Analista",
            "accesos": ["guru"]
        }
    })
    assert response.status_code == 200
    assert response.json() == {"message": "Usuario modificado exitosamente"}

def test_modificar_usuario_no_admin(client):
    response = client.put("/modificar_usuario", json={
        "admin_user": "user",
        "admin_password": "password",
        "username": "emilio",
        "updates": {
            "puesto": "Analista",
            "accesos": ["guru"]
        }
    })
    assert response.status_code == 403
    assert response.json() == {"detail": "Solo los administradores pueden modificar usuarios."}