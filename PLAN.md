# Task Flow PLAN
## 작업 원칙
한 번에 아래 작업 하나만 구현한다. 실제 확인 전에는 완료로 표시하지 않는다.
상태는 [ ] 미완료, [x] 확인 완료로 관리하고 확인 결과를 각 항목 아래 기록한다.
## 2장: 브라우저 앱
- [x] T01: frontend/index.html, styles.css, app.js 생성. 제목 입력·등록·목록만 구현한다.
  확인: 두 항목 등록, 빈 제목 거절. 이 단계에서 새로고침하면 사라져도 정상이다.
  기록(2026-10-13): frontend/index.html, styles.css, app.js 생성.
  Node DOM 스텁 테스트 통과(두 항목 등록, 빈·공백 제목 거절, 101자 거절, 100자 등록, HTML 글자 표시).
  http.server 5500에서 세 파일 200 응답.
  Windows 브라우저(http://localhost:5500, WSL localhostForwarding)에서 사용자 확인 정상. 남은 오류 없음.
- [x] T02: localStorage(task-flow-v1) 저장·복원.
  확인: 새로고침 후 유지. 손상된 저장값을 자동 덮어쓰지 않는다.
  기록(2026-10-13): frontend/app.js 저장·복원 추가, index.html에 저장 오류 영역·버튼 id 추가, styles.css 비활성 스타일.
  Node 스텁 테스트 통과(저장, 재실행 후 복원, 손상값 4종에서 등록 중지·원래 값 유지, 저장 실패 시 되돌림, T01 회귀).
  http.server 세 파일 200 응답.
  Windows 브라우저에서 사용자 확인 정상(새로고침 후 유지, 손상값 입력 시 등록 중지). 남은 오류 없음.
- [x] T03: 상태 변경, 수정, 삭제 확인.
  확인: 삭제 취소 시 유지. 다른 항목이 수정되지 않는다.
  기록(2026-10-13): frontend/app.js 상태 선택·제목 수정·삭제 확인 추가(id 기준), styles.css 항목 버튼·완료 스타일.
  설명 수정은 T04에서 다룬다. 저장 실패 시 변경을 되돌린다. status 없는 기존 저장값은 TODO로 읽는다.
  Node 스텁 테스트 12개 통과(상태 변경, 빈 제목 수정 거절, 수정·취소·Esc, 삭제 취소 유지, 삭제 시 해당 항목만, 재실행 후 유지, 저장 실패 되돌림, 회귀).
  Windows 브라우저에서 사용자 확인 정상(상태 변경·수정·삭제 취소·삭제, 새로고침 후 유지). 남은 오류 없음.
- [x] T04: 설명·우선순위·마감일·검색·필터·지연 표시.
  확인: 필터 중 수정·삭제, 어제 마감 TODO의 지연 표시.
  기록(2026-10-13): index.html 등록 폼(우선순위·마감일·설명)과 검색·필터 영역 추가, app.js 필드·검증·수정 폼·필터·지연 표시, styles.css 배지·필터 스타일.
  수정 폼에서 제목·설명·우선순위·마감일을 함께 수정한다. 이전 단계 저장값은 빠진 필드를 기본값으로 읽는다.
  Node 스텁 테스트 통과: T04 12개(기본값, 검증, 지연 표시, 검색·필터 AND, 필터 중 수정·삭제, 호환·손상값, 새로고침 유지), T03 회귀 12개.
  Windows 브라우저에서 사용자 확인 정상(어제 마감 TODO 지연 표시, 필터 AND, 필터 중 수정·삭제, 새로고침 유지). 남은 오류 없음.
## 3장: API
- [x] T05: API-SPEC.md 작성, FastAPI /api/health 구현.
  확인: curl로 200과 status=ok.
  기록(2026-10-13): API-SPEC.md(T05~T08 계약), backend/__init__.py, backend/main.py, requirements.txt(fastapi 0.143.0, uvicorn 0.54.0), .gitignore 생성.
  실행: .venv/bin/python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 (Python 3.10.12)
  결과: curl -i /api/health → 200, {"status":"ok"}. /docs 200, 없는 경로 404. 남은 오류 없음.
- [x] T06: 메모리 기반 /api/tasks GET과 POST.
  확인: /docs에서 등록 후 조회. 입력 위반은 422.
  기록(2026-10-13): backend/schemas.py(TaskCreate·Task 검증), backend/store.py(메모리 저장소), backend/main.py에 GET·POST /api/tasks 추가.
  수정: due_date strict 검증이 "2026-10-20"까지 거절해 YYYY-MM-DD 형식 검사 후 날짜 변환하도록 변경.
  실행: 포트 8001에서 uvicorn 실행 후 urllib 스크립트로 확인. 26개 통과(기본값 201, 경계값 201, 위반 18종 422, GET id 순서, 재시작 후 빈 목록).
  /docs 화면에서 사용자 확인 정상(등록 201, 빈 제목 422, 등록 후 조회). 남은 오류 없음.
- [x] T07: PATCH·DELETE와 필터 구현.
  확인: 미전달 필드 유지, 없는 ID 404, 삭제 204.
  기록(2026-10-13): backend/schemas.py TaskUpdate(보낸 필드만 수정, due_date만 null 허용), backend/store.py update·delete·필터, backend/main.py PATCH·DELETE와 q·status·priority 쿼리.
  실행: 포트 8001에서 uvicorn 실행 후 urllib 스크립트로 확인. T07 41개 통과(부분 수정 시 나머지·다른 항목 유지, due_date null 삭제, PATCH 위반 14종 422, 없는 id 404, 삭제 204·재삭제 404, q·status·priority AND, 잘못된 필터 422). T06 회귀 25개 통과.
  남은 오류 없음.
- [x] T08: 프런트엔드 저장 처리를 API 호출로 교체.
  확인: 화면과 curl 목록이 같음. API 중지 시 오류 표시.
  기록(2026-10-13): frontend/app.js localStorage 제거, 목록·등록·상태 변경·수정·삭제를 /api 호출로 교체, 검색·필터는 API 쿼리(q·status·priority)로 조회, 지연 표시는 화면에서 계산.
  backend/main.py에 frontend 정적 파일 제공 추가(같은 주소, CORS 불필요), index.html 오류 영역 id를 api-error로 변경, API-SPEC.md에 화면 제공 방식 추가.
  실행: 포트 8001 uvicorn + Node 스텁(실제 HTTP 요청) 테스트 12개 통과(등록 후 화면·curl 목록 동일, 필터 중 수정·삭제, 404 안내, API 중지 시 오류 표시). T07 API 회귀 41개 통과.
  Windows 브라우저(http://localhost:8000)에서 사용자 확인 정상(화면·curl 목록 동일, API 중지 시 오류 표시). 남은 오류 없음.
## 4장: DB
- [x] T09: MariaDB 전용 사용자·DB와 .env 준비. 접속 확인.
  기록(2026-10-13): MariaDB 10.6.23(127.0.0.1:3306). 사용자가 task_flow DB와 task_flow_app@localhost 생성, .env 작성. .env.example(가짜 값) 추가, .env 권한 600, .gitignore 대상 확인.
  결과: .env 정보로 mariadb 접속 성공(CURRENT_USER task_flow_app@localhost, DATABASE task_flow, utf8mb4_general_ci, 테이블 없음).
  참고: 권한이 ALL PRIVILEGES(DROP 포함)로 부여됨. 비밀번호가 짧아 서버 분리(T12) 전 변경 권장.
- [x] T10: backend/database.py, models.py, init_db.py 생성.
  확인: python -m backend.init_db 실행 후 tasks 테이블 확인.
  기록(2026-10-13): requirements.txt에 SQLAlchemy 2.0.54, PyMySQL 1.2.3 추가. database.py(.env·환경변수 읽기, 엔진·세션), models.py(TaskRow), init_db.py(없는 테이블만 생성) 작성.
  실행: python -m backend.init_db 2회 → 1회차 생성, 2회차 "이미 있어 변경하지 않음".
  결과: DESCRIBE tasks로 id(AUTO_INCREMENT PK)·title varchar(100)·description varchar(2000)·status·priority ENUM·due_date date NULL·created_at datetime 확인. InnoDB, utf8mb4, 0행. 접속 정보 누락 시 안내 오류 확인. 남은 오류 없음.
- [x] T11: API 메모리 저장을 DB로 교체.
  확인: 등록한 행을 SQL로 조회. API 재시작 후 데이터 유지.
  기록(2026-10-13): backend/store.py를 DbTaskStore(MariaDB, 메서드 동일)로 교체, backend/main.py가 DbTaskStore 사용·DB 오류 시 503 응답. API-SPEC.md에 503 추가.
  실행: 포트 8001 uvicorn + urllib 스크립트. 31개 통과(등록·부분 수정·422·404·204, q·status·priority AND, q의 %·_ 글자 검색, 2000자 설명·이모지 저장).
  결과: 등록 행을 mariadb SELECT로 확인. API 재시작 후 같은 id·수정 내용 유지. 틀린 DB 비밀번호로 실행 시 /api/tasks 503, 로그에 비밀번호 미노출.
  테스트 항목([T11검증] 제목)은 확인 후 삭제해 tasks는 0행. AUTO_INCREMENT는 6부터 시작. 남은 오류 없음.
## 5장: 서버 분리
- [x] T12: DB 서버 구성 후 App 서버에서 SELECT 1 확인.
  기록(2026-10-14): 구성 방식은 WSL 하나에서 역할 분리(DB: MariaDB, App: uvicorn·T13 systemd, Web: Nginx·T14), 사용자 결정. 이 환경은 MariaDB 11.8.6(T09 기록의 10.6.23과 다름), .venv는 Python 3.14.4로 재생성, 패키지 버전은 requirements.txt와 일치.
  변경 파일: 없음(DB 서버 설정이 이미 요구에 맞음).
  실행: systemctl is-active/is-enabled mariadb, ss -ltn, .venv/bin/python으로 backend.database.engine에서 SELECT 1.
  결과: mariadb active·enabled. bind-address 127.0.0.1, 3306은 127.0.0.1에서만 LISTEN, WSL eth0 주소로는 연결 거부. App 경로(.venv → .env → backend.database)로 SELECT 1 → 1, CURRENT_USER task_flow_app@localhost, DATABASE task_flow, utf8mb4. 다른 작업 디렉터리에서도 접속. 권한은 task_flow.* ALL만.
  참고: tasks 테이블은 2026-10-14 09:57에 이 저장소 코드로 생성된 상태(status·priority ENUM, 0행). 서버를 실제로 나누면 bind-address를 사설 IP로, 사용자 호스트를 App 서버로 제한해야 함. T09 기록의 비밀번호 변경 권장은 DB가 127.0.0.1에만 열린 이번 구성에서는 보류. 남은 오류 없음.
- [x] T13: App 서버 코드·가상환경·환경변수·systemd 구성.
  확인: App에서 /api/health 응답.
  기록(2026-10-14): deploy/task-flow-api.service 추가(현재 계정 hjcha, 코드 ~/vibe-lab/flow-task, .venv Python 3.14.4, EnvironmentFile=.env, 127.0.0.1:8000, --reload 없음, Restart=on-failure, mariadb 이후 시작). 서비스 파일에 비밀번호 없음.
  실행: systemd-analyze verify(오류 없음) → 사용자가 sudo cp, daemon-reload, enable --now 실행.
  결과: task-flow-api active·enabled, User hjcha, 설치된 유닛과 저장소 파일 동일. 프로세스 환경에 DB_* 5개 존재. curl /api/health → {"status":"ok"}, /api/tasks 200, / 200, journalctl에 시작·요청 로그. 프로세스를 kill -9 하자 약 3초 뒤 새 PID로 자동 재시작(NRestarts=1), health 정상. 남은 오류 없음.
  참고: 서비스가 8000을 쓰므로 개발용 uvicorn --reload는 다른 포트로 실행하거나 서비스를 멈춘 뒤 실행. 코드 변경 후 sudo systemctl restart task-flow-api.
- [x] T14: Web 서버 Nginx와 정적 파일·/api 프록시 구성.
  확인: Web 주소로 등록, DB 저장, App 재시작 후 유지.
  기록(2026-10-14): deploy/nginx-task-flow.conf(80 포트, 정적 파일은 /var/www/task-flow, /api/만 127.0.0.1:8000으로 프록시, /docs 등 App의 다른 경로 비공개, 본문 64KB 제한, server_tokens off), deploy/deploy-web.sh(frontend/를 /var/www/task-flow로 동기화, 사이트 설정 설치, 기본 사이트 링크 제거, nginx -t 후 reload) 추가. www-data가 홈 디렉터리(750)를 읽지 못하므로 정적 파일은 복사해 배포.
  실행: 사용자가 sudo apt install -y nginx(1.28.3), sudo bash deploy/deploy-web.sh 실행.
  결과: 설치된 설정·정적 파일이 저장소와 동일. Web 주소(http://127.0.0.1) / · app.js · styles.css 200(Nginx가 직접 제공), /api/health·/api/tasks 200(프록시), /docs·/openapi.json·/.env·/backend/main.py 404, 70KB 요청 413. Web 주소로 POST → SQL SELECT로 행 확인 → PATCH → App 프로세스 재시작(systemd 자동 재시작, 새 PID) 후 목록 동일. Windows 쪽에서도 http://127.0.0.1 의 화면·API 200. 남은 오류 없음.
  참고: 검증용 행 "[T14검증] Nginx 경유 등록"(id 2)을 남겨 둠. 프런트엔드 변경 후에는 sudo bash deploy/deploy-web.sh, 백엔드 변경 후에는 sudo systemctl restart task-flow-api. 일반 사용자로 nginx -t를 실행하면 /run/nginx.pid 권한 오류가 나므로 sudo로 실행.
## 6장: 다중 사용자
결정(2026-10-14, 사용자): PRD 충돌 문구는 T15에서 정리, 로그인 상태는 서버 세션 + HttpOnly 쿠키, 로그인 ID는 아이디(username), 기존 할 일은 소유자 없이 남겨 두고 누구에게도 보이지 않게 한다(삭제·자동 이전 없음).
- [x] T15: PRD 정리와 인증 API 명세. PRD의 목적·사용자와 범위·데이터를 다중 사용자 기준으로 고치고, API-SPEC.md에 회원가입·로그인·로그아웃·현재 사용자 API, 아이디·비밀번호 규칙, 세션 쿠키·만료, 401·409 응답을 추가한다.
  확인: PRD·PLAN·API-SPEC 사이에 충돌 없음(사용자 확인).
  기록(2026-10-14): PRD.md — 목적·사용자와 범위를 다중 사용자 기준으로 수정(이전 단계는 기록으로 남김), 데이터에 user_id·사용자 항목과 기존 할 일 처리 추가, 완료 기준에 사용자 간 분리 추가, 추가 기능에 F10~F12 추가, 제외 기능 앞 공백 정리. API-SPEC.md — 401·409 상태 코드, 인증 규칙(아이디 ^[a-z0-9_]{3,30}$, 비밀번호 8~64자, scrypt 해시, 세션 쿠키 task_flow_session HttpOnly·SameSite=Lax·7일, 토큰 해시 저장), User 객체, POST /api/auth/signup(가입 후 바로 로그인)·login·logout, GET /api/auth/me, 할 일 API의 인증 규칙(비로그인 401, 다른 사용자 할 일 404), user_id 열 추가 계획.
  결과: 세 문서에서 '로그인 없음·단일 사용자' 문구는 이전 단계 기록으로만 남고, 세션 7일 등 값이 PRD·API-SPEC에서 일치. 2026-10-14 사용자 확인(가입 후 바로 로그인, 세션 7일, 아이디 대문자 거절, 제외 범위 포함).
- [ ] T16: users·sessions 테이블과 비밀번호 해시. backend/models.py에 사용자·세션 모델을 추가하고, 비밀번호는 표준 라이브러리 hashlib.scrypt로 솔트와 함께 해시해 저장한다. 세션은 추측할 수 없는 토큰을 쓰고 DB에는 토큰의 해시만 저장한다.
  확인: python -m backend.init_db 후 두 테이블 확인, 기존 tasks 테이블·행 변화 없음, 비밀번호·토큰 평문이 DB와 로그에 없음.
- [ ] T17: 인증 API. POST /api/auth/signup·login·logout, GET /api/auth/me를 구현한다. 로그인하면 HttpOnly·SameSite=Lax 세션 쿠키를 발급하고, 로그아웃하면 서버 세션을 지운다.
  확인: 가입 201, 중복 아이디 409, 입력 위반 422, 틀린 아이디·비밀번호 모두 같은 401, 로그인 후 /me 200, 로그아웃 후 /me 401, 응답에 비밀번호 해시 없음.
- [ ] T18: 할 일 소유자 적용. tasks에 user_id(NULL 허용, users 참조) 열을 추가하는 스크립트를 만들고(데이터 삭제·초기화 없음), /api/tasks의 조회·등록·수정·삭제·필터를 로그인 사용자의 할 일로 제한한다. 기존 행은 user_id가 비어 있어 누구에게도 보이지 않는다.
  확인: 비로그인 401, 사용자 A의 할 일을 B가 조회·수정·삭제하면 404, 검색·필터도 본인 것만, 기존 행 수 변화 없음.
- [ ] T19: 화면에 회원가입·로그인·로그아웃 추가. 로그인 전에는 할 일 화면을 숨기고, API가 401을 반환하면 로그인 화면으로 돌아간다.
  확인: 브라우저에서 두 사용자가 각각 등록한 목록이 서로 보이지 않음, 로그아웃 후 목록이 사라짐, 새로고침해도 로그인 유지, 사용자 입력은 글자로 표시.
- [ ] T20: 배포 반영. deploy-web.sh로 화면을, systemctl restart로 App을 갱신한다.
  확인: Web 주소(http://127.0.0.1)로 두 사용자 시나리오 통과, App 재시작 후 할 일과 로그인 상태 유지.
## 추가 작업
- [x] A01: App(8000)은 API만 제공하도록 FastAPI의 화면 파일 제공(StaticFiles) 제거(2026-10-14 사용자 요청, PLAN 외 작업). 화면은 Nginx(80)만 제공.
  확인: 8000에서 화면 경로 404·API 정상, Web 주소(80)의 화면·API 정상.
  기록(2026-10-14): backend/main.py에서 StaticFiles 마운트·FRONTEND_DIR 제거, API-SPEC.md 화면 제공 항목 수정.
  결과: 8001 포트 시험 서버에서 / · /index.html · /app.js · /styles.css 404, /api/health·/api/tasks 200, /docs·/openapi.json 200(OpenAPI 경로는 /api만), 등록 201·삭제 204. 사용자가 sudo systemctl restart task-flow-api 실행 후(11:40) 8000: 화면 경로 404, /api·/docs 200. 80(Nginx): 화면·/api 200, /docs 404, 웹 경유 등록 201·삭제 204. Windows에서 80은 200, 8000/는 404. 남은 오류 없음.
## 실행 기준
T01~T04: python3 -m http.server 5500 --bind 127.0.0.1 --directory frontend
T05~T11: 가상환경에서 python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
T12 이후: App은 systemd(task-flow-api, 127.0.0.1:8000), 화면은 Nginx(http://127.0.0.1). 백엔드 변경 후 sudo systemctl restart task-flow-api, 화면 변경 후 sudo bash deploy/deploy-web.sh. 개발 중 시험 실행은 다른 포트(예: 8001)를 쓴다.
실제 존재하는 파일을 확인한 뒤 명령을 실행한다.
## 기록
각 작업에 변경 파일, 실행 명령, 실제 확인 결과, 남은 오류를 기록한다.
정상 동작을 확인한 작업 단위로 Git 커밋한다.