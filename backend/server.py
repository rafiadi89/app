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

# CRUD Operations for Siswa (Admin only)
@api_router.get("/siswa/{siswa_id}", response_model=Siswa)
async def get_siswa_by_id(siswa_id: str, current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.WALI_KELAS]))):
    siswa = await db.siswa.find_one({"id": siswa_id, "is_active": True})
    if not siswa:
        raise HTTPException(status_code=404, detail="Siswa not found")
    return Siswa(**siswa)

@api_router.put("/siswa/{siswa_id}", response_model=Siswa)
async def update_siswa(siswa_id: str, siswa_data: Siswa, current_user: User = Depends(require_role([UserRole.ADMIN]))):
    existing_siswa = await db.siswa.find_one({"id": siswa_id})
    if not existing_siswa:
        raise HTTPException(status_code=404, detail="Siswa not found")
    
    await db.siswa.update_one({"id": siswa_id}, {"$set": siswa_data.dict()})
    updated_siswa = await db.siswa.find_one({"id": siswa_id})
    return Siswa(**updated_siswa)

@api_router.delete("/siswa/{siswa_id}")
async def delete_siswa(siswa_id: str, current_user: User = Depends(require_role([UserRole.ADMIN]))):
    result = await db.siswa.update_one({"id": siswa_id}, {"$set": {"is_active": False}})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Siswa not found")
    return {"message": "Siswa deleted successfully"}

# CRUD Operations for Guru (Admin only)
@api_router.get("/guru", response_model=List[Guru])
async def get_guru_list(current_user: User = Depends(require_role([UserRole.ADMIN]))):
    guru_list = await db.guru.find().to_list(1000)
    return [Guru(**g) for g in guru_list]

@api_router.get("/guru/{guru_id}", response_model=Guru)
async def get_guru_by_id(guru_id: str, current_user: User = Depends(require_role([UserRole.ADMIN]))):
    guru = await db.guru.find_one({"id": guru_id})
    if not guru:
        raise HTTPException(status_code=404, detail="Guru not found")
    return Guru(**guru)

@api_router.post("/guru", response_model=Guru)
async def create_guru(guru: Guru, current_user: User = Depends(require_role([UserRole.ADMIN]))):
    await db.guru.insert_one(guru.dict())
    return guru

@api_router.put("/guru/{guru_id}", response_model=Guru)
async def update_guru(guru_id: str, guru_data: Guru, current_user: User = Depends(require_role([UserRole.ADMIN]))):
    existing_guru = await db.guru.find_one({"id": guru_id})
    if not existing_guru:
        raise HTTPException(status_code=404, detail="Guru not found")
    
    await db.guru.update_one({"id": guru_id}, {"$set": guru_data.dict()})
    updated_guru = await db.guru.find_one({"id": guru_id})
    return Guru(**updated_guru)

