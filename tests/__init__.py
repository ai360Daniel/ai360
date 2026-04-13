def pytest_configure():
    import pytest
    from your_application import create_admin_user

    create_admin_user("admin", "123456")