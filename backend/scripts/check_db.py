from app.core.config import get_settings
import sqlalchemy as sa
from sqlalchemy import text
import os

s = get_settings()
print('POSTGRES_URL=', s.POSTGRES_URL)
url = s.POSTGRES_URL.replace('+asyncpg', '')
engine = sa.create_engine(url)
with engine.connect() as conn:
    try:
        rows = conn.execute(text('select * from alembic_version')).fetchall()
        print('alembic_version rows:', rows)
    except Exception as e:
        print('alembic_version read error:', e)
    try:
        tables = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public' order by tablename"))
        print('tables:', [r[0] for r in tables.fetchall()])
    except Exception as e:
        print('tables read error:', e)
    try:
        col = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='user' AND column_name='dob'"))
        print('user.dob exists:', bool(col.fetchall()))
    except Exception as e:
        print('column check error:', e)
print('done')
