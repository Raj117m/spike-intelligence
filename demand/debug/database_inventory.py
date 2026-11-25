import duckdb

con = duckdb.connect("data/demand.duckdb")

print("\n=== TABLES ===\n")

tables = con.execute("SHOW TABLES").fetchall()

for table in tables:
    print(table[0])

print("\n=== SCHEMAS ===\n")

for table in tables:

    name = table[0]

    print("=" * 80)
    print(name)

    print(
        con.execute(
            f"DESCRIBE {name}"
        ).fetchdf()
    )

    print()
