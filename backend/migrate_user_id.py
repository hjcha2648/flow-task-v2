"""기존 tasks 테이블에 소유자 열(user_id)을 추가한다(T18).

실행: python -m backend.migrate_user_id
- user_id가 이미 있으면 아무것도 바꾸지 않는다. 여러 번 실행해도 된다.
- 기존 행은 지우거나 바꾸지 않으며 user_id는 NULL(소유자 없음)로 남는다.
- users 테이블이 먼저 있어야 하므로 python -m backend.init_db를 먼저 실행한다.
"""

import sys

from sqlalchemy import inspect, text

from .database import engine

ALTER_SQL = """
ALTER TABLE tasks
    ADD COLUMN user_id INT NULL,
    ADD INDEX ix_tasks_user_id (user_id),
    ADD CONSTRAINT fk_tasks_user_id FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
"""


def main() -> int:
    inspector = inspect(engine)
    if not inspector.has_table("users"):
        print("users 테이블이 없습니다. 먼저 python -m backend.init_db를 실행하세요.", file=sys.stderr)
        return 1
    columns = {column["name"] for column in inspector.get_columns("tasks")}
    if "user_id" in columns:
        print("tasks.user_id가 이미 있어 변경하지 않았습니다.")
        return 0
    with engine.begin() as connection:
        rows = connection.execute(text("SELECT COUNT(*) FROM tasks")).scalar_one()
        connection.execute(text(ALTER_SQL))
    print(f"tasks.user_id를 추가했습니다. 기존 할 일 {rows}개는 소유자 없이 남겨 두었습니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
