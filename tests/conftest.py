import pytest

@pytest.fixture
def admin_user():
    return {
        "admin_user": "admin",
        "admin_password": "123456"
    }

@pytest.fixture
def user_data():
    return {
        "username": "emilio",
        "updates": {
            "puesto": "Analista",
            "accesos": ["guru"]
        }
    }