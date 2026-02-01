from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional

# =====================
# DATABASE SETUP
# =====================
DATABASE_URL = "sqlite:///./app.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# =====================
# MODELS
# =====================
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_admin = Column(Boolean, default=False)
    verifications = relationship("Verification", back_populates="owner")


class Verification(Base):
    __tablename__ = "verifications"
    id = Column(Integer, primary_key=True, index=True)
    id_type = Column(String)
    id_number = Column(String)
    status = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="verifications")


Base.metadata.create_all(bind=engine)

# =====================
# SCHEMAS
# =====================
class UserCreate(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class VerificationRequest(BaseModel):
    id_type: str  # "NIA" or "NHIS"
    id_number: str


class VerificationOut(BaseModel):
    id: int
    id_type: str
    id_number: str
    status: str

    class Config:
        from_attributes = True


# =====================
# AUTH SETUP
# =====================
SECRET_KEY = "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

app = FastAPI(title="Identity Verification API")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user


def get_admin_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


def mock_verify(id_type: str, id_number: str) -> str:
    """Mock verification logic - even last digit = verified, odd = failed"""
    last_digit = int(id_number[-1]) if id_number[-1].isdigit() else 0
    return "verified" if last_digit % 2 == 0 else "failed"


# =====================
# ENDPOINTS
# =====================
@app.get("/")
def root():
    return {"message": "Identity Verification API is running"}


@app.post("/register", response_model=dict)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = get_password_hash(user.password)
    new_user = User(email=user.email, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully", "email": new_user.email}


@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Ensure subject is a string to comply with JWT libraries that expect string sub
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}


@app.get("/me")
def read_users_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "is_admin": current_user.is_admin,
    }


@app.post("/verify-id", response_model=VerificationOut)
def verify_id(
    data: VerificationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    status_result = mock_verify(data.id_type, data.id_number)

    record = Verification(
        id_type=data.id_type,
        id_number=data.id_number,
        status=status_result,
        owner=current_user,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@app.get("/admin/verifications", response_model=list[VerificationOut])
def list_all_verifications(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    records = db.query(Verification).all()
    return records