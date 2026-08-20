import sqlite3
import json

conn = sqlite3.connect('data/db.sqlite')
conn.row_factory = sqlite3.Row
c = conn.cursor()

for table in ['documents', 'classifications', 'hesitation_tags', 'factor_mentions', 'unmet_needs', 'question_mappings']:
    sample = c.execute(f"SELECT * FROM {table} LIMIT 1").fetchone()
    if sample:
        print(f"\n=== Table: {table} ===")
        print("Columns:", list(sample.keys()))
        print("Sample row:", dict(sample))

