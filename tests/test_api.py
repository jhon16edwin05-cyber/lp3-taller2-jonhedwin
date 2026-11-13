"""
Tests para la API de Películas.
Pruebas unitarias y de integración usando pytest.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from main import app
from app.database import get_session
from app.models import Usuario, Pelicula, Favorito


# =============================================================================
# CONFIGURACIÓN DE FIXTURES
# =============================================================================


@pytest.fixture(name="session")
def session_fixture():
    """Crea una sesión de base de datos en memoria para cada test."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Crea un cliente de pruebas de FastAPI con la sesión de test."""

    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="usuario_test")
def usuario_test_fixture(session: Session):
    """Crea un usuario de prueba en la base de datos."""
    usuario = Usuario(nombre="Usuario Test", correo="test@example.com")
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario


@pytest.fixture(name="pelicula_test")
def pelicula_test_fixture(session: Session):
    """Crea una película de prueba en la base de datos."""
    pelicula = Pelicula(
        titulo="Película Test",
        director="Director Test",
        genero="Drama",
        duracion=120,
        año=2020,
        clasificacion="PG-13",
        sinopsis="Una película de prueba",
    )
    session.add(pelicula)
    session.commit()
    session.refresh(pelicula)
    return pelicula


# =============================================================================
# TESTS DE USUARIOS
# =============================================================================


