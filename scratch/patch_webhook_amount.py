import re

with open('app/api/routes/payments.py', 'r') as f:
    content = f.read()

def repl(m):
    return """                    payment.status = "PAID"
                    payment.school.plan_type = "PRO"
                    if payment.amount == 799.00:
                        payment.school.available_generations += 5
                    else:
                        payment.school.available_generations += 2
                    db.commit()"""

content = re.sub(
    r'                    payment\.status = "PAID"\s+payment\.school\.plan_type = "PRO"\s+payment\.school\.available_generations \+= 2\s+db\.commit\(\)',
    repl,
    content
)

with open('app/api/routes/payments.py', 'w') as f:
    f.write(content)
