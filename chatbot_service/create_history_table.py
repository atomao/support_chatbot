from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from shop_agents.settings import DBConfig


def create_chatbot_history_table(config: DBConfig):
    """
    Connects to the database specified in config.db_uri and
    creates a `chatbot_history` table for logging conversation turns.
    """
    ddl = """
    CREATE TABLE IF NOT EXISTS chatbot_history (
      id BIGINT AUTO_INCREMENT PRIMARY KEY,
      session_id VARCHAR(100) NOT NULL,
      user_id BIGINT,
      role ENUM('system','user','assistant') NOT NULL,
      message TEXT NOT NULL,
      embedding JSON,
      token_count INT,
      response_time_ms INT,
      metadata JSON,
      created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """

    engine = create_engine(config.db_uri, echo=False, future=True)
    try:
        with engine.begin() as conn:
            conn.execute(text(ddl))
        print("Chatbot_history table is ready.")
    except SQLAlchemyError as e:
        print("Error creating table:", e)


if __name__ == "__main__":

    config = DBConfig()
    create_chatbot_history_table(config)