@api_router.delete("/guru/{guru_id}")
async def delete_guru(guru_id: str, current_user: User = Depends(require_role([UserRole.ADMIN]))):
    result = await db.guru.delete_one({"id": guru_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Guru not found")
    return {"message": "Guru deleted successfully"}

# CRUD Operations for Kelas (Admin only)
@api_router.put("/kelas/{kelas_id}", response_model=Kelas)
async def update_kelas(kelas_id: str, kelas_data: Kelas, current_user: User = Depends(require_role([UserRole.ADMIN]))):
    existing_kelas = await db.kelas.find_one({"id": kelas_id})
    if not existing_kelas:
        raise HTTPException(status_code=404, detail="Kelas not found")
    
    await db.kelas.update_one({"id": kelas_id}, {"$set": kelas_data.dict()})
    updated_kelas = await db.kelas.find_one({"id": kelas_id})
    return Kelas(**updated_kelas)

@api_router.delete("/kelas/{kelas_id}")
async def delete_kelas(kelas_id: str, current_user: User = Depends(require_role([UserRole.ADMIN]))):
    result = await db.kelas.delete_one({"id": kelas_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Kelas not found")
    return {"message": "Kelas deleted successfully"}

# CRUD Operations for Mapel (Admin only)
@api_router.get("/mapel", response_model=List[Mapel])
async def get_mapel_list(jenis: Optional[str] = None, current_user: User = Depends(get_current_user)):
    query = {}
    if jenis:
        query["jenis"] = jenis
    
    mapel_list = await db.mapel.find(query).to_list(1000)
    return [Mapel(**m) for m in mapel_list]

@api_router.post("/mapel", response_model=Mapel)
async def create_mapel(mapel: Mapel, current_user: User = Depends(require_role([UserRole.ADMIN]))):
    await db.mapel.insert_one(mapel.dict())
    return mapel

@api_router.put("/mapel/{mapel_id}", response_model=Mapel)
async def update_mapel(mapel_id: str, mapel_data: Mapel, current_user: User = Depends(require_role([UserRole.ADMIN]))):
    existing_mapel = await db.mapel.find_one({"id": mapel_id})
    if not existing_mapel:
        raise HTTPException(status_code=404, detail="Mapel not found")
    
    await db.mapel.update_one({"id": mapel_id}, {"$set": mapel_data.dict()})
    updated_mapel = await db.mapel.find_one({"id": mapel_id})
    return Mapel(**updated_mapel)

@api_router.delete("/mapel/{mapel_id}")
async def delete_mapel(mapel_id: str, current_user: User = Depends(require_role([UserRole.ADMIN]))):
    result = await db.mapel.delete_one({"id": mapel_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Mapel not found")
    return {"message": "Mapel deleted successfully"}

# CRUD Operations for Tahun Ajaran (Admin only)
@api_router.get("/tahun-ajaran", response_model=List[TahunAjaran])
async def get_tahun_ajaran_list(current_user: User = Depends(require_role([UserRole.ADMIN]))):
    tahun_ajaran_list = await db.tahun_ajaran.find().to_list(1000)
    return [TahunAjaran(**ta) for ta in tahun_ajaran_list]

@api_router.post("/tahun-ajaran", response_model=TahunAjaran)
async def create_tahun_ajaran(tahun_ajaran: TahunAjaran, current_user: User = Depends(require_role([UserRole.ADMIN]))):
    # If this is set as active, deactivate others
    if tahun_ajaran.is_active:
        await db.tahun_ajaran.update_many({}, {"$set": {"is_active": False}})
    
    await db.tahun_ajaran.insert_one(tahun_ajaran.dict())
    return tahun_ajaran

@api_router.put("/tahun-ajaran/{ta_id}", response_model=TahunAjaran)
async def update_tahun_ajaran(ta_id: str, ta_data: TahunAjaran, current_user: User = Depends(require_role([UserRole.ADMIN]))):
    existing_ta = await db.tahun_ajaran.find_one({"id": ta_id})
    if not existing_ta:
        raise HTTPException(status_code=404, detail="Tahun Ajaran not found")
    
    # If this is set as active, deactivate others
    if ta_data.is_active:
        await db.tahun_ajaran.update_many({}, {"$set": {"is_active": False}})
    
    await db.tahun_ajaran.update_one({"id": ta_id}, {"$set": ta_data.dict()})
    updated_ta = await db.tahun_ajaran.find_one({"id": ta_id})
    return TahunAjaran(**updated_ta)

@api_router.delete("/tahun-ajaran/{ta_id}")
async def delete_tahun_ajaran(ta_id: str, current_user: User = Depends(require_role([UserRole.ADMIN]))):
    result = await db.tahun_ajaran.delete_one({"id": ta_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Tahun Ajaran not found")
    return {"message": "Tahun Ajaran deleted successfully"}

# Search and Filter endpoints
@api_router.get("/siswa/search")
async def search_siswa(
    q: Optional[str] = None,
    kelas_id: Optional[str] = None, 
    jurusan_id: Optional[str] = None,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.WALI_KELAS]))
):
    query = {"is_active": True}
    
    if q:
        query["$or"] = [
            {"nama_lengkap": {"$regex": q, "$options": "i"}},
            {"nis": {"$regex": q, "$options": "i"}},
            {"nisn": {"$regex": q, "$options": "i"}}
        ]
    
    if kelas_id:
        query["kelas_id"] = kelas_id
        
    # If wali kelas, only show their students
    if current_user.role == UserRole.WALI_KELAS:
        wali_kelas = await db.kelas.find_one({"wali_kelas_id": current_user.id})
        if wali_kelas:
            query["kelas_id"] = wali_kelas["id"]
        else:
            return []
    
    siswa_list = await db.siswa.find(query).limit(100).to_list(100)
    return [Siswa(**s) for s in siswa_list]

# Get detailed kelas with jurusan info
@api_router.get("/kelas/detailed")
async def get_kelas_detailed(current_user: User = Depends(get_current_user)):
    kelas_list = await db.kelas.find().to_list(1000)
    detailed_kelas = []
    
    for kelas in kelas_list:
        # Get jurusan info
        jurusan = await db.jurusan.find_one({"id": kelas["jurusan_id"]})
        
        # Get wali kelas info if assigned
        wali_kelas = None
        if kelas.get("wali_kelas_id"):
            wali_kelas = await db.users.find_one({"id": kelas["wali_kelas_id"]})
        
        # Count siswa in this kelas
        siswa_count = await db.siswa.count_documents({"kelas_id": kelas["id"], "is_active": True})
        
        detailed_kelas.append({
            **kelas,
            "jurusan": jurusan,
            "wali_kelas": wali_kelas,
            "siswa_count": siswa_count
        })
    
    return detailed_kelas

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
    
    # Create default kelas for each jurusan
    jurusan_list = await db.jurusan.find().to_list(1000)
    tingkatan = ["X", "XI", "XII"]
    
    for tingkat in tingkatan:
        for jurusan in jurusan_list:
            kelas_name = f"{tingkat} {jurusan['kode_jurusan']} 1"
            existing = await db.kelas.find_one({"nama_kelas": kelas_name})
            if not existing:
                kelas_obj = Kelas(
                    tingkatan=tingkat,
                    jurusan_id=jurusan["id"],
                    nama_kelas=kelas_name
                )
                await db.kelas.insert_one(kelas_obj.dict())
    
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
    
    # Create default tahun ajaran
    current_year = 2024
    default_ta = f"{current_year}/{current_year + 1}"
    existing_ta = await db.tahun_ajaran.find_one({"tahun": default_ta})
    if not existing_ta:
        ta_ganjil = TahunAjaran(tahun=default_ta, semester="ganjil", is_active=True)
        await db.tahun_ajaran.insert_one(ta_ganjil.dict())
    
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