from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import inspect, text
from app.core.config import get_settings
from app.db.base import *  
from app.db.base_class import Base
import logging

settings = get_settings()
engine = create_async_engine(settings.POSTGRES_URL, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)

async def init_db():
    async with engine.begin() as conn:
        # Get all tables from metadata
        metadata_tables = Base.metadata.tables
        
        for table_name, table in metadata_tables.items():
            quoted_table = f'"{table_name}"'  
            
            # Check if table exists and create if it doesn't
            exists = await conn.run_sync(
                lambda sync_conn: sync_conn.dialect.has_table(sync_conn, table_name)
            )
            
            if not exists:
                await conn.run_sync(lambda x: table.create(x))
                logging.info(f"Created new table: {table_name}")
                continue
            
            # Get existing columns
            existing_columns = await conn.run_sync(
                lambda sync_conn: {
                    col["name"]: col 
                    for col in inspect(sync_conn).get_columns(table_name)
                }
            )
            
            # Get a list of columns that exist in database but not in model
            columns_to_drop = set(existing_columns.keys()) - {col.name for col in table.columns}
            
            # Drop columns that are not in the model anymore
            for col_name in columns_to_drop:
                drop_stmt = f'ALTER TABLE {quoted_table} DROP COLUMN "{col_name}"'
                await conn.execute(text(drop_stmt))
                logging.info(f"Dropped column {col_name} from table {table_name}")
            
            # Check each column in the model
            for column in table.columns:
                if column.name not in existing_columns:
                    # Add new column
                    column_type = column.type.compile(dialect=engine.dialect)
                    nullable_str = "" if column.nullable else " NOT NULL"
                    
                    # Handle default values properly
                    if column.default is not None and column.default.arg is not None:
                        if isinstance(column.default.arg, str):
                            default = f" DEFAULT '{column.default.arg}'"
                        elif isinstance(column.default.arg, bool):
                            default = f" DEFAULT {str(column.default.arg).lower()}"
                        else:
                            default = f" DEFAULT {column.default.arg}"
                    else:
                        default = ""
                    
                    alter_stmt = f'ALTER TABLE {quoted_table} ADD COLUMN "{column.name}" {column_type}{nullable_str}{default}'
                    await conn.execute(text(alter_stmt))
                    logging.info(f"Added new column {column.name} to table {table_name}")

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
