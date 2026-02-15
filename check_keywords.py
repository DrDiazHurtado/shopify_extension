import sqlite3
import pandas as pd

def query_keywords():
    conn = sqlite3.connect("radar.db")
    try:
        # Check active keywords (candidates count per keyword)
        keyword_counts = pd.read_sql_query("SELECT keyword, count(*) as count FROM candidates GROUP BY keyword ORDER BY count DESC LIMIT 10;", conn)
        print("\n----- TOP ACTIVE SEARCH TERMS -----\n")
        print(keyword_counts.to_string(index=False))
        
        # Check total number of candidates
        total = pd.read_sql_query("SELECT count(*) as total FROM candidates;", conn).iloc[0]['total']
        print(f"\nTotal Candidates Analyzed: {total}\n")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    query_keywords()
