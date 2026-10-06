Absolutely. Phase 3 is where Splitwiser starts becoming a real backend.

We're going to replace:

Python dictionary
        ↓
   temporary data

with:

FastAPI
   ↓
SQLAlchemy
   ↓
PostgreSQL
   ↓
Persistent data

And I'll keep the guidance high-detail for now.

Phase 3 — PostgreSQL + SQLAlchemy
What are we trying to solve?

Right now you have:

users = {}

Suppose you create:

Santhosh
Arun
Rahul

Your memory looks like:

users
│
├── 1 → Santhosh
├── 2 → Arun
└── 3 → Rahul

But then:

Stop FastAPI
     ↓
Start FastAPI
     ↓
users = {}

Everything is gone.

We need persistent storage.

That's the job of a database.

3.1 What is PostgreSQL?

Think of PostgreSQL as a program whose job is to:

store data
retrieve data
update data
delete data
enforce rules
handle multiple users simultaneously
maintain data consistency

Instead of:

users[1]

we'll eventually do something conceptually like:

SELECT *
FROM users
WHERE id = 1;

And instead of:

users[1] = new_user

we'll do:

INSERT INTO users (...)
VALUES (...);
3.2 First understand the database structure

Before installing anything, let's design our first table.

Our current user looks like:

User
├── id
├── name
└── email

A PostgreSQL table can look like:

users
┌────┬──────────┬─────────────────────────┐
│ id │ name     │ email                   │
├────┼──────────┼─────────────────────────┤
│ 1  │ Santhosh │ santhosh@example.com    │
│ 2  │ Arun     │ arun@example.com        │
│ 3  │ Rahul    │ rahul@example.com       │
└────┴──────────┴─────────────────────────┘

Each:

row = one user

and:

column = one property
3.3 What is a primary key?

Our:

id

should uniquely identify a user.

So:

id = 1

means exactly one user.

We call this the primary key.

Conceptually:

users

id ← PRIMARY KEY
│
├── 1
├── 2
└── 3

Two users can't have:

id = 1

This is enforced by PostgreSQL, not merely by our Python code.

3.4 What about email?

We previously implemented:

email_exists()

But here's something important.

Imagine two requests arrive at almost exactly the same time:

Request A → santhosh@example.com
Request B → santhosh@example.com

Both check:

Does email exist?
       ↓
      No

Then both insert.

You could accidentally get duplicates.

This is why business-critical constraints should also be enforced at the database level.

So our table should eventually have:

email UNIQUE

This is an important backend engineering lesson:

Application validation improves the user experience; database constraints protect the data.

3.5 Install PostgreSQL

You have two reasonable choices:

Option A — Install PostgreSQL directly
Option B — Run PostgreSQL using Docker

For this project, I recommend Docker.

It keeps your development environment clean and will also help you later when we containerize Splitwiser.

If Docker is already installed on your machine, check:

docker --version

Then:

docker ps

If Docker isn't installed/running, tell me before continuing and we'll handle that separately.

3.6 Start PostgreSQL with Docker

From your Splitwiser project:

docker run --name splitwiser-postgres \
  -e POSTGRES_USER=splitwiser \
  -e POSTGRES_PASSWORD=splitwiser \
  -e POSTGRES_DB=splitwiser \
  -p 5432:5432 \
  -d postgres

This command looks scary, so let's break it down.

docker run

Create and start a container.

--name splitwiser-postgres

Give the container a name.

POSTGRES_USER=splitwiser

Database username.

POSTGRES_PASSWORD=splitwiser

Database password.

POSTGRES_DB=splitwiser

Create a database called splitwiser.

-p 5432:5432

Connect your computer's port 5432 to PostgreSQL's port 5432.

-d postgres

Run the PostgreSQL image in the background.

3.7 Check that PostgreSQL is running

Run:

docker ps

You should see something similar to:

CONTAINER ID   IMAGE      PORTS
abc123         postgres   0.0.0.0:5432->5432/tcp

Now you have:

Your Mac
   │
   │ localhost:5432
   ▼
Docker
   │
   ▼
PostgreSQL
   │
   ▼
splitwiser database
3.8 Understand the connection URL

Our application needs to know how to connect to PostgreSQL.

The connection information is:

postgresql://splitwiser:splitwiser@localhost:5432/splitwiser

Break it apart:

postgresql://
       │
       ├── username: splitwiser
       ├── password: splitwiser
       ├── host: localhost
       ├── port: 5432
       └── database: splitwiser

So:

postgresql://USERNAME:PASSWORD@HOST:PORT/DATABASE

This format is extremely common.

3.9 Don't hardcode this into Python

You might be tempted to write:

DATABASE_URL = "postgresql://splitwiser:splitwiser@localhost:5432/splitwiser"

Don't.

Eventually you'll have:

development
staging
production

