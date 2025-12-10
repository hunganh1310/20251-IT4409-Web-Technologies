import psycopg2

conn = psycopg2.connect(dbname="music_streaming", user="postgres", password="postgres", host="localhost", port=5432)
cur = conn.cursor()
cur.execute("""
UPDATE users
SET roles = CASE
  WHEN roles IS NULL OR roles = '' THEN 'admin'
  WHEN roles ~* '\\badmin\\b' THEN roles
  ELSE roles || ',admin'
END
WHERE username = %s AND email = %s
""", ("admin", "anh.th225164@sis.hust.edu.vn"))
conn.commit()
cur.close()
conn.close()
print("Updated roles for admin user")