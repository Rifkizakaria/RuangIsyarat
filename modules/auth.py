import os
import json
import hashlib
from typing import Tuple

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
USERS_FILE = os.path.join(DATA_DIR, "users.json")


def _ensure_data_file() -> None:
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, indent=2)


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def load_users() -> list:
    _ensure_data_file()
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def _save_users(users: list) -> None:
    _ensure_data_file()
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)


def register_user(nickname: str, password: str) -> Tuple[bool, str]:
    nick = nickname.strip()
    pwd = password.strip()

    if not nick or not pwd:
        return False, "Kolom tidak boleh kosong!"

    users = load_users()
    for user in users:
        if user.get("nickname", "").lower() == nick.lower():
            return False, "Nickname sudah dipakai"

    users.append({
        "nickname": nick,
        "password": _hash_password(pwd)
    })
    _save_users(users)
    return True, "Pendaftaran berhasil! Silakan masuk."


def login_user(nickname: str, password: str) -> Tuple[bool, str]:
    nick = nickname.strip()
    pwd = password.strip()

    if not nick or not pwd:
        return False, "Kolom tidak boleh kosong!"

    users = load_users()
    hashed_pwd = _hash_password(pwd)

    for user in users:
        if user.get("nickname", "").lower() == nick.lower() and user.get("password") == hashed_pwd:
            return True, "Login berhasil"

    return False, "Nickname atau password salah"

