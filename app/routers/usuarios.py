"""
Router de Usuarios.
Endpoints para gestionar usuarios en la plataforma.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

from app.database import get_session
from app.models import Usuario, Favorito, Pelicula
from app.schemas import (
    UsuarioCreate,
    UsuarioRead,
    UsuarioUpdate,
    UsuarioWithFavoritos,
    PeliculaRead
)

# Crear el router con prefijo y tags

router = APIRouter(
    prefix="/api/usuarios",
    tags=["Usuarios"]
)


# Endpoint para listar todos los usuarios

@router.get("/", response_model=List[UsuarioRead])
def listar_usuarios(
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100
):
    statement = select(Usuario).offset(skip).limit(limit)
    usuarios = session.exec(statement).all()

    return usuarios
    
    # Consultar todos los usuarios con paginación



#  Endpoint para crear un nuevo usuario
@router.post("/", response_model=UsuarioRead, status_code=status.HTTP_201_CREATED)
def crear_usuario(
    usuario: UsuarioCreate,
    session: Session = Depends(get_session)
):
    
    statement = select(Usuario).where(Usuario.correo == usuario.correo)
    existing_user = session.exec(statement).first()


    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya está registrado"
        )

    
# Crear el nuevo usuario

    db_usuario = Usuario.model_validate(usuario)
    session.add(db_usuario)
    session.commit()
    session.refresh(db_usuario)
    return db_usuario

# Endpoint para obtener un usuario por ID

@router.get("/{usuario_id}", response_model=UsuarioRead)
def obtener_usuario(
    usuario_id: int,
    session: Session = Depends(get_session)
):
    
# Buscar el usuario por ID

    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El usuario no existe"
        )
    
    return usuario


# Endpoint para actualizar un usuario
@router.put("/{usuario_id}", response_model=UsuarioRead)
def actualizar_usuario(
    usuario_id: int,
    usuario_update: UsuarioUpdate,
    session: Session = Depends(get_session)
):
    
# Buscar el usuario

    db_usuario = session.get(Usuario, usuario_id)
    if not db_usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El usuario aun no existe"
        )
    
#  Si se actualiza el correo, verificar que no exista
    
#  Actualizar solo los campos proporcionados
    usuario_data = usuario_data.model_dump(exclude_unset=True)
    for key, value in usuario_data.items():
        setattr(db_usuario, key, value)
        
    session.add(db_usuario)
    session.commit()
    session.refresh(db_usuario)
    
    return db_usuario


# Endpoint para eliminar un usuario
@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_usuario(
    usuario_id: int,
    session: Session = Depends(get_session)
):
    
# Buscar el usuario

    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con id {usuario_id} no encontrado"
        )
    
    # Eliminar el usuario (los favoritos se eliminan por CASCADE)
    session.delete(usuario)
    session.commit()
    return None


# Endpoint para obtener los favoritos de un usuario

@router.get("/{usuario_id}/favoritos", response_model=List[PeliculaRead])
def listar_favoritos_usuario(
    usuario_id: int,
    session: Session = Depends(get_session)
):
    
    #  Verificar que el usuario existe

    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El usuario no existe"
        )
    
    #  Obtener las películas favoritas del usuario

    statement = select(Favorito).where(Favorito.id_usuario == usuario_id)
    favoritos = session.exec(statement).all()
    
    return favoritos


# Endpoint para marcar una película como favorita

@router.post(
    "/{usuario_id}/favoritos/{pelicula_id}",
    status_code=status.HTTP_201_CREATED
)
def marcar_favorito(
    usuario_id: int,
    pelicula_id: int,
    session: Session = Depends(get_session)
):
    
    # Verificar que el usuario existe

    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con id {usuario_id} no encontrado"
        )
    
    # Verificar que la película existe

    pelicula = session.get(Pelicula, pelicula_id)
    if not pelicula:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Película con id {pelicula_id} no encontrada"
        )
   
    # Verificar si ya existe el favorito

    statement = select(Favorito).where(
        Favorito.id_usuario == usuario_id,
        Favorito.id_pelicula == pelicula_id
    )
    existing_favorito = session.exec(statement).first()
    if existing_favorito:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La película ya está marcada como favorita"
        )
    
    #  Crear el favorito

    favorito = Favorito(id_usuario=usuario_id, id_pelicula=pelicula_id)
    session.add(favorito)
    session.commit()
    session.refresh(favorito)
    
    return {"message": "Película marcada como favorita exitosamente"}


# Endpoint para eliminar una película de favoritos
@router.delete(
    "/{usuario_id}/favoritos/{pelicula_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def eliminar_favorito(
    usuario_id: int,
    pelicula_id: int,
    session: Session = Depends(get_session)
):
    
    #  Buscar el favorito

    statement = select(Favorito).where(
        Favorito.id_usuario == usuario_id,
        Favorito.id_pelicula == pelicula_id
    )

    favorito = session.exec(statement).first()

    if not favorito:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El favorito no existe"
        )
    
    # Eliminar el favorito

    session.delete(favorito)
    session.commit()

    return None


#  Opcional - Endpoint para estadísticas del usuario

@router.get("/{usuario_id}/estadisticas")
def obtener_estadisticas_usuario(
    usuario_id: int,
    session: Session = Depends(get_session)
):
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con id {usuario_id} no encontrado"
        )
    
    statement = select(Favorito).where(Favorito.id_usuario == usuario_id)
    favoritos = session.exec(statement).all()
    total_favoritos = len(favoritos)
    
    tiempo_total = sum([f.pelicula.duracion for f in favoritos if f.pelicula and f.pelicula.duracion])
    
    return {
        "usuario_id": usuario_id,
        "nombre_usuario": usuario.nombre,
        "total_favoritos": total_favoritos,
        "tiempo_total_minutos": tiempo_total
    }

