import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
print("Connecting to:", DATABASE_URL)

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        result = connection.execute(text("SELECT version();"))
        for row in result:
            print("✅ Connected successfully!")
            print("PostgreSQL version:", row[0])
except Exception as e:
    print("❌ Connection failed:")
    print(e)