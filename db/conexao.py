"""
Módulo de conexão com o banco de dados PostgreSQL.
Usa SQLAlchemy (engine) para consultas com pandas e
psycopg2 (via SQLAlchemy) para execução de comandos.
"""

from sqlalchemy import create_engine

DB_USER = "postgres"
DB_PASSWORD = "123456"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "monitoramento_saude"

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# Engine único, reutilizado por toda a aplicação
engine = create_engine(DATABASE_URL)


def get_engine():
    """Retorna o engine SQLAlchemy compartilhado."""
    return engine
