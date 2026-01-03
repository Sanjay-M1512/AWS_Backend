from datetime import timedelta
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MONGO_URI = os.getenv("MONGO_URI")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    
    # 🔐 Token expiry (30 minutes)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)