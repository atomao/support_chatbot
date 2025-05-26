import os


class Config:
    user = os.getenv("DB_USER", "root")
    passwd = os.getenv("DB_PASSWD", "123456")
    host = os.getenv("DB_HOST", "127.0.0.1")
    port = os.getenv("DB_PORT", 3306)
    db_name = os.getenv("DB_NAME", "flaskshop")
    db_uri = (
        f"mysql+pymysql://{user}:{passwd}@{host}:{port}/{db_name}?charset=utf8mb4"
    )

    TicketsExcel = "../tickets.xlsx"

