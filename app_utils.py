import hashlib
import os

import mysql.connector
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "mydatabase"),
}

FACE_CASCADE_PATHS = [
    "haarcascades/haarcascade_frontalface_default.xml",
    "haarcascades/haarcascade_frontalcatface.xml",
    "haarcascades/haarcascade_frontalcatface_extended.xml",
    "haarcascades/haarcascade_frontalface_alt_tree.xml",
    "haarcascades/haarcascade_frontalface_alt.xml",
    "haarcascades/haarcascade_frontalface_alt2.xml",
]


def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)


def hash_password(password):
    return hashlib.md5(password.encode("utf-8")).hexdigest()


def ensure_directories(*paths):
    for path in paths:
        os.makedirs(path, exist_ok=True)
