import os
import json
import pymysql
import openai

DB_HOST     = os.getenv("DB_HOST", "localhost")
DB_PORT     = int(os.getenv("DB_PORT", 3306))
DB_USER     = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "123456")
DB_NAME     = os.getenv("DB_NAME", "flaskshop")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

FETCH_SQL = """
    SELECT id, description
      FROM product_product
     WHERE description IS NOT NULL
       AND (embeddings IS NULL OR JSON_LENGTH(embeddings) = 0)
"""

UPDATE_SQL = """
    UPDATE product_product
       SET embeddings = {embedding}
     WHERE id = {id}
"""

def get_embedding(text: str, model = "text-embedding-ada-002") -> list[float]:
    resp = openai.Embedding.create(
        model=model,
        input=text
    )
    return resp["data"][0]["embedding"]

def main():
    # 1. Connect to MySQL
    conn = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with conn.cursor() as cursor:
            cursor.execute(FETCH_SQL)
            rows = cursor.fetchall()

            for row in rows:
                prod_id = row["id"]
                desc    = row["description"].strip()
                if not desc:
                    continue

                embedding = get_embedding(desc)

                embedding_json = json.dumps(embedding)
                cursor.execute(UPDATE_SQL.format(embedding=embedding_json, id=prod_id))
                print(f"Updated product {prod_id} (len={len(embedding)})")

        conn.commit()
        print("All done.")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
