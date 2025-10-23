from app.core.config import get_settings
import sqlalchemy as sa
from sqlalchemy import text
from pathlib import Path

s = get_settings()
url = s.POSTGRES_URL.replace('+asyncpg','')
engine = sa.create_engine(url)
# determine head revision from alembic/versions newest file
versions = list((Path(__file__).resolve().parent.parent / 'alembic' / 'versions').glob('*.py'))
versions.sort(key=lambda p: p.stat().st_mtime)
head_rev = None
if versions:
    text_content = versions[-1].read_text(encoding='utf8')
    import re
    m = re.search(r"^revision\s*=\s*['\"]([^'\"]+)['\"]", text_content, re.M)
    if m:
        head_rev = m.group(1)

with engine.connect() as conn:
    conn = conn.execution_options(isolation_level='AUTOCOMMIT')
    # add column if missing
    res = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='user' AND column_name='dob'"))
    exists = bool(res.fetchone())
    if not exists:
        print('Adding dob column...')
        conn.execute(text("ALTER TABLE \"user\" ADD COLUMN dob VARCHAR(10);") )
    else:
        print('dob column already exists')
    # set alembic_version
    if head_rev:
        print('Setting alembic_version to', head_rev)
        conn.execute(text("CREATE TABLE IF NOT EXISTS alembic_version (version_num VARCHAR(32) NOT NULL);") )
        conn.execute(text("DELETE FROM alembic_version;"))
        conn.execute(text("INSERT INTO alembic_version (version_num) VALUES (:rev)"), {'rev': head_rev})
    else:
        print('Could not determine head revision file in alembic/versions')

print('Done')
