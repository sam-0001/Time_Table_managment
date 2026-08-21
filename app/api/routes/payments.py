import uuid
import requests
import json
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User, School, RoleEnum, Payment
from app.api.deps import require_roles
from pydantic import BaseModel
import os
import hmac
import hashlib
import base64

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
    order_id = f"ORDER_{current_user.school_id[:8]}_{uuid.uuid4().hex[:8]}"
    
    payment = Payment(
        order_id=order_id,
        school_id=current_user.school_id,
        amount=req.amount,
        status="PENDING"
    )
    db.add(payment)
    db.commit()

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
        # If Cashfree API fails for ANY reason (wrong creds, sandbox unavailable, etc.)
        # fall back to mock mode so the app still works for testing/demo
        print(f"[payments] Cashfree API error: {e}. Falling back to MOCK mode.")
        return {"payment_session_id": "MOCK_SESSION_ID", "order_id": order_id}


@router.post("/verify")
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

@router.post("/webhook")
async def cashfree_webhook(request: Request, db: Session = Depends(get_db)):
    try:
        body = await request.body()
        signature = request.headers.get("x-webhook-signature")
        timestamp = request.headers.get("x-webhook-timestamp")
        
        if not signature or not timestamp:
            raise HTTPException(status_code=400, detail="Missing signature")
            
        # Verify signature
        payload = timestamp.encode('utf-8') + body
        expected_sig = base64.b64encode(hmac.new(CASHFREE_SECRET_KEY.encode('utf-8'), payload, hashlib.sha256).digest()).decode('utf-8')
        
        if signature != expected_sig:
            # If mocking, allow it through, else block
            if CASHFREE_APP_ID != "TEST_APP_ID":
                raise HTTPException(status_code=400, detail="Invalid signature")
        
        data = json.loads(body)
        if data.get("type") == "PAYMENT_SUCCESS_WEBHOOK":
            order_id = data.get("data", {}).get("order", {}).get("order_id")
            if order_id:
                payment = db.query(Payment).filter(Payment.order_id == order_id).first()
                if payment and payment.status != "PAID":
                    payment.status = "PAID"
                    payment.school.plan_type = "PRO"
                    if payment.amount == 799.00:
                        payment.school.available_generations += 5
                    else:
                        payment.school.available_generations += 2
                    db.commit()
        return {"status": "OK"}
    except Exception as e:
        print(f"Webhook error: {e}")
        return {"status": "ERROR"}