and each environment will have different credentials.

Instead, we'll use an environment variable.

Create:

.env

at your project root:

splitwiser/
├── .env
├── app/
│   └── main.py
└── ...

Put:

DATABASE_URL=postgresql://splitwiser:splitwiser@localhost:5432/splitwiser

And make sure .env is in .gitignore.

Create:

.gitignore

with:

.venv/
.env
__pycache__/

Even though this is a local learning database, get into the habit of never committing credentials.

3.10 Install SQLAlchemy and PostgreSQL driver

Now:

pip install sqlalchemy psycopg[binary] python-dotenv

We're introducing three things:

SQLAlchemy

Python's SQL toolkit/ORM.

psycopg

The PostgreSQL driver that actually communicates with PostgreSQL.

python-dotenv

Loads .env variables into your application.

3.11 What is SQLAlchemy?

This is important.

You could write SQL directly from Python:

cursor.execute(
    "SELECT * FROM users WHERE id = %s",
    (user_id,)
)

That works.

But SQLAlchemy gives us a layer where we can work with Python models and database queries.

Conceptually:

Python
   │
   ▼
SQLAlchemy
   │
   ▼
SQL
   │
   ▼
PostgreSQL

For example, eventually we'll be able to express:

select(User).where(User.id == user_id)

and SQLAlchemy generates appropriate SQL.

But don't think of SQLAlchemy as a replacement for SQL.

You should still understand what's happening underneath.

3.12 Create our database configuration

Let's clean up our project.

Move toward:

splitwiser/
│
├── .env
├── .gitignore
│
└── app/
    ├── __init__.py
    ├── main.py
    └── database.py

Create:

touch app/database.py
touch app/__init__.py
3.13 database.py

Put this in:

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

Let's understand this slowly.

load_dotenv()
load_dotenv()

loads:

.env

so:

os.getenv("DATABASE_URL")

can retrieve:

postgresql://splitwiser:splitwiser@localhost:5432/splitwiser
3.14 What is an Engine?

This:

engine = create_engine(DATABASE_URL)

creates SQLAlchemy's connection infrastructure to PostgreSQL.

Think:

FastAPI
   │
   ▼
SQLAlchemy Engine
   │
   ▼
PostgreSQL

The engine knows:

"Here's how I communicate with this database."

3.15 What is a Session?

This:

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

creates a factory for database sessions.

A session represents a unit of interaction with the database.

Conceptually:

API request
    │
    ▼
Open DB session
    │
    ├── Query
    ├── Insert
    ├── Update
    └── Delete
    │
    ▼
Commit / rollback
    │
    ▼
Close session

We'll use this heavily.

3.16 Now create our database model

Create:

app/models.py

Add:

from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False
    )

This is your first SQLAlchemy model.

And this is an important distinction:

UserCreate

is a Pydantic model.

User

is a database model.

Don't confuse them.

3.17 Pydantic vs SQLAlchemy

This is one of the most important concepts in this phase.

Pydantic

Used for API data:

HTTP
 ↓
Pydantic
 ↓
Python

Example:

class UserCreate(BaseModel):
    name: str
    email: EmailStr

It answers:

Is the incoming API data valid?

SQLAlchemy

Used for database data:

Python
 ↓
SQLAlchemy
 ↓
PostgreSQL

Example:

class User(Base):
    ...

It answers:

How does a User exist in our database?

So:

                  Client
                     │
                     ▼
              ┌─────────────┐
              │  Pydantic   │
              │ UserCreate  │
              └──────┬──────┘
                     │
                     ▼
                Application
                     │
                     ▼
              ┌─────────────┐
              │ SQLAlchemy  │
              │    User     │
              └──────┬──────┘
                     │
                     ▼
                PostgreSQL

This separation is fundamental.

3.18 Create the table

We now have a model, but PostgreSQL doesn't know about it yet.

For our learning phase, we'll initially create tables programmatically.

Update database.py:

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)


class Base(DeclarativeBase):
    pass


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

But then our model needs to use the same Base.

So let's make the structure slightly cleaner.

database.py
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


class Base(DeclarativeBase):
    pass


engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)
models.py
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False
    )

Now SQLAlchemy knows:

Base
 │
 └── User
       │
       └── users table
3.19 Create tables

Temporarily, add this to main.py:

from app.database import Base, engine
from app import models

Base.metadata.create_all(bind=engine)

This tells SQLAlchemy:

Create all tables represented by my models if they don't already exist.

Then run:

fastapi dev app/main.py

If everything works, SQLAlchemy should create:

users

inside PostgreSQL.

3.20 Verify the database

You can inspect PostgreSQL using:

docker exec -it splitwiser-postgres psql \
  -U splitwiser \
  -d splitwiser

You'll enter the PostgreSQL CLI.

Then:

\dt

You should see:

