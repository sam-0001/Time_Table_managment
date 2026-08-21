import re

with open('frontend/src/components/PaymentModal.tsx', 'r') as f:
    content = f.read()

content = content.replace(
    'Upgrade to Pro',
    'Upgrade Plan'
)
content = content.replace(
    'Unlock the power to add unlimited teachers, subjects, and classes! For ₹{amount}, you get 2 Timetable Generations for your full school data.',
    'Unlock the power to add unlimited teachers, subjects, and classes! For ₹{amount}, you get {amount === 799 ? 5 : 2} Timetable Generations for your full school data.'
)

with open('frontend/src/components/PaymentModal.tsx', 'w') as f:
    f.write(content)
