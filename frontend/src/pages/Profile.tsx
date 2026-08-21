import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { toast } from 'sonner'
import { Loader2, User, LogOut, KeyRound, CreditCard, CheckCircle2, Zap, Star, Crown, Phone } from 'lucide-react'
import { api } from '@/lib/api'
import { PaymentModal } from '@/components/PaymentModal'

export default function Profile() {
  const [user, setUser] = useState<any>(null)
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [isChangingPassword, setIsChangingPassword] = useState(false)
  const [isPaymentModalOpen, setIsPaymentModalOpen] = useState(false)
  const [selectedPlanAmount, setSelectedPlanAmount] = useState(499)
  const [phone, setPhone] = useState('')
  const [isSavingPhone, setIsSavingPhone] = useState(false)
  const navigate = useNavigate()

  const fetchUser = () => {
    api.get('/auth/me').then((r: any) => {
      setUser(r.data)
      setPhone(r.data?.phone || '')
    }).catch(console.error)
  }

  useEffect(() => {
    fetchUser()
    const params = new URLSearchParams(window.location.search)
    const orderId = params.get('order_id')
    if (orderId) {
      api.post('/payments/verify', { order_id: orderId })
        .then((res: any) => {
          if (res.data.status === 'SUCCESS') {
            toast.success('Payment successful! Plan upgraded.')
            fetchUser()
          } else {
            toast.info('Payment is still pending. We will notify you once completed.')
          }
        })
        .catch(() => toast.error('Could not verify payment status automatically.'))
        .finally(() => {
          window.history.replaceState({}, '', '/profile')
        })
    }
  }, [])

  const handleSavePhone = async (e: React.FormEvent) => {
    e.preventDefault()
    const digits = phone.replace(/\D/g, '')
    if (digits.length !== 10) {
      toast.error('Please enter a valid 10-digit mobile number')
      return
    }
    setIsSavingPhone(true)
    try {
      await api.patch('/auth/me', { phone: digits })
      toast.success('Mobile number saved!')
      fetchUser()
    } catch {
      toast.error('Could not save mobile number')
    } finally {
      setIsSavingPhone(false)
    }
  }

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsChangingPassword(true)
    try {
      await api.post('/auth/change-password', { current_password: currentPassword, new_password: newPassword })
      toast.success('Password changed successfully!')
      setCurrentPassword('')
      setNewPassword('')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to change password')
    } finally {
      setIsChangingPassword(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    toast.success('Logged out successfully')
    navigate('/login')
  }

  const isFreeOrDemo = user?.school_plan === 'FREE' || user?.school_plan === 'DEMO'
  const planLabel = user?.school_plan === 'FREE' ? 'Free'
    : user?.school_plan === 'DEMO' ? 'Demo'
    : 'Pro'
  const planBadgeCls = user?.school_plan === 'FREE'
    ? 'bg-slate-100 text-slate-700 ring-slate-300'
    : user?.school_plan === 'DEMO'
    ? 'bg-amber-100 text-amber-700 ring-amber-300'
    : 'bg-blue-100 text-blue-700 ring-blue-300'

  return (
    <div className="p-6 md:p-8 max-w-5xl mx-auto space-y-8 animate-in fade-in zoom-in-95 duration-200">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">My Profile</h1>
        <p className="text-slate-500 mt-1">Manage your account, billing, and subscription</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Account Details */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <div className="h-8 w-8 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center">
                <User className="h-4 w-4 text-slate-500" />
              </div>
              <div>
                <CardTitle className="text-base">Account Details</CardTitle>
                <CardDescription className="text-xs">Your personal information</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {user ? (
              <>
                <div className="flex items-center gap-4 p-4 bg-slate-50 dark:bg-slate-900 rounded-xl border border-slate-100 dark:border-slate-800">
                  <div className="h-14 w-14 rounded-full bg-blue-600 flex items-center justify-center text-white font-bold text-2xl shadow-sm shrink-0">
                    {user.full_name?.charAt(0)?.toUpperCase() || 'U'}
                  </div>
                  <div className="min-w-0">
                    <p className="font-semibold text-slate-900 dark:text-white text-base truncate">{user.full_name}</p>
                    <p className="text-slate-500 text-sm truncate">{user.email}</p>
                    <span className={`mt-1.5 inline-flex items-center rounded-full px-2 py-0.5 text-xs font-semibold ring-1 ${planBadgeCls}`}>
                      {planLabel} Plan
                    </span>
                  </div>
                </div>
                <div className="divide-y divide-slate-100 dark:divide-slate-800">
                  <div className="flex justify-between items-center py-2.5">
                    <span className="text-sm text-slate-500">Role</span>
                    <span className="text-xs font-semibold bg-blue-50 text-blue-700 px-2 py-0.5 rounded-md ring-1 ring-blue-100">
                      {user.role?.replace(/_/g, ' ')}
                    </span>
                  </div>
                  <div className="flex justify-between items-center py-2.5">
                    <span className="text-sm text-slate-500">Generations Remaining</span>
                    <span className="text-sm font-bold text-slate-900 dark:text-white">{user.available_generations ?? 0}</span>
                  </div>
                  <div className="flex justify-between items-center py-2.5">
                    <span className="text-sm text-slate-500">Account Status</span>
                    <span className="text-sm font-medium text-green-600">● Active</span>
                  </div>
                </div>

                {/* Mobile Number */}
                <form onSubmit={handleSavePhone} className="space-y-2 pt-1">
                  <label className="flex items-center gap-1.5 text-sm font-medium text-slate-700 dark:text-slate-300">
                    <Phone className="h-3.5 w-3.5" /> Mobile Number
                    {user.phone && <span className="ml-auto text-xs text-green-600 font-normal">Saved ✓</span>}
                  </label>
                  <div className="flex gap-2">
                    <span className="flex items-center px-3 bg-slate-100 border border-slate-200 rounded-lg text-slate-500 text-sm font-medium">+91</span>
                    <Input
                      type="tel"
                      maxLength={10}
                      placeholder="10-digit mobile"
                      value={phone}
                      onChange={e => setPhone(e.target.value.replace(/\D/g, ''))}
                      className="flex-1"
                    />
                    <Button type="submit" disabled={isSavingPhone} size="sm" className="bg-slate-900 hover:bg-slate-800 text-white shrink-0">
                      {isSavingPhone ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : 'Save'}
                    </Button>
                  </div>
                  <p className="text-xs text-slate-400">Used automatically for payment processing — no need to re-enter.</p>
                </form>

                <Button variant="destructive" onClick={handleLogout} className="w-full">
                  <LogOut className="h-4 w-4 mr-2" />Sign Out
                </Button>
              </>
            ) : (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="h-6 w-6 animate-spin text-slate-400" />
              </div>
            )}
          </CardContent>
        </Card>

        {/* Change Password */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <div className="h-8 w-8 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center">
                <KeyRound className="h-4 w-4 text-slate-500" />
              </div>
              <div>
                <CardTitle className="text-base">Change Password</CardTitle>
                <CardDescription className="text-xs">Update your login credentials</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleChangePassword} className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700 dark:text-slate-300">Current Password</label>
                <Input type="password" required placeholder="Enter current password" value={currentPassword} onChange={e => setCurrentPassword(e.target.value)} />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700 dark:text-slate-300">New Password</label>
                <Input type="password" required minLength={6} placeholder="At least 6 characters" value={newPassword} onChange={e => setNewPassword(e.target.value)} />
              </div>
              <Button type="submit" className="w-full bg-slate-900 hover:bg-slate-800 text-white" disabled={isChangingPassword}>
                {isChangingPassword ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Updating...</> : 'Update Password'}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>

      {/* Subscription & Billing */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-lg bg-blue-50 dark:bg-blue-900/30 flex items-center justify-center">
              <CreditCard className="h-4 w-4 text-blue-600" />
            </div>
            <div>
              <CardTitle className="text-base">Subscription & Billing</CardTitle>
              <CardDescription className="text-xs">Upgrade your plan to generate more timetables</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {user ? (
            <>
              {/* Current plan banner */}
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 p-4 rounded-xl border bg-gradient-to-r from-slate-50 to-blue-50/30 dark:from-slate-900 dark:to-blue-950/20">
                <div>
                  <p className="text-xs text-slate-500 uppercase tracking-wider font-semibold mb-0.5">Current Plan</p>
                  <h3 className="font-bold text-2xl text-slate-900 dark:text-white">{planLabel} Plan</h3>
                  <p className="text-sm text-slate-500 mt-1">
                    <span className="font-bold text-slate-900 dark:text-white">{user.available_generations ?? 0}</span>{' '}
                    timetable generation{(user.available_generations ?? 0) !== 1 ? 's' : ''} remaining
                  </p>
                </div>
                {isFreeOrDemo && (
                  <div className="flex items-center gap-1.5 text-amber-700 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2 text-sm font-medium shrink-0">
                    <Zap className="h-4 w-4" />
                    Upgrade to unlock more generations
                  </div>
                )}
              </div>

              {/* Plan cards */}
              <div className="grid sm:grid-cols-3 gap-4">
                {/* Free */}
                <div className={`relative border rounded-xl p-5 flex flex-col gap-4 ${isFreeOrDemo ? 'border-slate-300 bg-slate-50/50 dark:bg-slate-900/20' : 'border-slate-200 opacity-60'}`}>
                  {isFreeOrDemo && (
                    <span className="absolute -top-2.5 left-4 bg-slate-700 text-white text-[10px] font-bold px-2.5 py-0.5 rounded-full">CURRENT</span>
                  )}
                  <div className="flex items-center gap-2">
                    <User className="h-5 w-5 text-slate-400" />
                    <h3 className="font-bold text-lg">Free</h3>
                  </div>
                  <div>
                    <div className="text-3xl font-extrabold">₹0</div>
                    <p className="text-slate-500 text-sm mt-0.5">Try the Demo Sandbox</p>
                  </div>
                  <ul className="space-y-2 text-sm flex-1">
                    <li className="flex gap-2 items-center text-slate-600 dark:text-slate-400"><CheckCircle2 className="h-4 w-4 text-slate-400 shrink-0" />Demo sandbox access</li>
                    <li className="flex gap-2 items-center text-slate-600 dark:text-slate-400"><CheckCircle2 className="h-4 w-4 text-slate-400 shrink-0" />View pre-built timetable</li>
                    <li className="flex gap-2 items-center text-slate-400 line-through"><CheckCircle2 className="h-4 w-4 text-slate-300 shrink-0" />Real timetable generation</li>
                  </ul>
                  <Button variant="outline" className="w-full" disabled>Current Plan</Button>
                </div>

                {/* Plus */}
                <div className="relative border border-slate-200 hover:border-slate-400 rounded-xl p-5 flex flex-col gap-4 transition-colors">
                  <div className="flex items-center gap-2">
                    <Star className="h-5 w-5 text-yellow-500" />
                    <h3 className="font-bold text-lg">Plus</h3>
                  </div>
                  <div>
                    <div className="text-3xl font-extrabold">₹499</div>
                    <p className="text-slate-500 text-sm mt-0.5">For small schools</p>
                  </div>
                  <ul className="space-y-2 text-sm flex-1">
                    <li className="flex gap-2 items-center"><CheckCircle2 className="h-4 w-4 text-green-500 shrink-0" /><span>2 Timetable Generations</span></li>
                    <li className="flex gap-2 items-center"><CheckCircle2 className="h-4 w-4 text-green-500 shrink-0" /><span>Unlimited Teachers & Classes</span></li>
                    <li className="flex gap-2 items-center"><CheckCircle2 className="h-4 w-4 text-green-500 shrink-0" /><span>Export to Excel & Print</span></li>
                  </ul>
                  <Button
                    className="w-full bg-slate-900 hover:bg-slate-800 text-white"
                    onClick={() => { setSelectedPlanAmount(499); setIsPaymentModalOpen(true) }}
                  >
                    Buy Plus — ₹499
                  </Button>
                </div>

                {/* Pro */}
                <div className="relative border-2 border-blue-500 rounded-xl p-5 flex flex-col gap-4 bg-blue-50/30 dark:bg-blue-900/10">
                  <span className="absolute -top-2.5 right-4 bg-blue-600 text-white text-[10px] font-bold px-2.5 py-0.5 rounded-full">BEST VALUE</span>
                  <div className="flex items-center gap-2">
                    <Crown className="h-5 w-5 text-blue-600" />
                    <h3 className="font-bold text-lg text-blue-900 dark:text-blue-300">Pro</h3>
                  </div>
                  <div>
                    <div className="text-3xl font-extrabold text-blue-900 dark:text-blue-300">₹799</div>
                    <p className="text-slate-500 text-sm mt-0.5">For established schools</p>
                  </div>
                  <ul className="space-y-2 text-sm flex-1">
                    <li className="flex gap-2 items-center"><CheckCircle2 className="h-4 w-4 text-blue-600 shrink-0" /><span>5 Timetable Generations</span></li>
                    <li className="flex gap-2 items-center"><CheckCircle2 className="h-4 w-4 text-blue-600 shrink-0" /><span>Unlimited Teachers & Classes</span></li>
                    <li className="flex gap-2 items-center"><CheckCircle2 className="h-4 w-4 text-blue-600 shrink-0" /><span>Export to Excel & Print</span></li>
                    <li className="flex gap-2 items-center"><CheckCircle2 className="h-4 w-4 text-blue-600 shrink-0" /><span>Priority Support</span></li>
                  </ul>
                  <Button
                    className="w-full bg-blue-600 hover:bg-blue-700 text-white shadow"
                    onClick={() => { setSelectedPlanAmount(799); setIsPaymentModalOpen(true) }}
                  >
                    Buy Pro — ₹799
                  </Button>
                </div>
              </div>
            </>
          ) : (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-6 w-6 animate-spin text-slate-400" />
            </div>
          )}
        </CardContent>
      </Card>

      <PaymentModal
        isOpen={isPaymentModalOpen}
        setIsOpen={setIsPaymentModalOpen}
        amount={selectedPlanAmount}
        onSuccess={() => window.location.reload()}
      />
    </div>
  )
}
