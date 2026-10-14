from datetime import datetime, timezone

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .database import SessionLocal
from .models import AuthSessionRow, UserRow
from .schemas import User
from .security import (
    SESSION_LIFETIME,
    hash_password,
    hash_session_token,
    new_session_token,
    verify_password,
)

# 없는 아이디로 로그인할 때도 해시 검증 시간을 똑같이 써서, 응답 시간으로 아이디 존재 여부를 알 수 없게 한다.
_DUMMY_PASSWORD_HASH = hash_password("dummy-password-for-timing")


def _utc_now() -> datetime:
    """DB에는 시간대 정보 없이 UTC로 저장한다."""
    return datetime.now(timezone.utc).replace(microsecond=0, tzinfo=None)


def to_user(row: UserRow) -> User:
    return User(id=row.id, username=row.username, created_at=row.created_at.replace(tzinfo=timezone.utc))


def _add_session(session: Session, user_id: int) -> str:
    """세션 행을 추가하고 쿠키에 담을 토큰을 반환한다. DB에는 토큰의 해시만 저장한다."""
    token = new_session_token()
    now = _utc_now()
    session.add(
        AuthSessionRow(
            user_id=user_id,
            token_hash=hash_session_token(token),
            created_at=now,
            expires_at=now + SESSION_LIFETIME,
        )
    )
    return token


class DbAuthStore:
    """MariaDB users·sessions 테이블로 회원가입·로그인·세션을 처리한다."""

    def signup(self, username: str, password: str) -> tuple[User, str] | None:
        """사용자를 만들고 바로 세션을 연다. 이미 있는 아이디면 None."""
        try:
            with SessionLocal() as session, session.begin():
                row = UserRow(username=username, password_hash=hash_password(password), created_at=_utc_now())
                session.add(row)
                session.flush()
                token = _add_session(session, row.id)
                return to_user(row), token
        except IntegrityError:
            # 동시에 같은 아이디로 가입해도 DB 고유 제약이 막는다.
            return None

    def login(self, username: str, password: str) -> tuple[User, str] | None:
        """아이디·비밀번호가 맞으면 새 세션을 연다. 틀리면 이유와 관계없이 None."""
        with SessionLocal() as session, session.begin():
            row = session.scalar(select(UserRow).where(UserRow.username == username))
            stored_hash = row.password_hash if row is not None else _DUMMY_PASSWORD_HASH
            if not verify_password(password, stored_hash) or row is None:
                return None
            token = _add_session(session, row.id)
            return to_user(row), token

    def user_for_token(self, token: str) -> User | None:
        """유효한 세션의 사용자를 반환한다. 없거나 만료된 세션은 None이며, 만료된 세션 행은 지운다."""
        token_hash = hash_session_token(token)
        with SessionLocal() as session, session.begin():
            auth = session.scalar(select(AuthSessionRow).where(AuthSessionRow.token_hash == token_hash))
            if auth is None:
                return None
            if auth.expires_at <= _utc_now():
                session.delete(auth)
                return None
            user = session.get(UserRow, auth.user_id)
            return to_user(user) if user is not None else None

    def logout(self, token: str) -> None:
        """해당 세션만 지운다. 같은 사용자의 다른 세션은 유지된다."""
        with SessionLocal() as session, session.begin():
            session.execute(delete(AuthSessionRow).where(AuthSessionRow.token_hash == hash_session_token(token)))
