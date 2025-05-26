from agents import Agent, function_tool
from pydantic import BaseModel
import json
import logging
import time
import random
import pandas as pd
import os
from shop_agents.database import database
from shop_agents.settings import Config
from shop_agents.embedding_search import rag

logger = logging.getLogger(__name__)


@function_tool
def get_products(query_message: str, 
                 columns_to_retrieve: list[str] = ['title', 'description', 'author'],
                 filter_clause: str | None = None):
    """General search for products 
    query_message: str - paraphrased user message that should describe product
    columns_to_retrieve: list[str] = ['title', 'description', 'author'] - which columns to retrieve 
    from all columns(described below)
    filter_clause: str | None = None - use this argument if user want filtering for example on sale or books count , rating etc
    
    Products table columns descritpion so that you can create columns_to_retrieve, filter_clause.

    +-------------------+-----------------+------+
    | Field             | Type            | Null |
    +-------------------+-----------------+------+
    | title             | varchar(255)    | NO   |
    | on_sale           | tinyint(1)      | YES  |
    | rating            | decimal(8,2)    | YES  |
    | sold_count        | int             | YES  |
    | review_count      | int             | YES  |
    | basic_price       | decimal(10,2)   | YES  |
    | category_id       | int             | YES  |
    | is_featured       | tinyint(1)      | YES  |
    | product_type_id   | int             | YES  |
    | attributes        | json            | YES  |
    | description       | text            | YES  |
    | id                | int             | NO   |
    | created_at        | datetime        | YES  |
    | updated_at        | datetime        | YES  |
    | embedding         | vector          | YES  |
    +-------------------+-----------------+------+

    """
    data = rag(query_text=query_message, 
               columns_to_retrieve=columns_to_retrieve, 
               table_name='product_product', 
               threshold=0.8,
               custom_filters=filter_clause)
    return data


@function_tool
def get_user_cart_info(user_id: int):
    """Retrieve current cart contents for a given user
    user_id: int - unique identifier of the user
    """
    with database.create_session() as session:
        sql_query = f"""
            SELECT product_id, title, quantity, price, description
            FROM cart_items
            WHERE user_id = {user_id}
        """
        result = session.execute(sql_query).fetchall()
        return [dict(row) for row in result]



@function_tool
def search_in_faq(user_faq_question: str, 
                  columns_to_retrieve: list[str] = ['question', 'answer'],
                  top_k: int = 5):
    """Semantic FAQ search
    user_faq_question: str - question from user in free form related to store, support, about, etc.
    columns_to_retrieve: list[str] = ['question', 'answer'] - which columns to retrieve 
    from all columns (described below)

    FAQ table columns description so that you can create columns_to_retrieve.

    +-------------+---------+------+
    | Field       | Type    | Null |
    +-------------+---------+------+
    | question    | text    | YES  |
    | answer      | text    | YES  |
    | embedding   | vector  | YES  |
    +-------------+---------+------+
    """
    data = rag(query_text=user_faq_question, 
               columns_to_retrieve=columns_to_retrieve, 
               table_name='faq', 
               threshold=0.82,
               top_k=top_k)
    return data

@function_tool
def submit_ticket(user_ticket_message: str, email: str) -> str:
    """Submit a user ticket to Excel file
    user_ticket_message: str - content of the ticket
    email: str - user's email address
    """
    file_path = Config.TicketsExcel


    if os.path.exists(file_path):
        df = pd.read_excel(file_path)
    else:
        df = pd.DataFrame(columns=["User Ticket", "Email"])

    new_row = {"User Ticket": user_ticket_message, "Email": email}
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    df.to_excel(file_path, index=False)

    return "Ticket submitted successfully"

