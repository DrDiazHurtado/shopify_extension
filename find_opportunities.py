import sqlite3
import pandas as pd

conn = sqlite3.connect("/home/noorm/Escritorio/SAAS_v2/radar.db")
print("Top Demand Results (More than 10k users):")
df = pd.read_sql_query("SELECT title, users, rating, reviews, pricing, keyword FROM search_results ORDER BY users DESC LIMIT 20", conn)
print(df.to_string())

print("\nTop Pain Results (Low rating with many reviews):")
df_pain = pd.read_sql_query("SELECT title, users, rating, reviews, pricing, keyword FROM search_results WHERE reviews > 50 AND rating < 4.0 ORDER BY rating ASC LIMIT 20", conn)
print(df_pain.to_string())

conn.close()
