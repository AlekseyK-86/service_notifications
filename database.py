import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

# Загружаем переменные из .env
load_dotenv()

# Получаем данные из окружения
DB_USER = os.getenv("DB_USER")
if not DB_USER:
    raise ValueError("DB_USER не найден в переменных окружения")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# Формируем URL подключения (для PostgreSQL)
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Создаем движок (Engine)
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=10,
    max_overflow=20
)

# Создаем фабрику сессий
AsyncSessionLocal = async_sessionmaker(expire_on_commit=False, bind=engine)


# Базовый класс для моделей
class Base(DeclarativeBase):
    pass


# Функция (Dependency) для получения сессии в эндпоинтах FastAPI
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
