import openai
from shop_agents.database import database


def generate_embedding(text, model="text-embedding-ada-002"):
    response = openai.Embedding.create(
        input=text,
        model=model
    )
    return response["data"][0]["embedding"]



def rag(query_text, columns_to_retrieve, table_name='product_product', custom_filters=None, top_k=10, threshold=0.75):
    query_embedding = generate_embedding(query_text)

    selected_columns = ", ".join(columns_to_retrieve)

    filter_clause = f"AND {custom_filters}" if custom_filters else ""

    with database.create_session() as session:
        sql_query = f"""
            SELECT {selected_columns}, 
                    cosine_similarity(embedding, {query_embedding}) 
                    as similarity_score
            FROM {table_name}
            WHERE cosine_similarity(embedding, {query_embedding}) >= {threshold}
            {filter_clause}
            ORDER BY similarity_score DESC LIMIT {top_k}
        """

        result = session.execute(
            sql_query,
        )
        return [dict(row) for row in result]