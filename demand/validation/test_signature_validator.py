from demand.validation.signature_validator import SignatureValidator
import duckdb

SignatureValidator().validate()

con = duckdb.connect("data/demand.duckdb")

print(
    con.execute("""
    SELECT
        factor_set,
        category_scope,
        hit_rate,
        support_n
    FROM signatures
    ORDER BY support_n DESC
    LIMIT 50
    """).fetchdf()
)
