import re

with open('frontend/src/components/PaymentModal.tsx', 'r') as f:
    content = f.read()

content = content.replace(
    'export function PaymentModal({ isOpen, setIsOpen, onSuccess }: PaymentModalProps) {',
    'export function PaymentModal({ isOpen, setIsOpen, onSuccess, amount = 499.00 }: PaymentModalProps & { amount?: number }) {'
)
content = content.replace(
    '{ amount: 499.00, currency: "INR" }',
    '{ amount, currency: "INR" }'
)

# And update the text in the modal
content = content.replace(
    '<h3 className="text-lg font-medium leading-6 text-slate-900 mb-2">\n                    Upgrade to Pro Plan\n                  </h3>',
    '<h3 className="text-lg font-medium leading-6 text-slate-900 mb-2">\n                    Upgrade Plan\n                  </h3>'
)
content = content.replace(
    '<p className="text-sm text-slate-500">\n                    Get 2 Timetable Generations for ₹499.\n                  </p>',
    '<p className="text-sm text-slate-500">\n                    Pay ₹{amount} to upgrade your account.\n                  </p>'
)
content = content.replace(
    'toast.success("Upgraded to Pro successfully!")',
    'toast.success("Upgraded successfully!")'
)
content = content.replace(
    '₹499',
    '₹{amount}'
)

with open('frontend/src/components/PaymentModal.tsx', 'w') as f:
    f.write(content)
