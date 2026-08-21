import sys

def patch():
    with open('app/api/routes/payments.py', 'r') as f:
        content = f.read()

    # Create Order
    old_create = """    if current_user.school.plan_type == "PRO":
        raise HTTPException(status_code=400, detail="You are already on the PRO plan.")"""
    new_create = """    # If they are PRO, they can still buy more generations!
    # if current_user.school.plan_type == "PRO":
    #     raise HTTPException(status_code=400, detail="You are already on the PRO plan.")"""
    content = content.replace(old_create, new_create)

    # Verify
    old_mock = """    if CASHFREE_APP_ID == "TEST_APP_ID":
        current_user.school.plan_type = "PRO"
        db.commit()
        return {"status": "SUCCESS", "message": "Upgraded to PRO successfully (MOCK)"}"""
    new_mock = """    if CASHFREE_APP_ID == "TEST_APP_ID":
        current_user.school.plan_type = "PRO"
        current_user.school.available_generations += 2
        db.commit()
        return {"status": "SUCCESS", "message": "Payment successful! 2 Generations added to your account."}"""
    content = content.replace(old_mock, new_mock)

    old_verify = """        if data.get("order_status") == "PAID":
            current_user.school.plan_type = "PRO"
            db.commit()
            return {"status": "SUCCESS", "message": "Upgraded to PRO successfully!"}"""
    new_verify = """        if data.get("order_status") == "PAID":
            current_user.school.plan_type = "PRO"
            current_user.school.available_generations += 2
            db.commit()
            return {"status": "SUCCESS", "message": "Payment successful! 2 Generations added to your account."}"""
    content = content.replace(old_verify, new_verify)

    with open('app/api/routes/payments.py', 'w') as f:
        f.write(content)

patch()
