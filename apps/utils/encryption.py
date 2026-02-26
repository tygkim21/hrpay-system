"""
대칭키 암호화 유틸리티 (Fernet / AES-128-CBC)

사용처: 주민등록번호 등 개인정보 필드 암호화
키 도출: settings.SECRET_KEY → SHA-256 → base64url (Fernet 키 형식)
"""
import re
import base64
import hashlib

from cryptography.fernet import Fernet
from django.conf import settings


def _fernet() -> Fernet:
    """settings.SECRET_KEY로부터 안정적인 Fernet 키를 생성"""
    raw = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
    key = base64.urlsafe_b64encode(raw)
    return Fernet(key)


def encrypt(plain: str) -> str:
    """평문 → 암호문(base64 문자열)"""
    if not plain:
        return ''
    return _fernet().encrypt(plain.encode()).decode()


def decrypt(cipher: str) -> str:
    """암호문 → 평문. 복호화 실패 시 빈 문자열 반환"""
    if not cipher:
        return ''
    try:
        return _fernet().decrypt(cipher.encode()).decode()
    except Exception:
        return ''


def mask_resident_no(plain: str) -> str:
    """980101-1234567  →  980101-*******"""
    if not plain:
        return ''
    clean = re.sub(r'[^0-9]', '', plain)
    if len(clean) == 13:
        return f'{clean[:6]}-*******'
    return '***-*******'
