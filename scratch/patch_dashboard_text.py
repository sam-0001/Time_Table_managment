import sys

def patch():
    with open('frontend/src/components/PaymentModal.tsx', 'r') as f:
        content = f.read()
    
    old_text = "You are currently on the Demo plan. To add more teachers, subjects, or generate real timetables, please upgrade to the Pro plan for a one-time fee of ₹499."
    new_text = "Unlock the power to add unlimited teachers, subjects, and classes! For ₹499, you get 2 Timetable Generations for your full school data."
    
    content = content.replace(old_text, new_text)
    
    with open('frontend/src/components/PaymentModal.tsx', 'w') as f:
        f.write(content)

patch()
