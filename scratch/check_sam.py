import psycopg2
from psycopg2.extras import RealDictCursor

conn = psycopg2.connect("postgresql://postgres:TimeTable#1100@db.ujdutvrmljeoczzelprd.supabase.co:5432/postgres")
cur = conn.cursor(cursor_factory=RealDictCursor)

cur.execute("SELECT id, school_id FROM users WHERE email = 'sam000123456789001@gmail.com'")
user = cur.fetchone()
print("User:", user)

if user and user['school_id']:
    cur.execute(f"SELECT id FROM academic_years WHERE school_id = '{user['school_id']}' LIMIT 1")
    ay = cur.fetchone()
    print("Academic Year:", ay)
    
cur.close()
conn.close()
