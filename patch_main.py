import re

with open("app/main.py", "r") as f:
    content = f.read()

migration_sql = """
            # Add roles if Postgres
            try:
                db.execute(text("ALTER TYPE roleenum ADD VALUE IF NOT EXISTS 'STUDENT'"))
                db.execute(text("ALTER TYPE roleenum ADD VALUE IF NOT EXISTS 'PARENT'"))
                db.commit()
            except Exception as e:
                db.rollback()
                pass # might fail if not postgres or already exists or transaction issue
                
            db.execute(text('''
                CREATE TABLE IF NOT EXISTS parents (
                    id VARCHAR PRIMARY KEY,
                    user_id VARCHAR UNIQUE REFERENCES users(id) ON DELETE CASCADE,
                    school_id VARCHAR REFERENCES schools(id) ON DELETE CASCADE,
                    phone VARCHAR,
                    address VARCHAR,
                    blood_group VARCHAR
                )
            '''))
            db.execute(text('''
                CREATE TABLE IF NOT EXISTS students (
                    id VARCHAR PRIMARY KEY,
                    user_id VARCHAR UNIQUE REFERENCES users(id) ON DELETE CASCADE,
                    school_id VARCHAR REFERENCES schools(id) ON DELETE CASCADE,
                    parent_id VARCHAR REFERENCES parents(id) ON DELETE SET NULL,
                    division_id VARCHAR REFERENCES divisions(id) ON DELETE SET NULL,
                    admission_number VARCHAR,
                    gender VARCHAR,
                    date_of_birth TIMESTAMP,
                    blood_group VARCHAR,
                    address VARCHAR
                )
            '''))
"""

content = content.replace(
    'db.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS phone VARCHAR"))',
    'db.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS phone VARCHAR"))\n' + migration_sql
)

with open("app/main.py", "w") as f:
    f.write(content)
