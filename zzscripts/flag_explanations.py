import psycopg2

DATABASE_URL = "postgresql://prod_perfusion_board_prep_user:gpJpRUk4edz6HXGCGyZc9F2yUDTnSV49@dpg-cmr8u2md3nmc73efeb1g-a.ohio-postgres.render.com/prod_perfusion_board_prep"

conn = psycopg2.connect(DATABASE_URL)

cursor = conn.cursor()
cursor.execute("""
    UPDATE review_explanation
    SET flagged = true
    WHERE sources::text LIKE '%Glenn P. Gravlee, Richard F. Davis, John W. Hammon, Barry D. Kussman - Cardiopulmonary Bypass and Mechanical Support- Principles and Practice%'
""")

count = cursor.rowcount
conn.commit()

print(f"Updated {count} rows")

cursor.close()
conn.close()
