import logging

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from .auth_store import DbAuthStore
from .schemas import Credentials, Priority, Status, Task, TaskCreate, TaskUpdate, User
from .security import SESSION_LIFETIME
from .store import DbTaskStore

app = FastAPI(title="Task Flow API")
store = DbTaskStore()
auth_store = DbAuthStore()
logger = logging.getLogger(__name__)

TASK_NOT_FOUND = "할 일을 찾을 수 없습니다."
DATABASE_ERROR = "DB에 연결할 수 없거나 처리 중 오류가 발생했습니다."
USERNAME_TAKEN = "이미 사용 중인 아이디입니다."
LOGIN_FAILED = "아이디 또는 비밀번호가 올바르지 않습니다."
LOGIN_REQUIRED = "로그인이 필요합니다."
SESSION_COOKIE = "task_flow_session"


@app.exception_handler(SQLAlchemyError)
def handle_database_error(request: Request, error: SQLAlchemyError) -> JSONResponse:
    """DB 오류는 내부 내용을 응답에 노출하지 않고 503으로 알린다. 자세한 내용은 서버 로그에 남긴다."""
    logger.error("DB 오류: %s %s: %s", request.method, request.url.path, error)
    return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content={"detail": DATABASE_ERROR})


@app.get("/api/health")
def health() -> dict[str, str]:
    """API 서버가 요청을 처리할 수 있는지 확인한다."""
    return {"status": "ok"}


def set_session_cookie(response: Response, token: str) -> None:
    # HTTPS로 배포하면 secure=True로 바꾼다(API-SPEC 인증 규칙).
    response.set_cookie(
        SESSION_COOKIE,
        token,
        max_age=int(SESSION_LIFETIME.total_seconds()),
        path="/",
        httponly=True,
        samesite="lax",
    )


def end_previous_session(request: Request) -> None:
    """로그인·가입 전에 요청에 실려 온 기존 세션이 있으면 서버에서 지운다."""
    token = request.cookies.get(SESSION_COOKIE)
    if token:
        auth_store.logout(token)


@app.post("/api/auth/signup", status_code=status.HTTP_201_CREATED)
def signup(data: Credentials, request: Request, response: Response) -> User:
    """회원가입하고 바로 로그인한다."""
    result = auth_store.signup(data.username, data.password)
    if result is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=USERNAME_TAKEN)
    end_previous_session(request)
    user, token = result
    set_session_cookie(response, token)
    return user


@app.post("/api/auth/login")
def login(data: Credentials, request: Request, response: Response) -> User:
    """아이디·비밀번호가 맞으면 새 세션 쿠키를 발급한다."""
    result = auth_store.login(data.username, data.password)
    if result is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=LOGIN_FAILED)
    end_previous_session(request)
    user, token = result
    set_session_cookie(response, token)
    return user


@app.post("/api/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request, response: Response) -> None:
    """현재 세션을 지우고 쿠키를 삭제한다. 로그인하지 않은 상태에서도 204."""
    end_previous_session(request)
    response.delete_cookie(SESSION_COOKIE, path="/", httponly=True, samesite="lax")


@app.get("/api/auth/me")
def me(request: Request) -> User:
    """현재 로그인한 사용자를 반환한다."""
    token = request.cookies.get(SESSION_COOKIE)
    user = auth_store.user_for_token(token) if token else None
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=LOGIN_REQUIRED)
    return user


@app.get("/api/tasks")
def list_tasks(
    q: str | None = None,
    status: Status | None = None,
    priority: Priority | None = None,
) -> list[Task]:
    """제목 검색(q)과 상태·우선순위 필터를 AND로 적용해 등록 순서로 반환한다."""
    return store.list(q=q, status=status, priority=priority)


@app.post("/api/tasks", status_code=status.HTTP_201_CREATED)
def create_task(data: TaskCreate) -> Task:
    """할 일을 등록한다. 상태는 항상 TODO로 시작한다."""
    return store.create(data)


@app.patch("/api/tasks/{task_id}")
def update_task(task_id: int, data: TaskUpdate) -> Task:
    """보낸 필드만 수정하고 나머지는 유지한다."""
    task = store.update(task_id, data.changes())
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=TASK_NOT_FOUND)
    return task


@app.delete("/api/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int) -> None:
    """할 일을 삭제한다."""
    if not store.delete(task_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=TASK_NOT_FOUND)
