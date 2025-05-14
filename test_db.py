import os
import time
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get database URL from environment
database_url = os.environ.get("DATABASE_URL")

def test_connection():
    if not database_url:
        print("No DATABASE_URL found in environment variables.")
        print("Available environment variables:")
        for key, value in os.environ.items():
            if not key.startswith("REPL"):
                print(f"  {key}")
        return False
    
    print(f"Attempting to connect to database using URL: {database_url}")
    
    try:
        # Attempt to establish a connection
        conn = psycopg2.connect(database_url)
        
        # Create a cursor
        cur = conn.cursor()
        
        # Execute a simple test query
        cur.execute("SELECT version();")
        
        # Fetch the result
        version = cur.fetchone()
        print(f"Successfully connected to PostgreSQL database!")
        print(f"PostgreSQL version: {version[0]}")
        
        # Close cursor and connection
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return False

if __name__ == "__main__":
    # Try connecting a few times with some delay between attempts
    for attempt in range(3):
        print(f"Connection attempt {attempt + 1}/3...")
        if test_connection():
            break
        else:
            print("Connection failed. Waiting 5 seconds before retrying...")
            time.sleep(5)