from app.core.config import get_settings
import sqlalchemy as sa
from sqlalchemy import text

s = get_settings()
url = s.POSTGRES_URL.replace('+asyncpg','')
engine = sa.create_engine(url)
with engine.connect() as conn:
    conn = conn.execution_options(isolation_level='AUTOCOMMIT')
    # create table if not exists
    try:
        conn.execute(text("CREATE TABLE IF NOT EXISTS alembic_version (version_num VARCHAR(32) NOT NULL);"))
        conn.execute(text("DELETE FROM alembic_version;"))
        conn.execute(text("INSERT INTO alembic_version (version_num) VALUES ('04261a04e3fc');"))
        print('alembic_version table ensured and set to 04261a04e3fc')
    except Exception as e:
        print('failed to ensure alembic_version:', e)
        raise
