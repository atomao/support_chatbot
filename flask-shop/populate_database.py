
import json
from datetime import datetime
import mysql.connector

DB = dict(
    host="localhost",
    user="root",
    password="123456",
    database="flaskshop",
)


def ensure_attr_value(cur, attr_title, value_title):
    """Return id of value_title under attribute attr_title, inserting if needed"""
    cur.execute("SELECT id FROM product_attribute WHERE title=%s", (attr_title,))
    attr_id = cur.fetchone()["id"]

    cur.execute(
        "SELECT id FROM product_attribute_value "
        "WHERE title=%s AND attribute_id=%s",
        (value_title, attr_id),
    )
    row = cur.fetchone()
    if row:
        return row["id"]

    now = datetime.now()
    cur.execute(
        "INSERT INTO product_attribute_value "
        "(title, attribute_id, created_at, updated_at) "
        "VALUES (%s, %s, %s, %s)",
        (value_title, attr_id, now, now),
    )
    return cur.lastrowid


def rewrite_product(cur, book):
    pid = book["rewrite_mapped_id"]
    now = datetime.now()

    # attribute values → ids
    publisher_id = ensure_attr_value(cur, "Publisher", book["publisher"])
    author_id    = ensure_attr_value(cur, "Author",    book["author"])
    lang_id      = ensure_attr_value(cur, "Language",  book["language"])
    attrs_json   = json.dumps(
        {"publisher": publisher_id, "author": author_id, "language": lang_id}
    )

    # update product_product
    cur.execute(
        """
        UPDATE product_product
           SET title=%s,
               on_sale=%s,
               rating=%s,
               sold_count=%s,
               review_count=%s,
               basic_price=%s,
               category_id=%s,
               is_featured=%s,
               product_type_id=%s,
               attributes=%s,
               description=%s,
               updated_at=%s
         WHERE id=%s
        """,
        (
            book["title"],
            book["on_sale"],
            book["rating"],
            book["sold_count"],
            book["review_count"],
            book["basic_price"],
            book["category_id"],
            book["is_featured"],
            book["product_type_id"],
            attrs_json,
            book["description"],
            now,
            pid,
        ),
    )


    cur.execute("SELECT id FROM product_image WHERE product_id=%s LIMIT 1", (pid,))
    row = cur.fetchone()
    if row:
        cur.execute(
            "UPDATE product_image SET image=%s, updated_at=%s WHERE id=%s",
            (book["image_path"], now, row["id"]),
        )
    else:
        cur.execute(
            "INSERT INTO product_image "
            "(image, product_id, created_at, updated_at) "
            "VALUES (%s, %s, %s, %s)",
            (book["image_path"], pid, now, now),
        )

    print(f"✔ rewrote product #{pid} – {book['title']}")


def main():
    with open("books_to_update.json", encoding="utf-8") as f:
        books = json.load(f)

    conn = mysql.connector.connect(**DB)
    cur = conn.cursor(dictionary=True)

    for book in books:
        rewrite_product(cur, book)

    conn.commit()
    cur.close()
    conn.close()
    print("Done.")

if __name__ == "__main__":
    main()