users

Then:

\d users

You should see something representing:

id       integer     primary key
name     varchar
email    varchar     unique

This is a very important moment.

Your Python model:

class User(Base):

has become an actual PostgreSQL table.

3.21 But our API still uses the dictionary!

Exactly.

That's our next task.

Currently:

users = {}

is still our database.

We need to replace:

users dictionary

with:

PostgreSQL

But don't delete it just yet.

We'll migrate one endpoint at a time.

3.22 First database-powered endpoint

Let's create a database session dependency.

In database.py, add:

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

This is a FastAPI dependency.

Don't worry if yield feels strange.

Conceptually:

Request
   │
   ▼
get_db()
   │
   ▼
Open database session
   │
   ▼
Endpoint uses it
   │
   ▼
Endpoint finishes
   │
   ▼
Close database session

This pattern is extremely common in FastAPI.

3.23 Use the database session

Import:

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db

Then:

@app.get("/users/{user_id}")
def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    ...

Now FastAPI understands:

Before calling get_user, give it a database session.

So:

db: Session = Depends(get_db)

is essentially saying:

FastAPI:
"Please provide me with a database Session."
3.24 Query the database

Now we can retrieve a user.

With modern SQLAlchemy:

from sqlalchemy import select

Then:

result = db.execute(
    select(User).where(User.id == user_id)
)

user = result.scalar_one_or_none()

Let's understand this.

We want:

SELECT *
FROM users
WHERE id = 1;

SQLAlchemy:

select(User).where(User.id == user_id)

is expressing the same idea.

Then:

scalar_one_or_none()

means:

one user → return it

no user → return None

multiple users → error
3.25 Complete GET endpoint

Your endpoint becomes:

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
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

Notice something interesting.

We didn't manually convert:

User

into:

{
    "id": ...,
    "name": ...,
    "email": ...
}

Our response model handles the API representation.

3.26 Now create users in PostgreSQL

Our POST endpoint currently does:

users[next_user_id] = new_user

We're going to replace that.

First create:

new_user = User(
    name=user.name,
    email=user.email
)

Then:

db.add(new_user)
db.commit()
db.refresh(new_user)

This is a critical sequence.

db.add()
db.add(new_user)

means:

SQLAlchemy, I want this object inserted into the database.

db.commit()
db.commit()

means:

Actually commit this transaction.

db.refresh()
db.refresh(new_user)

means:

Refresh the Python object with the database's current values.

This matters because PostgreSQL generates the ID.

For example:

Before commit:

new_user
id = ???

After commit:

new_user
id = 1
3.27 Your new POST endpoint

It should eventually look like:

@app.post(
    "/users",
    response_model=UserResponse,
    status_code=201
)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
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

Now the flow is:

POST /users
      │
      ▼
Pydantic
      │
      ▼
UserCreate
      │
      ▼
SQLAlchemy User
      │
      ▼
PostgreSQL
      │
      ▼
UserResponse
      │
      ▼
JSON
3.28 Notice what disappeared

We no longer need:

users = {}
next_user_id = 1

because PostgreSQL handles persistence and ID generation.

Your architecture has changed from:

FastAPI
   │
   ▼
Python dictionary

to:

FastAPI
   │
   ▼
SQLAlchemy
   │
   ▼
PostgreSQL

That's the major milestone of Phase 3.

One important thing: don't rush ahead

At this point, don't add Groups yet.

First make sure you understand this entire flow.

Your project should now roughly be:

splitwiser/
│
├── .env
├── .gitignore
│
└── app/
    ├── __init__.py
    ├── main.py
    ├── database.py
    └── models.py

And conceptually:

main.py
   │
   │ Depends(get_db)
   ▼
database.py
   │
   │ SQLAlchemy Session
   ▼
models.py
   │
   │ User model
   ▼
PostgreSQL
Your first Phase 3 exercise

Before we continue, I want you to get this working.

1. Start PostgreSQL
docker start splitwiser-postgres
2. Start FastAPI
fastapi dev app/main.py
3. Open
http://127.0.0.1:8000/docs
4. Create two users
{
  "name": "Santhosh",
  "email": "santhosh@example.com"
}

and:

{
  "name": "Arun",
  "email": "arun@example.com"
}
5. Stop FastAPI

Ctrl + C

6. Start it again
fastapi dev app/main.py
7. Call:
GET /users/1

If Santhosh is still there:

🎉 You have successfully moved from in-memory storage to persistent database storage.

And one conceptual challenge for you

Try to explain this in your own words:

Pydantic UserCreate
          ↓
       FastAPI
          ↓
    SQLAlchemy User
          ↓
      PostgreSQL

Specifically:

Why do we need both UserCreate and User? Why not just use the SQLAlchemy User model everywhere?

If you can explain that, you've understood one of the most important architectural ideas in this phase.