class TestUsuarios:
    """Tests para los endpoints de usuarios."""

    def test_listar_usuarios(self, client: TestClient):
        """Test para GET /api/usuarios"""
        response = client.get("/api/usuarios/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_crear_usuario(self, client: TestClient):
        """Test para POST /api/usuarios"""
        usuario_data = {"nombre": "Nuevo Usuario", "correo": "nuevo@example.com"}
        response = client.post("/api/usuarios/", json=usuario_data)
        assert response.status_code == 201
        data = response.json()
        assert data["nombre"] == usuario_data["nombre"]
        assert data["correo"] == usuario_data["correo"]
        assert "id" in data

    def test_crear_usuario_correo_duplicado(self, client: TestClient, usuario_test: Usuario):
        """Test para verificar que no se permiten correos duplicados"""
        usuario_data = {"nombre": "Otro Usuario", "correo": usuario_test.correo}
        response = client.post("/api/usuarios/", json=usuario_data)
        assert response.status_code == 400
        assert "correo" in response.json()["detail"].lower()

    def test_obtener_usuario(self, client: TestClient, usuario_test: Usuario):
        """Test para GET /api/usuarios/{id}"""
        response = client.get(f"/api/usuarios/{usuario_test.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == usuario_test.id
        assert data["nombre"] == usuario_test.nombre

    def test_obtener_usuario_no_existe(self, client: TestClient):
        """Test para verificar error 404 con usuario inexistente"""
        response = client.get("/api/usuarios/9999")
        assert response.status_code == 404

    def test_actualizar_usuario(self, client: TestClient, usuario_test: Usuario):
        """Test para PUT /api/usuarios/{id}"""
        update_data = {"nombre": "Nombre Actualizado"}
        response = client.put(f"/api/usuarios/{usuario_test.id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["nombre"] == update_data["nombre"]

    def test_eliminar_usuario(self, client: TestClient, usuario_test: Usuario):
        """Test para DELETE /api/usuarios/{id}"""
        response = client.delete(f"/api/usuarios/{usuario_test.id}")
        assert response.status_code == 204

        response = client.get(f"/api/usuarios/{usuario_test.id}")
        assert response.status_code == 404


# =============================================================================
# TESTS DE PELÍCULAS
# =============================================================================


class TestPeliculas:
    """Tests para los endpoints de películas."""

    def test_listar_peliculas(self, client: TestClient):
        """Test para GET /api/peliculas"""
        response = client.get("/api/peliculas/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_crear_pelicula(self, client: TestClient):
        """Test para POST /api/peliculas"""
        pelicula_data = {
            "titulo": "Nueva Película",
            "director": "Director Nuevo",
            "genero": "Acción",
            "duracion": 150,
            "año": 2023,
            "clasificacion": "PG-13",
            "sinopsis": "Una nueva película de prueba",
        }
        response = client.post("/api/peliculas/", json=pelicula_data)
        assert response.status_code == 201
        data = response.json()
        assert data["titulo"] == pelicula_data["titulo"]
        assert data["director"] == pelicula_data["director"]
        assert "id" in data

    def test_obtener_pelicula(self, client: TestClient, pelicula_test: Pelicula):
        """Test para GET /api/peliculas/{id}"""
        response = client.get(f"/api/peliculas/{pelicula_test.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == pelicula_test.id
        assert data["titulo"] == pelicula_test.titulo

    def test_actualizar_pelicula(self, client: TestClient, pelicula_test: Pelicula):
        """Test para PUT /api/peliculas/{id}"""
        update_data = {"titulo": "Título Actualizado"}
        response = client.put(f"/api/peliculas/{pelicula_test.id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["titulo"] == update_data["titulo"]

    def test_eliminar_pelicula(self, client: TestClient, pelicula_test: Pelicula):
        """Test para DELETE /api/peliculas/{id}"""
        response = client.delete(f"/api/peliculas/{pelicula_test.id}")
        assert response.status_code == 204

        response = client.get(f"/api/peliculas/{pelicula_test.id}")
        assert response.status_code == 404

    def test_buscar_peliculas(self, client: TestClient, pelicula_test: Pelicula):
        """Test para GET /api/peliculas/buscar"""
        response = client.get(f"/api/peliculas/buscar/?titulo={pelicula_test.titulo}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert data[0]["titulo"] == pelicula_test.titulo

    def test_buscar_peliculas_multiples_filtros(self, client: TestClient):
        """Test para búsqueda con múltiples parámetros"""
        pelicula_data = {
            "titulo": "Drama Clásico",
            "director": "Director Drama",
            "genero": "Drama",
            "duracion": 110,
            "año": 2021,
            "clasificacion": "PG",
            "sinopsis": "Película de drama",
        }
        response = client.post("/api/peliculas/", json=pelicula_data)
        assert response.status_code == 201

        response = client.get("/api/peliculas/buscar/?genero=Drama&año_min=2020")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert all(item["genero"].lower().find("drama") >= 0 for item in data)


# =============================================================================
# TESTS DE FAVORITOS
# =============================================================================


class TestFavoritos:
    """Tests para los endpoints de favoritos."""

    def test_listar_favoritos(self, client: TestClient):
        """Test para GET /api/favoritos"""
        response = client.get("/api/favoritos/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_crear_favorito(self, client: TestClient, usuario_test: Usuario, pelicula_test: Pelicula):
        """Test para POST /api/favoritos"""
        favorito_data = {
            "id_usuario": usuario_test.id,
            "id_pelicula": pelicula_test.id,
        }
        response = client.post("/api/favoritos/", json=favorito_data)
        assert response.status_code == 201
        data = response.json()
        assert data["id_usuario"] == usuario_test.id
        assert data["id_pelicula"] == pelicula_test.id

    def test_crear_favorito_duplicado(self, client: TestClient, usuario_test: Usuario, pelicula_test: Pelicula):
        """Test para verificar que no se permiten favoritos duplicados"""
        favorito_data = {
            "id_usuario": usuario_test.id,
            "id_pelicula": pelicula_test.id,
        }
        client.post("/api/favoritos/", json=favorito_data)
        response = client.post("/api/favoritos/", json=favorito_data)
        assert response.status_code == 400

    def test_eliminar_favorito(self, client: TestClient, session: Session, usuario_test: Usuario, pelicula_test: Pelicula):
        """Test para DELETE /api/favoritos/{id}"""
        favorito = Favorito(id_usuario=usuario_test.id, id_pelicula=pelicula_test.id)
        session.add(favorito)
        session.commit()
        session.refresh(favorito)

        response = client.delete(f"/api/favoritos/{favorito.id}")
        assert response.status_code == 204

    def test_marcar_favorito_usuario(self, client: TestClient, usuario_test: Usuario, pelicula_test: Pelicula):
        """Test para POST /api/usuarios/{id}/favoritos/{id_pelicula}"""
        response = client.post(f"/api/usuarios/{usuario_test.id}/favoritos/{pelicula_test.id}")
        assert response.status_code == 201

    def test_listar_favoritos_usuario(self, client: TestClient, session: Session, usuario_test: Usuario, pelicula_test: Pelicula):
        """Test para GET /api/usuarios/{id}/favoritos"""
        favorito = Favorito(id_usuario=usuario_test.id, id_pelicula=pelicula_test.id)
        session.add(favorito)
        session.commit()

        response = client.get(f"/api/usuarios/{usuario_test.id}/favoritos")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0


# =============================================================================
# TESTS DE INTEGRACIÓN
# =============================================================================


class TestIntegracion:
    """Tests de integración que prueban flujos completos."""

    def test_flujo_completo(self, client: TestClient):
        """Test que verifica el flujo completo de la aplicación"""
        usuario_data = {
            "nombre": "Usuario Integración",
            "correo": "integracion@example.com",
        }
        response_usuario = client.post("/api/usuarios/", json=usuario_data)
        assert response_usuario.status_code == 201
        usuario_id = response_usuario.json()["id"]

        pelicula_data = {
            "titulo": "Película Integración",
            "director": "Director Test",
            "genero": "Drama",
            "duracion": 120,
            "año": 2023,
            "clasificacion": "PG-13",
        }
        response_pelicula = client.post("/api/peliculas/", json=pelicula_data)
        assert response_pelicula.status_code == 201
        pelicula_id = response_pelicula.json()["id"]

        response_favorito = client.post(f"/api/usuarios/{usuario_id}/favoritos/{pelicula_id}")
        assert response_favorito.status_code == 201

        response_lista = client.get(f"/api/usuarios/{usuario_id}/favoritos")
        assert response_lista.status_code == 200
        favoritos = response_lista.json()
        assert len(favoritos) == 1
        assert favoritos[0]["id"] == pelicula_id


# =============================================================================
# TESTS DE VALIDACIÓN
# =============================================================================


class TestValidacion:
    """Tests para validaciones de datos."""

    def test_email_invalido(self, client: TestClient):
        """Test para verificar validación de email"""
        usuario_data = {"nombre": "Usuario Test", "correo": "email-invalido"}
        response = client.post("/api/usuarios/", json=usuario_data)
        assert response.status_code == 422

    def test_año_pelicula_invalido(self, client: TestClient):
        """Test para verificar validación de año"""
        pelicula_data = {
            "titulo": "Película Test",
            "director": "Director Test",
            "genero": "Drama",
            "duracion": 120,
            "año": 1800,
            "clasificacion": "PG-13",
        }
        response = client.post("/api/peliculas/", json=pelicula_data)
        assert response.status_code == 422

    def test_campos_requeridos(self, client: TestClient):
        """Test para verificar que los campos requeridos son obligatorios"""
        usuario_data = {"nombre": "Usuario Sin Email"}
        response = client.post("/api/usuarios/", json=usuario_data)
        assert response.status_code == 422
