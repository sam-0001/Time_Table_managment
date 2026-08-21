import sys

def patch():
    with open('frontend/src/pages/Dashboard.tsx', 'r') as f:
        content = f.read()

    # Add state
    old_state = "const [viewMode, setViewMode] = useState<'division' | 'teacher' | 'master'>('division')"
    new_state = "const [viewMode, setViewMode] = useState<'division' | 'teacher' | 'master'>('division')\n  const [isPaymentModalOpen, setIsPaymentModalOpen] = useState(false)"
    
    if "isPaymentModalOpen" not in content[:content.find("const handleGenerate")]:
        content = content.replace(old_state, new_state)
    
    with open('frontend/src/pages/Dashboard.tsx', 'w') as f:
        f.write(content)
        
    with open('frontend/src/components/PaymentModal.tsx', 'r') as f:
        content2 = f.read()
        
    old_decl = "declare const Cashfree: any;"
    new_decl = "declare global { interface Window { Cashfree: any } }"
    content2 = content2.replace(old_decl, new_decl)
    
    with open('frontend/src/components/PaymentModal.tsx', 'w') as f:
        f.write(content2)

patch()
