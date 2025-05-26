import os
import pymysql

DB_HOST     = os.getenv("DB_HOST", "localhost")
DB_PORT     = int(os.getenv("DB_PORT", 3306))
DB_USER     = os.getenv("DB_USER", "your_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "your_password")
DB_NAME     = os.getenv("DB_NAME", "your_database")


### As mysql do not have cosine_similarity function then I will create this sql function
FUNCTIONS_SQL = """
DELIMITER $$

CREATE FUNCTION vector_norm(vector JSON)
RETURNS DOUBLE
READS SQL DATA
DETERMINISTIC
BEGIN
  DECLARE array_length INT;
  DECLARE retval DOUBLE;
  DECLARE cell_value DOUBLE;
  DECLARE idx INT DEFAULT 0;

  SET array_length = JSON_LENGTH(vector);
  SET retval = 0.0;

  WHILE idx < array_length DO
    SET cell_value = JSON_EXTRACT(vector, CONCAT('$[', idx, ']'));
    SET retval = retval + POW(cell_value, 2);
    SET idx = idx + 1;
  END WHILE;

  RETURN SQRT(retval);
END$$

CREATE FUNCTION dot_product(vector1 JSON, vector2 JSON)
RETURNS DOUBLE
READS SQL DATA
DETERMINISTIC
BEGIN
  DECLARE array_length INT;
  DECLARE retval DOUBLE;
  DECLARE v1 DOUBLE;
  DECLARE v2 DOUBLE;
  DECLARE idx INT DEFAULT 0;

  SET array_length = JSON_LENGTH(vector1);
  SET retval = 0.0;

  WHILE idx < array_length DO
    SET v1 = JSON_EXTRACT(vector1, CONCAT('$[', idx, ']'));
    SET v2 = JSON_EXTRACT(vector2, CONCAT('$[', idx, ']'));
    SET retval = retval + v1 * v2;
    SET idx = idx + 1;
  END WHILE;

  RETURN retval;
END$$

CREATE FUNCTION cosine_similarity(vector1 JSON, vector2 JSON)
RETURNS DOUBLE
READS SQL DATA
DETERMINISTIC
BEGIN
  RETURN dot_product(vector1, vector2)
         / (vector_norm(vector1) * vector_norm(vector2));
END$$

DELIMITER ;
"""

ALTER_TABLE_SQL = """
ALTER TABLE product_product
  ADD COLUMN embedding JSON NULL
;
"""

def main():
    conn = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        client_flag=pymysql.constants.CLIENT.MULTI_STATEMENTS
    )
    try:
        with conn.cursor() as cursor:
            print("Creating vector_norm, dot_product, cosine_similarity functions...")
            for stmt in FUNCTIONS_SQL.strip().split("DELIMITER ;"):
                if stmt.strip():
                    cursor.execute(stmt)
            print("Altering product_product to add embeddings column...")
            cursor.execute(ALTER_TABLE_SQL)
        conn.commit()
        print("Done.")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
