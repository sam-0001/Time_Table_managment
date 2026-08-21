import { Fragment, useState } from 'react'
import { Dialog, Transition } from '@headlessui/react'
import { Zap, Crown, Star, X } from 'lucide-react'
import { api } from '@/lib/api'
import { toast } from 'sonner'
import { useNavigate } from 'react-router-dom'

interface PaymentModalProps {
  isOpen: boolean
  setIsOpen: (val: boolean) => void
  onSuccess: () => void
  amount?: number
}

declare global { interface Window { Cashfree: any } }

export function PaymentModal({ isOpen, setIsOpen, onSuccess, amount = 499 }: PaymentModalProps) {
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const isPro = amount === 799
  const generations = isPro ? 5 : 2
  const planName = isPro ? 'Pro' : 'Plus'

  const handlePayment = async () => {
    setLoading(true)
    try {
      const { data } = await api.post('/payments/create-order', { amount, currency: 'INR' })
      if (data.payment_session_id === 'MOCK_SESSION_ID') {
        const { data: vData } = await api.post('/payments/verify', { order_id: data.order_id })
        if (vData.status === 'SUCCESS') {
          toast.success(vData.message || 'Upgraded successfully!')
          setIsOpen(false)
          onSuccess()
        }
        return
      }
      const cashfree = await window.Cashfree({ mode: 'sandbox' })
      cashfree.checkout({
        paymentSessionId: data.payment_session_id,
        returnUrl: `${window.location.origin}/profile?order_id=${data.order_id}`,
      })
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Payment initiation failed')
    } finally {
      setLoading(false)
    }
  }

  const handleViewPlans = () => {
    setIsOpen(false)
    navigate('/profile')
  }

  return (
    <Transition.Root show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={setIsOpen}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300" enterFrom="opacity-0" enterTo="opacity-100"
          leave="ease-in duration-200" leaveFrom="opacity-100" leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm transition-opacity" />
        </Transition.Child>

        <div className="fixed inset-0 z-10 w-screen overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300" enterFrom="opacity-0 translate-y-4 scale-95" enterTo="opacity-100 translate-y-0 scale-100"
              leave="ease-in duration-200" leaveFrom="opacity-100 translate-y-0 scale-100" leaveTo="opacity-0 translate-y-4 scale-95"
            >
              <Dialog.Panel className="relative w-full max-w-md rounded-2xl bg-white shadow-2xl overflow-hidden">
                {/* Close button */}
                <button
                  onClick={() => setIsOpen(false)}
                  className="absolute top-4 right-4 p-1.5 rounded-full text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors z-10"
                >
                  <X className="h-4 w-4" />
                </button>

                {/* Header gradient */}
                <div className={`px-6 pt-6 pb-8 ${isPro ? 'bg-gradient-to-br from-blue-600 to-blue-800' : 'bg-gradient-to-br from-slate-800 to-slate-900'}`}>
                  <div className="flex items-center gap-3 mb-4">
                    <div className="h-10 w-10 rounded-xl bg-white/20 flex items-center justify-center">
                      {isPro ? <Crown className="h-5 w-5 text-white" /> : <Star className="h-5 w-5 text-yellow-300" />}
                    </div>
                    <div>
                      <p className="text-white/70 text-xs font-medium uppercase tracking-wider">Upgrade to</p>
                      <h3 className="text-white font-bold text-xl">{planName} Plan</h3>
                    </div>
                  </div>
                  <div className="flex items-end gap-1">
                    <span className="text-white text-4xl font-extrabold">{"₹" + amount}</span>
                    <span className="text-white/60 text-sm mb-1">one-time</span>
                  </div>
                </div>

                {/* Features */}
                <div className="px-6 py-5 space-y-3">
                  <p className="text-slate-500 text-sm">You will receive:</p>
                  <div className="space-y-2">
                    <div className="flex items-center gap-3 p-3 bg-slate-50 rounded-lg">
                      <div className="h-8 w-8 rounded-lg bg-green-100 flex items-center justify-center shrink-0">
                        <Zap className="h-4 w-4 text-green-600" />
                      </div>
                      <div>
                        <p className="font-semibold text-slate-900 text-sm">{generations} Timetable Generations</p>
                        <p className="text-slate-500 text-xs">Generate clash-free schedules for your school</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3 p-3 bg-slate-50 rounded-lg">
                      <div className="h-8 w-8 rounded-lg bg-blue-100 flex items-center justify-center shrink-0">
                        <Crown className="h-4 w-4 text-blue-600" />
                      </div>
                      <div>
                        <p className="font-semibold text-slate-900 text-sm">Full Access — No Limits</p>
                        <p className="text-slate-500 text-xs">Add unlimited teachers, subjects & classes</p>
                      </div>
                    </div>
                  </div>

                  {/* Action buttons */}
                  <div className="flex flex-col gap-2 pt-2">
                    <button
                      onClick={handlePayment}
                      disabled={loading}
                      className={`w-full py-3 rounded-xl font-semibold text-white transition-all ${isPro ? 'bg-blue-600 hover:bg-blue-700' : 'bg-slate-900 hover:bg-slate-800'} ${loading ? 'opacity-60 cursor-not-allowed' : ''}`}
                    >
                      {loading ? 'Processing payment...' : ("Pay ₹" + amount + " — Upgrade Now")}
                    </button>
                    <button
                      onClick={handleViewPlans}
                      className="w-full py-2.5 rounded-xl font-medium text-slate-600 border border-slate-200 hover:bg-slate-50 transition-colors text-sm"
                    >
                      View All Plans on Profile
                    </button>
                    <button
                      onClick={() => setIsOpen(false)}
                      className="w-full py-2 text-slate-400 hover:text-slate-600 text-sm transition-colors"
                    >
                      Maybe later
                    </button>
                  </div>
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition.Root>
  )
}
