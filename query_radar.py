import sqlite3
import pandas as pd

def query_radar():
    conn = sqlite3.connect("radar.db")
    
    # Consulta de Oportunidades
    query = """
    SELECT 
        c.product_name, 
        c.keyword, 
        c.url,
        s.money_score, 
        s.competition_score, 
        s.pain_score, 
        s.explanation
    FROM candidates c 
    JOIN scores s ON c.id = s.candidate_id 
    ORDER BY s.total_score DESC, s.money_score DESC
    LIMIT 20;
    """
    
    try:
        df = pd.read_sql_query(query, conn)
        if df.empty:
            print("No high-potential opportunities found yet.")
        else:
            print("\n----- TOP 20 BUSINESS OPPORTUNITIES -----\n")
            print(df.to_string(index=False))
            
            # Additional analysis for "High Ticket & Low Competition"
            print("\n----- REUSABLE SAAS CONCEPTS (3-DAY BUILD) -----\n")
            high_ticket = df[
                (df['money_score'] > 7) & 
                (df['competition_score'] < 5) & 
                (df['pain_score'] > 6)
            ]
            
            if not high_ticket.empty:
                print(high_ticket[['product_name', 'keyword', 'explanation']].to_string(index=False))
            else:
                print("No perfect matches for High Ticket/Low Competition yet. Generating creative pivots...")

    except Exception as e:
        print(f"Error querying DB: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    query_radar()
