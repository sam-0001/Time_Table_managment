import sys

def patch():
    with open('frontend/src/pages/Dashboard.tsx', 'r') as f:
        content = f.read()
    
    # We have PaymentModal. We just need to add a button to trigger it.
    old_buttons = """<Button className="bg-blue-600 hover:bg-blue-700" onClick={handleGenerate} disabled={isGenerating}>
              {isGenerating ? 'Generating...' : 'Generate Timetable'}
            </Button>"""
            
    new_buttons = """<Button className="bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-600 hover:to-amber-700 text-white border-0 shadow-lg" onClick={() => setIsPaymentModalOpen(true)}>
              Upgrade to Pro 🚀
            </Button>
            <Button className="bg-blue-600 hover:bg-blue-700" onClick={handleGenerate} disabled={isGenerating}>
              {isGenerating ? 'Generating...' : 'Generate Timetable'}
            </Button>"""
    
    content = content.replace(old_buttons, new_buttons)
    with open('frontend/src/pages/Dashboard.tsx', 'w') as f:
        f.write(content)

patch()
