from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DB_FILE = Path(r"D:\PythonProjects\blank_projects\LangChain1.0Demo\database\sqllite_data\sqllite_test.db")

engine = create_engine(
    f'sqlite:///{DB_FILE}',
    connect_args={"check_same_thread": False}  # SQLite特有参数，解决线程安全问题
)

# 3. 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine,expire_on_commit= False)

# 4. 创建基类（用于定义数据模型）
Base = declarative_base()

# 5. 优化后的会话获取函数（生成器 + 确保关闭）
def get_local_session():
    db = SessionLocal()
    try:
        yield db  # 提供会话
    finally:
        db.close()  # 确保会话最终关闭


@contextmanager
def get_session():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()  # 出错时回滚
        raise e
    finally:
        db.close()  # 确保会话关闭

if __name__ == '__main__':
    pass