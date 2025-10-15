# config.py
import os
from dotenv import load_dotenv

# Cargar variables del archivo .env
load_dotenv()

# ======================
# 🔑 VARIABLES GLOBALES
# ======================

# Token del bot
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# ======================
# ☁️ CONFIGURACIÓN FIREBASE
# ======================
FIREBASE_CONFIG = {
    "type": os.getenv("FIREBASE_TYPE"),
    "project_id": os.getenv("FIREBASE_PROJECT_ID"),
    "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
    "private_key": os.getenv("FIREBASE_PRIVATE_KEY"),
    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
    "client_id": os.getenv("FIREBASE_CLIENT_ID"),
    "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
    "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
    "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_CERT_URL"),
    "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_CERT_URL"),
}
