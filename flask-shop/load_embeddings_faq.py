import os
import json
import pymysql
import openai
from load_embeddings_product import get_embedding


DB_HOST       = os.getenv("DB_HOST", "localhost")
DB_PORT       = int(os.getenv("DB_PORT", 3306))
DB_USER       = os.getenv("DB_USER", "your_user")
DB_PASSWORD   = os.getenv("DB_PASSWORD", "your_password")
DB_NAME       = os.getenv("DB_NAME", "your_database")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  
openai.api_key = OPENAI_API_KEY

INSERT_SQL = """
    INSERT INTO faq (id, question, answer, embeddings)
    VALUES (%s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
      question   = VALUES(question),
      answer     = VALUES(answer),
      embeddings = VALUES(embeddings)
"""


def main():
    with open("faq_to_upload.json", "r", encoding="utf-8") as f:
        faq_list = json.load(f)['faqs']
        for idx, faq in enumerate(faq_list):
            faq['id'] = idx
            
    conn = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.Cursor
    )

    try:
        with conn.cursor() as cursor:
            for item in faq_list:
                qid  = item["id"]
                q    = item["question"].strip()
                a    = item["answer"].strip()

                if not q:
                    continue

                emb = get_embedding(q)
                emb_json = json.dumps(emb)

                cursor.execute(INSERT_SQL, (qid, q, a, emb_json))
                print(f"[+] Upserted FAQ id={qid}")

        conn.commit()
        print("Finished inserting all FAQ entries.")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
