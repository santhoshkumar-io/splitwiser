"""Application entry point.

Run locally with:
    uv run uvicorn app.main:app --reload
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr

app = FastAPI(
    title="Splitwiser API",
    description="Expense sharing backend",
    version="0.1.0",
)

class UserCreate(BaseModel):
    name:str
    email: EmailStr

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
users={}
next_user_id = 1

@app.post("/create-user", response_model=UserResponse, status_code=201)
def create_user(user:UserCreate):
    global next_user_id 
    if email_exists(user.email):
        raise HTTPException(
            status_code= 409,
            detail= "Email Already Registered!"
        )
    new_user = {
        "id": next_user_id,
        "name": user.name,
        "email": user.email,
    }

    users[next_user_id] = new_user
    next_user_id+=1
    return new_user


@app.get("/users", response_model=list[UserResponse])
def get_users():
    return list(users.values())

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id :int):
    if user_id not in users:
        raise HTTPException(
            status_code=404,
            detail="User not Found!"
        )
    return users[user_id]

def email_exists(email:str)->bool:
    for user in users.values():
        if user["email"] == email:
            return True
    return False