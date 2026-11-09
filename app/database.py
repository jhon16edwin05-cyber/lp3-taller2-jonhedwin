"""
Configuración de la base de datos y gestión de sesiones.
Utiliza SQLModel para ORM y gestión de conexiones.
"""

from collections.abc import Generator

from sqlalchemy import text
from sqlmodel import Session, SQLModel, create_engine, select

from app.config import settings


# Crear el engine de la base de datos
# El engine es la conexión principal a la base de datos
# connect_args es específico para SQLite, remover para otras bases de datos
connect_args = {"check_same_thread": False} if "sqlite" in settings.database_url else {}

engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    connect_args=connect_args,
)


# Función para crear todas las tablas

def create_db_and_tables():
    """
    Crea todas las tablas en la base de datos.
    Se llama al iniciar la aplicación.
    """
    # Importar todos los modelos antes de crear las tablas
    from app.models import Favorito, Pelicula, Usuario  # noqa: F401

    SQLModel.metadata.create_all(engine)
    print("Tablas de la base de datos creadas correctamente")


# Función para eliminar todas las tablas (útil para testing)

def drop_db_and_tables():
    """
    Elimina todas las tablas de la base de datos.
    Usar con precaución - elimina todos los datos.
    """
    SQLModel.metadata.drop_all(engine)
    print("Tablas de la base de datos eliminadas")


# Obtener una sesión de base de datos

def get_session() -> Generator[Session, None, None]:
    """
    Generador de sesiones de base de datos.
    Se usa como dependencia en los endpoints de FastAPI.

    Uso en endpoints:
        @app.get("/items")
        def read_items(session: Session = Depends(get_session)):
            items = session.exec(select(Item)).all()
            return items
    """
    with Session(engine) as session:
        yield session


# Opcional - Función para verificar la conexión a la base de datos

def check_database_connection() -> bool:
    """
    Verifica que la conexión a la base de datos funcione correctamente.
    Retorna True si la conexión es exitosa, False en caso contrario.
    """
    try:
        with Session(engine) as session:
            session.exec(text("SELECT 1"))
            return True
    except Exception as exc:
        print(f"Error al conectar con la base de datos: {exc}")
        return False


# Context manager para transacciones
class DatabaseSession:
    def __enter__(self) -> Session:
        self.session = Session(engine)
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.session.rollback()
        self.session.close()


# Opcional - Función para inicializar datos de prueba

def init_sample_data():
    """
    Inicializa la base de datos con datos de prueba.
    Útil para desarrollo y testing.
    """
    from app.models import Pelicula, Usuario

    with Session(engine) as session:
        if not session.exec(select(Usuario)).first():
            usuarios = [
                Usuario(nombre="Ana López", correo="ana@correo.com"),
                Usuario(nombre="Luis Pérez", correo="luis@correo.com"),
            ]
            session.add_all(usuarios)
            session.commit()

        if not session.exec(select(Pelicula)).first():
            peliculas = [
                Pelicula(
                    titulo="Inception",
                    director="Christopher Nolan",
                    genero="Ciencia ficción",
                    duracion=148,
                    año=2010,
                    clasificacion="PG-13",
                    sinopsis="Un ladrón que roba secretos del subconsciente.",
                ),
                Pelicula(
                    titulo="The Matrix",
                    director="Lana y Lilly Wachowski",
                    genero="Acción",
                    duracion=136,
                    año=1999,
                    clasificacion="R",
                    sinopsis="Un hacker descubre la verdad sobre la realidad.",
                ),
            ]
            session.add_all(peliculas)
            session.commit()
