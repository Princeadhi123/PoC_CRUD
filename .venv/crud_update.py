import psycopg2
from psycopg2 import sql
import json
from config import DB_CONFIG

# Extract database connection details from the configuration
db_config = DB_CONFIG

# Establish a connection
connection = psycopg2.connect(
    host=db_config['host'],
    port=db_config['port'],
    database=db_config['database'],
    user=db_config['user'],
    password=db_config['password']
)

# Create a cursor
cursor = connection.cursor()

# Update query
update_query = """
    UPDATE articles
    SET title = %s, keywords = %s
    WHERE id = %s
"""

# Example values for update
new_title = "Updated Article Title"
new_keywords = "updatedKeyword1 updatedKeyword2"
article_id_to_update = 1  # Replace with the specific article ID you want to update

# Execute the update query
cursor.execute(update_query, (new_title, new_keywords, article_id_to_update))

# Commit the changes
connection.commit()

# Execute a query to fetch the updated data
select_query = """
    SELECT
        articles.id,
        articles.filename,
        articles.source_url,
        articles.title,
        articles.author,
        articles.is_copyrighted,
        articles.keywords,
        articles.created_at,
        articles.updated_at,
        article_generated_qna.id AS qna_id,
        article_generated_qna.question,
        article_generated_qna.answer,
        article_generated_qna.paragraph,
        article_generated_qna.is_user_edited,
        article_generated_qna.created_at AS qna_created_at,
        article_generated_qna.updated_at AS qna_updated_at
    FROM
        articles
    LEFT JOIN
        article_generated_qna ON articles.id = article_generated_qna.article_id
"""
cursor.execute(select_query)

# Fetch all the rows
rows = cursor.fetchall()

# Close the cursor and connection
cursor.close()
connection.close()

# Create the desired JSON structure
data = []
current_article = None

for row in rows:
    article_id, filename, source_url, title, author, is_copyrighted, keywords, created_at, updated_at, qna_id, question, answer, paragraph, is_user_edited, qna_created_at, qna_updated_at = row

    if current_article is None or current_article['id'] != article_id:
        if current_article is not None:
            data.append(current_article)
        current_article = {
            "id": str(article_id),
            "filename": filename,
            "sourceUrl": source_url,
            "title": title,
            "author": author,
            "isCopyrighted": is_copyrighted,
            "articleGeneratedQna": [],
            "keywords": keywords,
            "createdAt": str(created_at),
            "updatedAt": str(updated_at)
        }

    if qna_id is not None:
        current_article['articleGeneratedQna'].append({
            "id": str(qna_id),
            "question": question,
            "answer": answer,
            "paragraph": paragraph,
            "isUserEdited": is_user_edited,
            "createdAt": str(qna_created_at),
            "updatedAt": str(qna_updated_at)
        })

# Append the last article
if current_article is not None:
    data.append(current_article)

# Create the final JSON
result_json = {"data": data}

# Print or use the result_json as needed
print(json.dumps(result_json, indent=2))
