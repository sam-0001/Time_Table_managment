import uuid
import requests
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User, School, RoleEnum
from app.api.deps import require_roles
from pydantic import BaseModel
import os

router = APIRouter()

CASHFREE_APP_ID = os.getenv("CASHFREE_APP_ID", "TEST_APP_ID")
CASHFREE_SECRET_KEY = os.getenv("CASHFREE_SECRET_KEY", "TEST_SECRET_KEY")
CASHFREE_ENV = os.getenv("CASHFREE_ENV", "SANDBOX") # SANDBOX or PRODUCTION

class PaymentOrderRequest(BaseModel):
    amount: float = 499.00
    currency: str = "INR"

class PaymentVerification(BaseModel):
    order_id: str

@router.post("/create-order")
def create_order(
    req: PaymentOrderRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([RoleEnum.SUPER_ADMIN, RoleEnum.SCHOOL_ADMIN]))
):
    if current_user.school.plan_type == "PRO":
        raise HTTPException(status_code=400, detail="You are already on the PRO plan.")
        
    order_id = f"ORDER_{current_user.school_id[:8]}_{uuid.uuid4().hex[:8]}"
    
    url = "https://sandbox.cashfree.com/pg/orders" if CASHFREE_ENV == "SANDBOX" else "https://api.cashfree.com/pg/orders"
    
    payload = {
        "order_amount": req.amount,
        "order_currency": req.currency,
        "order_id": order_id,
        "customer_details": {
            "customer_id": current_user.id[:10],
            "customer_phone": "9999999999",
            "customer_email": current_user.email,
            "customer_name": current_user.full_name
        },
        "order_meta": {
            "return_url": f"https://time-table-managment-smoky.vercel.app/payment-status?order_id={order_id}"
        }
    }
    
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "x-api-version": "2023-08-01",
        "x-client-id": CASHFREE_APP_ID,
        "x-client-secret": CASHFREE_SECRET_KEY
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return {"payment_session_id": data.get("payment_session_id"), "order_id": order_id}
    except Exception as e:
        print(f"Cashfree Order Error: {e}")
        # For demo purposes, if keys aren't set, we mock success!
        if CASHFREE_APP_ID == "TEST_APP_ID":
            return {"payment_session_id": "MOCK_SESSION_ID", "order_id": order_id}
        raise HTTPException(status_code=500, detail="Could not create payment order")

@router.post("/verify")
def verify_payment(
    req: PaymentVerification,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([RoleEnum.SUPER_ADMIN, RoleEnum.SCHOOL_ADMIN]))
):
    # Mock fallback
    if CASHFREE_APP_ID == "TEST_APP_ID":
        current_user.school.plan_type = "PRO"
        db.commit()
        return {"status": "SUCCESS", "message": "Upgraded to PRO successfully (MOCK)"}
        
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
            current_user.school.plan_type = "PRO"
            db.commit()
            return {"status": "SUCCESS", "message": "Upgraded to PRO successfully!"}
        else:
            return {"status": "PENDING", "message": "Payment not completed yet"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Could not verify payment")

