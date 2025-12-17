import csv

import psycopg2

DATABASE_URL = "postgresql://prod_perfusion_board_prep_user:gpJpRUk4edz6HXGCGyZc9F2yUDTnSV49@dpg-cmr8u2md3nmc73efeb1g-a.ohio-postgres.render.com/prod_perfusion_board_prep"

conn = psycopg2.connect(DATABASE_URL)

cursor = conn.cursor()
cursor.execute("""
    SELECT *
    FROM review_explanation
    WHERE sources::text LIKE '%Glenn P. Gravlee, Richard F. Davis, John W. Hammon, Barry D. Kussman - Cardiopulmonary Bypass and Mechanical Support- Principles and Practice%'
""")

rows = cursor.fetchall()
columns = [desc[0] for desc in cursor.description]

with open("explanations_export.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(columns)
    writer.writerows(rows)

print(f"Exported {len(rows)} rows to explanations_export.csv")

cursor.close()
conn.close()
