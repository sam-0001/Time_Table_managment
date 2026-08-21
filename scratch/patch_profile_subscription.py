import re

with open('frontend/src/pages/Profile.tsx', 'r') as f:
    content = f.read()

# Add PaymentModal import
content = content.replace(
    'import { api } from \'@/lib/api\'',
    'import { api } from \'@/lib/api\'\nimport { PaymentModal } from \'@/components/PaymentModal\'\nimport { CreditCard, CheckCircle2 } from \'lucide-react\''
)

# Add states for PaymentModal
state_code = """  const [isChangingPassword, setIsChangingPassword] = useState(false)
  const [isPaymentModalOpen, setIsPaymentModalOpen] = useState(false)
  const [selectedPlanAmount, setSelectedPlanAmount] = useState(499)"""

content = content.replace(
    '  const [isChangingPassword, setIsChangingPassword] = useState(false)',
    state_code
)

# Add Subscription Card
subscription_card = """        <Card className="md:col-span-2">
          <CardHeader>
            <div className="flex items-center gap-2">
              <CreditCard className="h-5 w-5 text-slate-500" />
              <CardTitle>Subscription & Billing</CardTitle>
            </div>
            <CardDescription>Manage your current plan and available credits.</CardDescription>
          </CardHeader>
          <CardContent>
            {user ? (
              <div className="space-y-6">
                <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center p-4 border rounded-lg bg-slate-50 dark:bg-slate-900/50">
                  <div>
                    <h3 className="font-semibold text-lg flex items-center gap-2">
                      Current Plan: <span className="text-blue-600 uppercase">{user.school_plan}</span>
                    </h3>
                    <p className="text-slate-500 mt-1">
                      Available Timetable Generations: <span className="font-bold text-slate-900 dark:text-white">{user.available_generations}</span>
                    </p>
                  </div>
                </div>
                
                <div className="grid md:grid-cols-2 gap-4">
                  <div className="border rounded-xl p-6 relative flex flex-col justify-between">
                    <div>
                      <h3 className="font-bold text-xl mb-2">Plus Plan</h3>
                      <div className="text-3xl font-extrabold mb-4">₹499</div>
                      <ul className="space-y-2 mb-6">
                        <li className="flex gap-2 items-start"><CheckCircle2 className="h-5 w-5 text-green-500 shrink-0" /> <span>2 Timetable Generations</span></li>
                        <li className="flex gap-2 items-start"><CheckCircle2 className="h-5 w-5 text-green-500 shrink-0" /> <span>Unlimited Teachers & Classes</span></li>
                        <li className="flex gap-2 items-start"><CheckCircle2 className="h-5 w-5 text-green-500 shrink-0" /> <span>Valid for 1 Academic Year</span></li>
                      </ul>
                    </div>
                    <Button 
                      className="w-full bg-slate-900 text-white hover:bg-slate-800"
                      onClick={() => { setSelectedPlanAmount(499); setIsPaymentModalOpen(true); }}
                    >
                      Buy Plus Plan
                    </Button>
                  </div>
                  
                  <div className="border border-blue-200 rounded-xl p-6 relative bg-blue-50/50 dark:bg-blue-900/10 flex flex-col justify-between">
                    <div className="absolute top-0 right-0 bg-blue-600 text-white px-3 py-1 text-xs font-bold rounded-bl-lg rounded-tr-xl">BEST VALUE</div>
                    <div>
                      <h3 className="font-bold text-xl mb-2 text-blue-900 dark:text-blue-400">Pro Plan</h3>
                      <div className="text-3xl font-extrabold mb-4 text-blue-900 dark:text-blue-400">₹799</div>
                      <ul className="space-y-2 mb-6">
                        <li className="flex gap-2 items-start"><CheckCircle2 className="h-5 w-5 text-blue-600 shrink-0" /> <span>5 Timetable Generations</span></li>
                        <li className="flex gap-2 items-start"><CheckCircle2 className="h-5 w-5 text-blue-600 shrink-0" /> <span>Unlimited Teachers & Classes</span></li>
                        <li className="flex gap-2 items-start"><CheckCircle2 className="h-5 w-5 text-blue-600 shrink-0" /> <span>Priority Support</span></li>
                      </ul>
                    </div>
                    <Button 
                      className="w-full bg-blue-600 hover:bg-blue-700 text-white shadow-sm"
                      onClick={() => { setSelectedPlanAmount(799); setIsPaymentModalOpen(true); }}
                    >
                      Buy Pro Plan
                    </Button>
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="h-6 w-6 animate-spin text-slate-400" />
              </div>
            )}
          </CardContent>
        </Card>
"""

content = content.replace(
    '      </div>\n    </div>\n  )\n}',
    '      </div>\n' + subscription_card + '\n      <PaymentModal \n        isOpen={isPaymentModalOpen} \n        setIsOpen={setIsPaymentModalOpen} \n        amount={selectedPlanAmount}\n        onSuccess={() => window.location.reload()} \n      />\n    </div>\n  )\n}'
)

with open('frontend/src/pages/Profile.tsx', 'w') as f:
    f.write(content)
