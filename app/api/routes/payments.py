import uuid
import requests
import json
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User, School, RoleEnum, Payment
from app.api.deps import require_roles, get_current_user
from pydantic import BaseModel
import os
import hmac
import hashlib
import base64

router = APIRouter()

CASHFREE_APP_ID = os.getenv("CASHFREE_APP_ID", "")
CASHFREE_SECRET_KEY = os.getenv("CASHFREE_SECRET_KEY", "")
CASHFREE_ENV = os.getenv("CASHFREE_ENV", "SANDBOX")  # SANDBOX or PRODUCTION
ADMIN_SECRET = os.getenv("ADMIN_SECRET", "")  # Secret key for admin credit endpoint
GATEWAY_ENABLED = bool(CASHFREE_APP_ID and CASHFREE_APP_ID != "TEST_APP_ID")

class PaymentOrderRequest(BaseModel):
    amount: float = 499.00
    currency: str = "INR"

class PaymentVerification(BaseModel):
    order_id: str

class AdminCreditRequest(BaseModel):
    school_id: str
    generations: int
    secret: str


@router.post("/create-order")
def create_order(
    req: PaymentOrderRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([RoleEnum.SUPER_ADMIN, RoleEnum.SCHOOL_ADMIN]))
):
    if not GATEWAY_ENABLED:
        raise HTTPException(
            status_code=503,
            detail="Payment gateway is not configured yet. Please contact support at sc922467@gmail.com to upgrade your plan."
        )

    order_id = f"ORDER_{current_user.school_id[:8]}_{uuid.uuid4().hex[:8]}"

    payment = Payment(
        order_id=order_id,
        school_id=current_user.school_id,
        amount=req.amount,
        status="PENDING"
    )
    db.add(payment)
    db.commit()

    # Make environment check case-insensitive
    is_sandbox = CASHFREE_ENV.upper() == "SANDBOX"
    url = "https://sandbox.cashfree.com/pg/orders" if is_sandbox else "https://api.cashfree.com/pg/orders"

    payload = {
        "order_amount": req.amount,
        "order_currency": req.currency,
        "order_id": order_id,
        "customer_details": {
            "customer_id": current_user.id[:10],
            "customer_phone": current_user.phone or "9999999999",
            "customer_email": current_user.email,
            "customer_name": current_user.full_name
        },
        "order_meta": {
            "return_url": f"https://time-table-managment-smoky.vercel.app/profile?order_id={order_id}"
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
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        # If Cashfree returned an error code, this will print the exact reason before throwing
        if not response.ok:
            print(f"Cashfree create_order failed: {response.text}")
            response.raise_for_status()
            
        data = response.json()
        
        if "payment_session_id" not in data:
            # Clean up the pending order since payment couldn't be initiated
            db.delete(payment)
            db.commit()
            print(f"Cashfree missing session ID. Full response: {data}")
            raise HTTPException(
                status_code=500, 
                detail=f"Cashfree API did not return a payment_session_id. Response: {data}"
            )
            
        return {
            "payment_session_id": data.get("payment_session_id"), 
            "order_id": order_id,
            "environment": CASHFREE_ENV.lower()
        }
    except requests.exceptions.RequestException as e:
        err_msg = e.response.text if e.response else str(e)
        db.delete(payment)
        db.commit()
        print(f"Cashfree create order error: {err_msg}")
        raise HTTPException(status_code=503, detail=f"Payment gateway unavailable: {err_msg}")
    except HTTPException:
        raise
    except Exception as e:
        db.delete(payment)
        db.commit()
        print(f"Unexpected create order error: {e}")
        raise HTTPException(status_code=503, detail="Payment gateway unavailable. Please try again later.")


@router.post("/verify")
def verify_payment(
    req: PaymentVerification,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([RoleEnum.SUPER_ADMIN, RoleEnum.SCHOOL_ADMIN]))
):
    if not GATEWAY_ENABLED:
        raise HTTPException(status_code=503, detail="Payment gateway not configured.")

    payment = db.query(Payment).filter(
        Payment.order_id == req.order_id,
        Payment.school_id == current_user.school_id
    ).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Order not found")

    if payment.status == "PAID":
        return {"status": "SUCCESS", "message": "Payment already processed!"}

    is_sandbox = CASHFREE_ENV.upper() == "SANDBOX"
    url = f"https://sandbox.cashfree.com/pg/orders/{req.order_id}" if is_sandbox else f"https://api.cashfree.com/pg/orders/{req.order_id}"
    headers = {
        "accept": "application/json",
        "x-api-version": "2023-08-01",
        "x-client-id": CASHFREE_APP_ID,
        "x-client-secret": CASHFREE_SECRET_KEY
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
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
    except requests.exceptions.RequestException as e:
        err_msg = e.response.text if e.response else str(e)
        print(f"Cashfree verify error: {err_msg}")
        raise HTTPException(status_code=500, detail="Could not verify payment with gateway")
    except Exception as e:
        print(f"Unexpected verify error: {e}")
        raise HTTPException(status_code=500, detail="Could not verify payment with gateway")


@router.post("/admin/credit")
def admin_credit_generations(
    req: AdminCreditRequest,
    db: Session = Depends(get_db),
):
    """Admin-only endpoint to manually credit generations to a school."""
    if not ADMIN_SECRET or req.secret != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Invalid admin secret")

    school = db.query(School).filter(School.id == req.school_id).first()
    if not school:
        raise HTTPException(status_code=404, detail="School not found")

    school.plan_type = "PRO"
    school.available_generations += req.generations
    db.commit()
    return {"status": "OK", "message": f"{req.generations} generations credited to {school.name}. Total: {school.available_generations}"}


@router.post("/webhook")
async def cashfree_webhook(request: Request, db: Session = Depends(get_db)):
    try:
        body = await request.body()
        signature = request.headers.get("x-webhook-signature")
        timestamp = request.headers.get("x-webhook-timestamp")

        if not signature or not timestamp:
            raise HTTPException(status_code=400, detail="Missing signature")

        if GATEWAY_ENABLED and CASHFREE_SECRET_KEY:
            payload = timestamp.encode('utf-8') + body
            expected_sig = base64.b64encode(
                hmac.new(CASHFREE_SECRET_KEY.encode('utf-8'), payload, hashlib.sha256).digest()
            ).decode('utf-8')
            if signature != expected_sig:
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
    except HTTPException:
        raise
    except Exception as e:
        print(f"Webhook error: {e}")
        return {"status": "ERROR"}
