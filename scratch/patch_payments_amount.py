import re

with open('app/api/routes/payments.py', 'r') as f:
    content = f.read()

def repl(m):
    return """        payment.status = "PAID"
        current_user.school.plan_type = "PRO"
        if payment.amount == 799.00:
            current_user.school.available_generations += 5
            msg = "5 Generations added to your account."
        else:
            current_user.school.available_generations += 2
            msg = "2 Generations added to your account."
        db.commit()
        return {"status": "SUCCESS", "message": f"Payment successful! {msg}"}"""

content = re.sub(
    r'        payment\.status = "PAID"\s+current_user\.school\.plan_type = "PRO"\s+current_user\.school\.available_generations \+= 2\s+db\.commit\(\)\s+return \{"status": "SUCCESS", "message": "Payment successful! 2 Generations added to your account\."\}',
    repl,
    content
)

with open('app/api/routes/payments.py', 'w') as f:
    f.write(content)
