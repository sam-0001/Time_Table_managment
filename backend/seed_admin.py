from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine
from app.db.models import User, RoleEnum
from app.core.security import get_password_hash
import sys

def seed_admin():
    db: Session = SessionLocal()
    try:
        admin_email = "admin@school.edu"
        existing_admin = db.query(User).filter(User.email == admin_email).first()
        if existing_admin:
            print("Admin user already exists.")
            return

        admin_user = User(
            email=admin_email,
            hashed_password=get_password_hash("admin123"),
            full_name="System Admin",
            role=RoleEnum.SUPER_ADMIN,
            is_active=True
        )
        db.add(admin_user)
        db.commit()
        print("Admin user seeded successfully!")
        print("Email: admin@school.edu")
        print("Password: admin123")
    except Exception as e:
        print(f"Error seeding admin: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_admin()
