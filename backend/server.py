from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Union
import uuid
from datetime import datetime, timezone, timedelta
import jwt
from passlib.context import CryptContext
import bcrypt

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Security
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here-change-in-production')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Create the main app
app = FastAPI(title="E-Rapor SMK API", version="1.0.0")

# Create API router
api_router = APIRouter(prefix="/api")

# User roles
class UserRole:
    ADMIN = "admin"
    GURU_MAPEL = "guru_mapel"
    GURU_PKL = "guru_pkl" 
    FASILITATOR_P5 = "fasilitator_p5"
    GURU_EKSTRA = "guru_ekstra"
    WALI_KELAS = "wali_kelas"

# Pydantic Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    name: str
    role: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str
    role: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

class Jurusan(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    kode_jurusan: str
    nama_jurusan: str

class Kelas(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tingkatan: str  # X, XI, XII
    jurusan_id: str
    nama_kelas: str
    wali_kelas_id: Optional[str] = None

class Siswa(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nis: str
    nisn: str
    nama_lengkap: str
    jk: str  # L/P
    tanggal_lahir: str
    kelas_id: str
    foto: Optional[str] = None
    is_active: bool = True

class Guru(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    nama: str
    nuptk: Optional[str] = None

class Mapel(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    kode_mapel: str
    nama_mapel: str
    jenis: str  # umum, kejuruan, p5, ekstra
    guru_id: Optional[str] = None

class TahunAjaran(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tahun: str  # 2024/2025
    semester: str  # ganjil, genap
    is_active: bool = False

# Authentication functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = await db.users.find_one({"email": email})
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return User(**user)

def require_role(allowed_roles: List[str]):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return role_checker

# Authentication Routes
@api_router.post("/auth/register", response_model=User)
async def register(user_data: UserCreate):
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    hashed_password = get_password_hash(user_data.password)
    
    # Create user
    user_dict = user_data.dict()
    user_dict["password"] = hashed_password
    user_obj = User(**{k: v for k, v in user_dict.items() if k != "password"})
    
    # Store in database
    await db.users.insert_one({**user_obj.dict(), "password": hashed_password})
    return user_obj

@api_router.post("/auth/login", response_model=Token)
async def login(user_credentials: UserLogin):
    user = await db.users.find_one({"email": user_credentials.email})
    if not user or not verify_password(user_credentials.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user["email"]})
    user_obj = User(**user)
    return Token(access_token=access_token, token_type="bearer", user=user_obj)

@api_router.get("/auth/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

# Dashboard Routes
@api_router.get("/dashboard/stats")
async def get_dashboard_stats(current_user: User = Depends(get_current_user)):
    """Get dashboard statistics based on user role"""
    stats = {}
    
    if current_user.role == UserRole.ADMIN:
        # Admin can see all statistics
        stats["total_siswa"] = await db.siswa.count_documents({"is_active": True})
        stats["total_guru"] = await db.guru.count_documents({})
        stats["total_kelas"] = await db.kelas.count_documents({})
        stats["total_mapel"] = await db.mapel.count_documents({})
    elif current_user.role == UserRole.WALI_KELAS:
        # Wali kelas can see their class statistics
        wali_kelas = await db.kelas.find_one({"wali_kelas_id": current_user.id})
        if wali_kelas:
            stats["siswa_di_kelas"] = await db.siswa.count_documents({"kelas_id": wali_kelas["id"], "is_active": True})
    
    return stats

# Jurusan Routes (Admin only)
@api_router.get("/jurusan", response_model=List[Jurusan])
async def get_jurusan(current_user: User = Depends(require_role([UserRole.ADMIN]))):
    jurusan_list = await db.jurusan.find().to_list(1000)
    return [Jurusan(**j) for j in jurusan_list]

@api_router.post("/jurusan", response_model=Jurusan)
async def create_jurusan(jurusan: Jurusan, current_user: User = Depends(require_role([UserRole.ADMIN]))):
    await db.jurusan.insert_one(jurusan.dict())
    return jurusan

# Kelas Routes (Admin only)
@api_router.get("/kelas", response_model=List[Kelas])
async def get_kelas(current_user: User = Depends(require_role([UserRole.ADMIN]))):
    kelas_list = await db.kelas.find().to_list(1000)
    return [Kelas(**k) for k in kelas_list]

@api_router.post("/kelas", response_model=Kelas)
async def create_kelas(kelas: Kelas, current_user: User = Depends(require_role([UserRole.ADMIN]))):
    await db.kelas.insert_one(kelas.dict())
    return kelas

# Siswa Routes (Admin only for CRUD)
@api_router.get("/siswa", response_model=List[Siswa])
async def get_siswa(current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.WALI_KELAS]))):
    if current_user.role == UserRole.WALI_KELAS:
        # Wali kelas can only see their students
        wali_kelas = await db.kelas.find_one({"wali_kelas_id": current_user.id})
        if wali_kelas:
            siswa_list = await db.siswa.find({"kelas_id": wali_kelas["id"], "is_active": True}).to_list(1000)
        else:
            siswa_list = []
    else:
        # Admin can see all students
        siswa_list = await db.siswa.find({"is_active": True}).to_list(1000)
    
    return [Siswa(**s) for s in siswa_list]

@api_router.post("/siswa", response_model=Siswa)
async def create_siswa(siswa: Siswa, current_user: User = Depends(require_role([UserRole.ADMIN]))):
    await db.siswa.insert_one(siswa.dict())
    return siswa

# Initialize default data
@api_router.post("/init/default-data")
async def init_default_data(current_user: User = Depends(require_role([UserRole.ADMIN]))):
    """Initialize default jurusan, kelas, and mapel data"""
    
    # Default jurusan
    default_jurusan = [
        {"kode_jurusan": "AKL", "nama_jurusan": "Akuntansi dan Keuangan Lembaga"},
        {"kode_jurusan": "MP", "nama_jurusan": "Manajemen Perkantoran"},
        {"kode_jurusan": "RPL", "nama_jurusan": "Rekayasa Perangkat Lunak"},
        {"kode_jurusan": "TO", "nama_jurusan": "Teknik Otomotif (TSM)"}
    ]
    
    for j_data in default_jurusan:
        existing = await db.jurusan.find_one({"kode_jurusan": j_data["kode_jurusan"]})
        if not existing:
            j_obj = Jurusan(**j_data)
            await db.jurusan.insert_one(j_obj.dict())
    
    # Default mapel
    default_mapel = [
        {"kode_mapel": "PABP", "nama_mapel": "Pendidikan Agama dan Budi Pekerti", "jenis": "umum"},
        {"kode_mapel": "PPKN", "nama_mapel": "Pendidikan Pancasila dan Kewarganegaraan", "jenis": "umum"},
        {"kode_mapel": "BINDO", "nama_mapel": "Bahasa Indonesia", "jenis": "umum"},
        {"kode_mapel": "MAT", "nama_mapel": "Matematika", "jenis": "umum"},
        {"kode_mapel": "SEJ", "nama_mapel": "Sejarah", "jenis": "umum"},
        {"kode_mapel": "BING", "nama_mapel": "Bahasa Inggris", "jenis": "umum"},
        {"kode_mapel": "PJOK", "nama_mapel": "Pendidikan Jasmani, Olahraga, dan Kesehatan", "jenis": "umum"},
        {"kode_mapel": "AKL1", "nama_mapel": "Akuntansi Dasar", "jenis": "kejuruan"},
        {"kode_mapel": "MP1", "nama_mapel": "Otomatisasi Tata Kelola Perkantoran", "jenis": "kejuruan"},
        {"kode_mapel": "RPL1", "nama_mapel": "Pemrograman Dasar", "jenis": "kejuruan"},
        {"kode_mapel": "TO1", "nama_mapel": "Teknik Kendaraan Ringan", "jenis": "kejuruan"},
        {"kode_mapel": "P5", "nama_mapel": "Projek P5", "jenis": "p5"},
        {"kode_mapel": "PRAM", "nama_mapel": "Pramuka", "jenis": "ekstra"},
        {"kode_mapel": "PMR", "nama_mapel": "Palang Merah Remaja", "jenis": "ekstra"}
    ]
    
    for m_data in default_mapel:
        existing = await db.mapel.find_one({"kode_mapel": m_data["kode_mapel"]})
        if not existing:
            m_obj = Mapel(**m_data)
            await db.mapel.insert_one(m_obj.dict())
    
    return {"message": "Default data initialized successfully"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()