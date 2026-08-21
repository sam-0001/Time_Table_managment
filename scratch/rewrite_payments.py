import re

with open('app/api/routes/payments.py', 'r') as f:
    content = f.read()

# I will replace the verify endpoint entirely
start_idx = content.find('@router.post("/verify")')
end_idx = content.find('@router.post("/webhook")')

new_verify = """@router.post("/verify")
def verify_payment(
    req: PaymentVerification,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([RoleEnum.SUPER_ADMIN, RoleEnum.SCHOOL_ADMIN]))
):
    payment = db.query(Payment).filter(Payment.order_id == req.order_id, Payment.school_id == current_user.school_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Order not found")
        
    if payment.status == "PAID":
        return {"status": "SUCCESS", "message": "Payment already processed!"}

    if CASHFREE_APP_ID == "TEST_APP_ID":
        payment.status = "PAID"
        current_user.school.plan_type = "PRO"
        if payment.amount == 799.00:
            current_user.school.available_generations += 5
            msg = "5 Generations added to your account."
        else:
            current_user.school.available_generations += 2
            msg = "2 Generations added to your account."
        db.commit()
        return {"status": "SUCCESS", "message": f"Payment successful! {msg}"}
        
    url = f"https://sandbox.cashfree.com/pg/orders/{req.order_id}" if CASHFREE_ENV == "SANDBOX" else f"https://api.cashfree.com/pg/orders/{req.order_id}"
    headers = {
        "accept": "application/json",
        "x-api-version": "2023-08-01",
        "x-client-id": CASHFREE_APP_ID,
        "x-client-secret": CASHFREE_SECRET_KEY
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data.get("order_status") == "PAID":
            payment.status = "PAID"
            current_user.school.plan_type = "PRO"
            if payment.amount == 799.00:
                current_user.school.available_generations += 5
                msg = "5 Generations added to your account."
            else:
                current_user.school.available_generations += 2
                msg = "2 Generations added to your account."
            db.commit()
            return {"status": "SUCCESS", "message": f"Payment successful! {msg}"}
        else:
            return {"status": "PENDING", "message": "Payment not completed yet"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Could not verify payment")

"""

content = content[:start_idx] + new_verify + content[end_idx:]

with open('app/api/routes/payments.py', 'w') as f:
    f.write(content)
