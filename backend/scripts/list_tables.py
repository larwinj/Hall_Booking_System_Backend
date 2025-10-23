from app.core.config import get_settings
import sqlalchemy as sa
from sqlalchemy import text
s = get_settings()
url = s.POSTGRES_URL.replace('+asyncpg','')
engine = sa.create_engine(url)
with engine.connect() as conn:
    conn = conn.execution_options(isolation_level='AUTOCOMMIT')
    try:
        res = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename"))
        tables = [r[0] for r in res.fetchall()]
        print('tables:', tables)
    except Exception as e:
        print('error listing tables:', e)
    try:
        rv = conn.execute(text('select * from alembic_version')).fetchall()
        print('alembic_version rows:', rv)
    except Exception as e:
        print('alembic_version read err:', e)
