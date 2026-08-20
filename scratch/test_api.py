import sys
import os

# Add backend directory to sys.path so 'app' can be imported
sys.path.insert(0, os.path.abspath('backend'))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

response = client.post(
    "/api/teachers/",
    json={
        "name": "Test Teacher",
        "email": "test@teacher.com",
        "employee_id": "T001",
        "mobile": "1234567890",
        "qualification": "PhD",
        "assignments": [],
        "max_daily_periods": 7,
        "max_weekly_periods": 32,
        "class_teacher_of_division_id": None
    }
)

print(response.status_code)
print(response.json())
