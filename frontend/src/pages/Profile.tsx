import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { toast } from 'sonner'
import { Loader2, User, LogOut, KeyRound } from 'lucide-react'
import { api } from '@/lib/api'

export default function Profile() {
  const [user, setUser] = useState<any>(null)
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [isChangingPassword, setIsChangingPassword] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    const fetchMe = async () => {
      try {
        const { data } = await api.get('/auth/me');
        setUser(data);
      } catch (err) {
        console.error(err);
      }
    };
    fetchMe();
  }, []);

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsChangingPassword(true)
    try {
      await api.post('/auth/change-password', {
        current_password: currentPassword,
        new_password: newPassword
      })
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

  return (
    <div className="p-8 max-w-4xl mx-auto space-y-8 animate-in fade-in zoom-in-95 duration-200">
      <div className="flex flex-col gap-1">
        <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">Profile</h1>
        <p className="text-slate-500">Manage your account settings and credentials</p>
      </div>

      <div className="grid gap-8 md:grid-cols-2">
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <User className="h-5 w-5 text-slate-500" />
              <CardTitle>Account Details</CardTitle>
            </div>
            <CardDescription>Your personal information.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {user ? (
              <>
                <div>
                  <label className="text-sm font-medium text-slate-500">Full Name</label>
                  <p className="text-lg font-medium">{user.full_name}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-slate-500">Email Address</label>
                  <p className="text-lg font-medium">{user.email}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-slate-500">Role</label>
                  <p className="text-lg font-medium">
                    <span className="inline-flex items-center rounded-md bg-blue-50 px-2 py-1 text-xs font-medium text-blue-700 ring-1 ring-inset ring-blue-700/10">
                      {user.role}
                    </span>
                  </p>
                </div>
                <div className="pt-4 mt-4 border-t">
                  <Button variant="destructive" onClick={handleLogout} className="w-full sm:w-auto">
                    <LogOut className="h-4 w-4 mr-2" />
                    Sign Out
                  </Button>
                </div>
              </>
            ) : (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="h-6 w-6 animate-spin text-slate-400" />
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <KeyRound className="h-5 w-5 text-slate-500" />
              <CardTitle>Change Password</CardTitle>
            </div>
            <CardDescription>Update your login credentials.</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleChangePassword} className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Current Password</label>
                <Input 
                  type="password" 
                  required 
                  value={currentPassword}
                  onChange={(e) => setCurrentPassword(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">New Password</label>
                <Input 
                  type="password" 
                  required 
                  minLength={6}
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                />
              </div>
              <Button type="submit" className="w-full" disabled={isChangingPassword}>
                {isChangingPassword ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : 'Update Password'}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
