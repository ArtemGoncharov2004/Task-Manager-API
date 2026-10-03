from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.user import UserCreate


def register_user(db: Session, data: UserCreate) -> User:
    existing = db.query(User).filter(User.email == data.email).first()
    if existing is not None:
        raise ConflictError(f"User with email '{data.email}' already exists")

    user = User(email=data.email, hashed_password=hash_password(data.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User:
    user = db.query(User).filter(User.email == email).first()
    if user is None or not verify_password(password, user.hashed_password):
        raise UnauthorizedError("Invalid email or password")
    return user


def login(db: Session, email: str, password: str) -> str:
    user = authenticate_user(db, email, password)
    return create_access_token({"sub": str(user.id)})
