import duckdb
import subprocess
import json
from datetime import datetime

con = duckdb.connect("mensa.duckdb")

con.execute("""
CREATE TABLE IF NOT EXISTS meals (
    id TEXT,
    menuLine TEXT,
    menuDate DATE,
    studentPrice TEXT,
    guestPrice TEXT,
    pupilPrice TEXT,
    menu TEXT[],
    meats TEXT[],
    icons TEXT[],
    allergens TEXT[],
    additives TEXT[],
    importedAt TIMESTAMP
)
""")

def fetch_cli_data(offset: int):
    """Calls the CLI with day offset and returns parsed JSON list"""
    result = subprocess.run(
        ["python", "mensa.py", "--raw", "-d", f"+{offset}"],
        capture_output=True,
        text=True,
        check=True
    )
    return json.loads(result.stdout)

def insert_data(meals, imported_at):
    for meal in meals:
        con.execute("""
            INSERT INTO meals VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            meal.get("id"),
            meal.get("menuLine"),
            meal.get("menuDate"),
            meal.get("studentPrice"),
            meal.get("guestPrice"),
            meal.get("pupilPrice"),
            meal.get("menu", []),
            meal.get("meats", []),
            meal.get("icons", []),
            meal.get("allergens", []),
            meal.get("additives", []),
            imported_at
        ))

# Fetch for next 7 days
now = datetime.now()
total_inserted = 0

for offset in range(8):
    data = fetch_cli_data(offset)
    insert_data(data, now)
    total_inserted += len(data)
    print(f"[Info] Inserted {len(data)} meals for +{offset} days")

print(f"\nDone. {total_inserted} meals saved to DuckDB.")
