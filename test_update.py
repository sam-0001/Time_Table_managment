import requests

r = requests.get("http://localhost:8000/api/teachers/")
teachers = r.json()
print("Teachers:", teachers)

if teachers:
    t_id = teachers[0]["id"]
    t_emp = teachers[0]["employee_id"]
    print(f"Updating teacher {t_id}")
    
    payload = {
        "name": "Updated Name",
        "email": "updated@test.com",
        "employee_id": t_emp,
        "mobile": "1234567890",
        "qualification": "Updated Qual"
    }
    r = requests.put(f"http://localhost:8000/api/teachers/{t_id}", json=payload)
    print(r.status_code)
    print(r.json())
