import { Link, useLocation } from 'react-router-dom'
import { LayoutDashboard, Users, BookOpen, Layers, Settings, CalendarRange, Menu, Zap } from 'lucide-react'
import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet'
import { Toaster } from 'sonner'
import { api } from '@/lib/api'

export function AppLayout({ children }: { children: React.ReactNode }) {
  const [isOpen, setIsOpen] = useState(false)
  const [user, setUser] = useState<any>(null)
  const location = useLocation()

  useEffect(() => {
    api.get('/auth/me').then((r: any) => setUser(r.data)).catch(() => {})
  }, [location.pathname])

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    { name: 'Teachers', href: '/teachers', icon: Users },
    { name: 'Subjects', href: '/subjects', icon: BookOpen },
    { name: 'Classes', href: '/classes', icon: Layers },
    { name: 'Leaves & Arr.', href: '/leaves', icon: CalendarRange },
    { name: 'Settings', href: '/settings', icon: Settings },
  ]

  const isFreeOrDemo = user?.school_plan === 'FREE' || user?.school_plan === 'DEMO'
  const planLabel = user?.school_plan === 'FREE' ? 'Free' : user?.school_plan === 'DEMO' ? 'Demo' : 'Pro'
  const planCls = user?.school_plan === 'PRO'
    ? 'bg-blue-100 text-blue-700'
    : 'bg-slate-100 text-slate-600'

  const SidebarContent = () => (
    <div className="flex flex-col h-full bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800">
      {/* Logo */}
      <div className="p-5 flex items-center gap-3 border-b border-slate-100 dark:border-slate-800">
        <div className="h-8 w-8 bg-blue-600 rounded-lg flex items-center justify-center shadow-sm">
          <CalendarRange className="h-4 w-4 text-white" />
        </div>
        <span className="font-bold text-lg text-slate-900 dark:text-white tracking-tight">TimeTable</span>
      </div>

      {/* Nav items */}
      <div className="flex-1 overflow-y-auto py-5 px-3 space-y-0.5">
        <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-3 px-3">Menu</p>
        {navigation.map((item) => {
          const isActive = location.pathname.startsWith(item.href)
          return (
            <Link
              key={item.name}
              to={item.href}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                isActive
                  ? 'bg-blue-50 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300 shadow-sm'
                  : 'text-slate-600 hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-800'
              }`}
            >
              <item.icon className={`h-4 w-4 shrink-0 ${isActive ? 'text-blue-600 dark:text-blue-400' : 'text-slate-400'}`} />
              {item.name}
              {isActive && <div className="ml-auto h-1.5 w-1.5 rounded-full bg-blue-600" />}
            </Link>
          )
        })}
      </div>

      {/* Upgrade nudge for free users */}
      {isFreeOrDemo && (
        <div className="px-3 pb-2">
          <Link to="/profile" className="flex items-center gap-2 p-3 rounded-xl bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-100 dark:from-blue-900/20 dark:to-indigo-900/20 dark:border-blue-800 hover:shadow-sm transition-all">
            <div className="h-8 w-8 rounded-lg bg-blue-600 flex items-center justify-center shrink-0">
              <Zap className="h-4 w-4 text-white" />
            </div>
            <div>
              <p className="text-xs font-semibold text-blue-900 dark:text-blue-300">Upgrade to Pro</p>
              <p className="text-[10px] text-blue-600/70">Get 5 timetable generations</p>
            </div>
          </Link>
        </div>
      )}

      {/* Profile section */}
      <div className="p-3 border-t border-slate-100 dark:border-slate-800">
        <Link to="/profile" className="flex items-center gap-3 px-2 py-2.5 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors group">
          <div className="h-8 w-8 rounded-full bg-blue-600 flex items-center justify-center text-white font-bold text-sm shrink-0 group-hover:ring-2 group-hover:ring-blue-300 transition-all">
            {user?.full_name?.charAt(0)?.toUpperCase() || '?'}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-semibold text-slate-900 dark:text-white truncate">{user?.full_name || 'My Profile'}</p>
            <div className="flex items-center gap-1.5">
              <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded-full ${planCls}`}>{planLabel}</span>
              {user?.available_generations !== undefined && (
                <span className="text-[10px] text-slate-400">{user.available_generations} gen left</span>
              )}
            </div>
          </div>
        </Link>
      </div>
    </div>
  )

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex flex-col md:flex-row font-sans">
      <Toaster position="top-right" richColors />

      {/* Mobile Header */}
      <div className="md:hidden flex items-center justify-between p-4 border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 print:hidden">
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 bg-blue-600 rounded-lg flex items-center justify-center">
            <CalendarRange className="h-4 w-4 text-white" />
          </div>
          <span className="font-bold text-lg">TimeTable</span>
        </div>
        <Sheet open={isOpen} onOpenChange={setIsOpen}>
          <SheetTrigger render={
            <Button variant="ghost" size="icon">
              <Menu className="h-5 w-5" />
            </Button>
          }>
          </SheetTrigger>
          <SheetContent side="left" className="p-0 w-72">
            <SidebarContent />
          </SheetContent>
        </Sheet>
      </div>

      {/* Desktop Sidebar */}
      <div className="hidden md:flex w-64 flex-col fixed inset-y-0 print:hidden">
        <SidebarContent />
      </div>

      {/* Main Content */}
      <div className="flex-1 md:pl-64 print:pl-0 flex flex-col min-h-screen print:min-h-0 bg-white dark:bg-slate-950">
        <main className="flex-1 print:overflow-visible">
          {children}
        </main>
      </div>
    </div>
  )
}
