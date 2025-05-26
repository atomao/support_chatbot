

from typing import List, Literal, TypedDict, Optional
from sqlalchemy import (
    create_engine, Column, BigInteger, Integer, Text, Enum, JSON,
    DateTime, String, func
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from shop_agents.settings import DBConfig
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Generator


Base = declarative_base()

class ChatbotHistory(Base):
    __tablename__ = 'chatbot_history'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(String(100), nullable=False, index=True)
    user_id = Column(BigInteger, nullable=True)
    role = Column(Enum('system', 'user', 'assistant', name='role_enum'), nullable=False)
    message = Column(Text, nullable=False)
    embedding = Column(JSON, nullable=True)
    token_count = Column(Integer, nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)



class MysqlDatabase:
    def __init__(self, config: DBConfig):
        self._engine = create_engine(config.db_uri, future=True)
        self._SessionLocal = sessionmaker(
            bind=self._engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
            future=True,
        )

    @contextmanager
    def create_session(self) -> Generator["Session", None, None]:
        session = self._SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

class Message(TypedDict):
    role: Literal['system', 'user', 'assistant']
    content: str

class HistoryClient:
    def __init__(self, config: DBConfig):
        self.engine = create_engine(config.db_uri, future=True)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False)

    def add_message(
        self,
        session_id: str,
        role: Literal['system', 'user', 'assistant'],
        content: str,
        user_id: Optional[int] = None,
        embedding: Optional[list] = None,
        token_count: Optional[int] = None,
        response_time_ms: Optional[int] = None,
        metadata: Optional[dict] = None,
    ) -> None:
        db: Session = self.SessionLocal()
        try:
            record = ChatbotHistory(
                session_id=session_id,
                user_id=user_id,
                role=role,
                message=content,
                embedding=embedding,
                token_count=token_count,
                response_time_ms=response_time_ms,
                metadata=metadata,
            )
            db.add(record)
            db.commit()
        except SQLAlchemyError:
            db.rollback()
            raise
        finally:
            db.close()

    def add_user_message(self, session_id: str, content: str, **kw) -> None:
        self.add_message(session_id, 'user', content, **kw)

    def add_assistant_message(self, session_id: str, content: str, **kw) -> None:
        self.add_message(session_id, 'assistant', content, **kw)

    def add_system_message(self, session_id: str, content: str, **kw) -> None:
        self.add_message(session_id, 'system', content, **kw)

    def get_history(self, session_id: str) -> List[Message]:
        """
        Retrieves all messages for a session, ordered by creation time.
        """
        db: Session = self.SessionLocal()
        try:
            rows = (
                db.query(ChatbotHistory)
                  .filter(ChatbotHistory.session_id == session_id)
                  .order_by(ChatbotHistory.created_at)
                  .all()
            )
            return [
                Message(
                    role=row.role,
                    content=row.message,
                    created_at=row.created_at.isoformat()
                )
                for row in rows
            ]
        finally:
            db.close()


cfg = DBConfig()
database = MysqlDatabase(cfg)
history = HistoryClient(database)
