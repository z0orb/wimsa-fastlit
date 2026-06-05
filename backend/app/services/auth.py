from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate


class AuthService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def register(self, data: UserCreate) -> User:
        existing = self.repo.get_by_username(data.username)
        if existing:
            raise ValueError("Username already taken")
        existing_email = self.repo.get_by_email(data.email)
        if existing_email:
            raise ValueError("Email already registered")
        return self.repo.create(
            username=data.username,
            email=data.email,
            hashed_password=hash_password(data.password),
            role=data.role,
        )

    def authenticate(self, username: str, password: str) -> User:
        user = self.repo.get_by_username(username)
        if not user or not verify_password(password, user.hashed_password):
            raise ValueError("Invalid credentials")
        if not user.is_active:
            raise ValueError("Account is disabled")
        return user

    def login(self, username: str, password: str) -> str:
        user = self.authenticate(username, password)
        return create_access_token(
            {"sub": str(user.id), "role": user.role, "username": user.username}
        )
