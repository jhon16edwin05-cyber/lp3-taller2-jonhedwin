from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import create_db_and_tables
from app.routers import usuarios, peliculas, favoritos

#  Importar la configuración desde app.config


@asynccontextmanager
async def lifespan(app: FastAPI):
    
    # Startup: Crear tablas en la base de datos

    create_db_and_tables()
    yield
    
    # Shutdown: Limpiar recursos si es necesario

    print("cerrando aplicación...")


#  Crear la instancia de FastAPI con metadatos apropiados
# Incluir: title, description, version, contact, license_info

app = FastAPI(
    title="API de Películas",
    description="API RESTful para gestionar usuarios, películas y favoritos",
    version="1.0.0",
    lifespan=lifespan,

    #  Agregar información de contacto y licencia

     contact={
         "name": "Tu Nombre",
         "email": "tu.email@example.com",
     },
     license_info={
         "name": "MIT",
     },
)


# Configurar CORS para permitir solicitudes desde diferentes orígenes
# Esto es importante para desarrollo con frontend separado

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  #  En producción, especificar orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Incluir los routers de usuarios, peliculas y favoritos
# Ejemplo:

app.include_router(usuarios.router, tags=["Usuarios"])
app.include_router(peliculas.router, tags=["Películas"])
app.include_router(favoritos.router, tags=["Favoritos"])


# Crear un endpoint raíz que retorne información básica de la API

@app.get("/", tags=["Root"])
async def root():
    
    return {
        "nombre_app": "API de Películas y Favoritos",
        "version": "1.0.0",
        "descripcion": "API desarrollada con FastAPI y SQLModel para el Taller 2 de LP3",
        "documentacion": "/docs",
        "redoc": "/redoc",
        "estado": "En línea"
    }


# Crear un endpoint de health check para monitoreo

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint para verificar el estado de la API."""
    return {
        "status": "healthy",
        "database": "ok",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

