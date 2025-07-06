import duckdb
from datetime import date

con = duckdb.connect("mensa.duckdb")

# Dein Ziel-Datum
menu_date = date(2025, 7, 8)

# Alle Einträge zu dem Tag, sortiert nach ID und Zeit
rows = con.execute("""
SELECT id, menuLine, studentPrice, guestPrice, menu, icons, allergens, importedAt
FROM meals
WHERE menuDate = ?
ORDER BY id, importedAt
""", (menu_date,)).fetchall()

from collections import defaultdict
import pprint

# Gruppieren nach id + datum
grouped = defaultdict(list)
for row in rows:
    key = (row[0], menu_date)  # row[0] = id
    grouped[key].append(row)

pp = pprint.PrettyPrinter(indent=2)

# Änderungen pro Gericht anzeigen
for id_, versions in grouped.items():
    print(f"\n🔍 Änderungen für Gericht ID {id_} ({versions[0][1]}):")

    prev = None
    for v in versions:
        if prev is None:
            print(f"🕒 {v[-1]} → Erste Version")
            prev = v
            continue

        changes = []
        fields = ['studentPrice', 'guestPrice', 'menu', 'icons', 'allergens']
        for i, field in enumerate(fields, start=2):
            if prev[i] != v[i]:
                changes.append((field, prev[i], v[i]))

        if changes:
            print(f"🕒 {v[-1]} → Änderungen:")
            for f, old, new in changes:
                print(f"   - {f}: '{old}' → '{new}'")
        else:
            print(f"🕒 {v[-1]} → Keine Änderungen")

        prev = v
