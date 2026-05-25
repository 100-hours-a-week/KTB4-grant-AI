from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql+psycopg://kks@localhost:5432/community" # postgresql+psycopg://<유저>:<비밀번호>@<호스트>:<포트>/<DB이름>
engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    result = conn.execute(text("SELECT 1"))
    print((result.scalar()))