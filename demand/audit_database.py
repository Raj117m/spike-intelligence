import duckdb

con = duckdb.connect("data/demand.duckdb")

tables = con.execute("""
SHOW TABLES
""").fetchall()

print("\n================ TABLES ================\n")

for (table,) in tables:

    print(f"\n===== {table} =====")

    try:

        count = con.execute(
            f"SELECT COUNT(*) FROM {table}"
        ).fetchone()[0]

        print(f"Rows : {count:,}")

    except Exception as e:

        print(e)

    try:

        schema = con.execute(
            f"DESCRIBE {table}"
        ).fetchdf()

        print(schema)

    except Exception as e:

        print(e)

print("\n================ DONE ================\n")
