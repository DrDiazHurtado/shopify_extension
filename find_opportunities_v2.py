import sqlite3
import pandas as pd

conn = sqlite3.connect("/home/noorm/Escritorio/SAAS_v2/radar.db")
print("Top Scored Candidates:")
query = """
SELECT c.name, c.url, s.total_score, s.money_score, s.demand_score, s.competition_score, s.pain_score
FROM candidates c
JOIN scores s ON c.id = s.candidate_id
ORDER BY s.total_score DESC
LIMIT 20
"""
df = pd.read_sql_query(query, conn)
print(df.to_string())

print("\nHigh Pain Candidates (Gap in market):")
query_pain = """
SELECT c.name, s.pain_score, s.demand_score, c.url
FROM candidates c
JOIN scores s ON c.id = s.candidate_id
WHERE s.pain_score > 5
ORDER BY s.pain_score DESC
LIMIT 10
"""
df_pain = pd.read_sql_query(query_pain, conn)
print(df_pain.to_string())

conn.close()
