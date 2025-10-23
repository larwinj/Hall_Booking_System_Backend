from app.core.config import get_settings
import sqlalchemy as sa
from sqlalchemy import text
s = get_settings()
url = s.POSTGRES_URL.replace('+asyncpg','')
engine = sa.create_engine(url)
with engine.connect() as conn:
    conn = conn.execution_options(isolation_level='AUTOCOMMIT')
    r = conn.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name='user' ORDER BY ordinal_position"))
    for row in r.fetchall():
        print(row)
