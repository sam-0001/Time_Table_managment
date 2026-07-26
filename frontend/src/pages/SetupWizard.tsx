import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, CardContent, CardFooter } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

export default function SetupWizard() {
  const [step, setStep] = useState(1)
  const navigate = useNavigate()

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex items-center justify-center p-4 font-sans">
      <Card className="w-full max-w-3xl shadow-xl border-slate-200 dark:border-slate-800">
        <div className="bg-slate-900 text-white p-6 rounded-t-xl">
          <h2 className="text-2xl font-bold tracking-tight">First Time Setup</h2>
          <p className="text-slate-300 text-sm mt-1">Configure your school environment</p>
          
          <div className="flex gap-2 mt-6">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className={`h-2 flex-1 rounded-full ${i <= step ? 'bg-blue-500' : 'bg-slate-700'}`} />
            ))}
          </div>
        </div>
        
        <CardContent className="p-8">
          {step === 1 && (
            <div className="space-y-6 animate-in fade-in slide-in-from-right-4">
              <div>
                <h3 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-4">Education Society & School</h3>
                <div className="grid grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-700 dark:text-slate-300">School Name</label>
                    <Input placeholder="e.g. St. Xavier's High School" />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-700 dark:text-slate-300">School Code</label>
                    <Input placeholder="e.g. SXHS" />
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {step === 2 && (
            <div className="space-y-6 animate-in fade-in slide-in-from-right-4">
              <h3 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-4">School Timings</h3>
              <div className="grid grid-cols-2 gap-6">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-700 dark:text-slate-300">Start Time</label>
                  <Input type="time" defaultValue="08:00" />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-700 dark:text-slate-300">End Time</label>
                  <Input type="time" defaultValue="14:00" />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-700 dark:text-slate-300">Periods Per Day</label>
                  <Input type="number" defaultValue={7} />
                </div>
              </div>
            </div>
          )}
          
          {step === 3 && (
            <div className="space-y-6 animate-in fade-in slide-in-from-right-4">
              <h3 className="text-xl font-semibold text-slate-900 dark:text-slate-100">Classes & Divisions</h3>
              <p className="text-sm text-slate-500 mb-4">Configure standard classes (e.g. 1st to 12th)</p>
              <div className="p-8 border border-dashed border-slate-300 dark:border-slate-700 rounded-lg text-center text-slate-500 bg-slate-50 dark:bg-slate-900">
                Bulk create classes utility
              </div>
            </div>
          )}
          
          {step === 4 && (
            <div className="space-y-6 animate-in fade-in slide-in-from-right-4">
              <h3 className="text-xl font-semibold text-slate-900 dark:text-slate-100">Final Review</h3>
              <p className="text-sm text-slate-500">All set! Let's generate your dashboard.</p>
            </div>
          )}
        </CardContent>
        
        <CardFooter className="flex justify-between p-8 pt-0">
          <Button 
            variant="outline"
            onClick={() => setStep(s => Math.max(1, s - 1))}
            disabled={step === 1}
          >
            Back
          </Button>
          <Button 
            onClick={() => {
              if (step === 4) navigate('/dashboard')
              else setStep(s => Math.min(4, s + 1))
            }}
          >
            {step === 4 ? 'Complete Setup' : 'Continue'}
          </Button>
        </CardFooter>
      </Card>
    </div>
  )
}
