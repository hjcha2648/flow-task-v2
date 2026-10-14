"""비밀번호 해시와 세션 토큰. 표준 라이브러리만 사용한다.

- 비밀번호: hashlib.scrypt + 사용자별 임의 솔트. 저장 형식 "scrypt$n$r$p$솔트$해시"(솔트·해시는 base64).
- 세션 토큰: secrets로 만든 임의 문자열을 쿠키에 담고, DB에는 SHA-256 해시만 저장한다.
"""

import base64
import hashlib
import hmac
import secrets
from datetime import timedelta

SCRYPT_N = 2**14
SCRYPT_R = 8
SCRYPT_P = 1
SCRYPT_DKLEN = 64
SALT_BYTES = 16
SESSION_TOKEN_BYTES = 32
SESSION_LIFETIME = timedelta(days=7)


def _scrypt(password: str, salt: bytes, n: int, r: int, p: int, dklen: int) -> bytes:
    return hashlib.scrypt(password.encode("utf-8"), salt=salt, n=n, r=r, p=p, dklen=dklen)


def hash_password(password: str) -> str:
    """비밀번호를 솔트와 함께 해시해 저장용 문자열로 만든다. 같은 비밀번호도 매번 결과가 다르다."""
    salt = secrets.token_bytes(SALT_BYTES)
    digest = _scrypt(password, salt, SCRYPT_N, SCRYPT_R, SCRYPT_P, SCRYPT_DKLEN)
    salt_b64 = base64.b64encode(salt).decode("ascii")
    digest_b64 = base64.b64encode(digest).decode("ascii")
    return f"scrypt${SCRYPT_N}${SCRYPT_R}${SCRYPT_P}${salt_b64}${digest_b64}"


def verify_password(password: str, stored: str) -> bool:
    """저장된 해시와 비밀번호가 맞는지 확인한다. 형식이 잘못된 값은 False."""
    try:
        scheme, n, r, p, salt_b64, digest_b64 = stored.split("$")
        if scheme != "scrypt":
            return False
        salt = base64.b64decode(salt_b64, validate=True)
        expected = base64.b64decode(digest_b64, validate=True)
        # scrypt는 짧은 길이의 결과가 긴 결과의 앞부분과 같으므로, 잘린 해시를 받아들이지 않게 길이를 고정한다.
        if len(salt) != SALT_BYTES or len(expected) != SCRYPT_DKLEN:
            return False
        actual = _scrypt(password, salt, int(n), int(r), int(p), SCRYPT_DKLEN)
    except ValueError:
        return False
    # 비교 시간이 내용에 따라 달라지지 않도록 한다.
    return hmac.compare_digest(actual, expected)


def new_session_token() -> str:
    """쿠키에 담을 추측할 수 없는 세션 토큰을 만든다."""
    return secrets.token_urlsafe(SESSION_TOKEN_BYTES)


def hash_session_token(token: str) -> str:
    """DB에 저장하고 조회할 세션 토큰의 해시(64자 16진수)."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
