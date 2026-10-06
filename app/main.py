"""Application entry point.

Run locally with:
    uv run uvicorn app.main:app --reload
"""

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, EmailStr
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import User

app = FastAPI(
    title="Splitwiser API",
    description="Expense sharing backend",
    version="0.1.0",
)


class UserCreate(BaseModel):
    """What the API accepts. Validates the incoming request."""

    name: str
    email: EmailStr


class UserResponse(BaseModel):
    """What the API returns. `from_attributes` lets this read a
    SQLAlchemy User object directly, instead of us building a dict."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr


Base.metadata.create_all(bind=engine)


@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    result = db.execute(
        select(User).where(User.email == user.email)
    )

    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Email already registered"
        )

    new_user = User(
        name=user.name,
        email=user.email
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@app.get("/users", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)):
    result = db.execute(select(User))

    return result.scalars().all()


@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    result = db.execute(
        select(User).where(User.id == user_id)
    )

    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user
