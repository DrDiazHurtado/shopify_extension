import sqlite3
import pandas as pd

def export_to_csv():
    conn = sqlite3.connect("radar.db")
    query = """
    SELECT 
        c.product_name, 
        c.keyword, 
        c.url, 
        s.money_score, 
        s.demand_score, 
        s.competition_score, 
        s.pain_score, 
        s.total_score, 
        s.explanation
    FROM candidates c 
    LEFT JOIN scores s ON c.id = s.candidate_id
    ORDER BY s.total_score DESC;
    """
    
    try:
        df = pd.read_sql_query(query, conn)
        df.to_csv("saas_opportunities_export.csv", index=False)
        print(f"✅ Exported {len(df)} opportunities to saas_opportunities_export.csv")
    except Exception as e:
        print(f"❌ Error exporting CSV: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    export_to_csv()
