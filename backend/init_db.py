"""tasks·users·sessions 테이블을 만든다. 이미 있는 테이블과 데이터는 변경하거나 삭제하지 않는다.

실행: python -m backend.init_db
"""

from sqlalchemy import inspect

from .database import Base, engine
from .models import AuthSessionRow, TaskRow, UserRow


def main() -> None:
    tables = [TaskRow.__tablename__, UserRow.__tablename__, AuthSessionRow.__tablename__]
    inspector = inspect(engine)
    existed = {table: inspector.has_table(table) for table in tables}
    # create_all은 없는 테이블만 만든다.
    Base.metadata.create_all(engine)
    for table in tables:
        if existed[table]:
            print(f"{table} 테이블이 이미 있어 변경하지 않았습니다.")
        else:
            print(f"{table} 테이블을 만들었습니다.")


if __name__ == "__main__":
    main()
