import { Link, useLocation } from 'react-router-dom'
import { LayoutDashboard, Users, BookOpen, Layers, Settings, CalendarRange, Menu } from 'lucide-react'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet'
import { Toaster } from 'sonner'

export function AppLayout({ children }: { children: React.ReactNode }) {
  const [isOpen, setIsOpen] = useState(false)
  const location = useLocation()
  
  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    { name: 'Teachers', href: '/teachers', icon: Users },
    { name: 'Subjects', href: '/subjects', icon: BookOpen },
    { name: 'Classes', href: '/classes', icon: Layers },
    { name: 'Leaves & Arr.', href: '/leaves', icon: CalendarRange },
    { name: 'Settings', href: '/settings', icon: Settings },
  ]

  const SidebarContent = () => (
    <div className="flex flex-col h-full bg-slate-50 dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800">
      <div className="p-6 flex items-center gap-3 border-b border-slate-200 dark:border-slate-800">
        <div className="h-8 w-8 bg-blue-600 rounded-lg flex items-center justify-center shadow-sm">
          <CalendarRange className="h-4 w-4 text-white" />
        </div>
        <span className="font-bold text-lg text-slate-900 dark:text-white tracking-tight">TimeTable</span>
      </div>
      
      <div className="flex-1 overflow-y-auto py-6 px-4 space-y-1">
        <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4 px-2">Menu</div>
        {navigation.map((item) => {
          const isActive = location.pathname.startsWith(item.href)
          return (
            <Link
              key={item.name}
              to={item.href}
              className={`flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                isActive 
                  ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300' 
                  : 'text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800'
              }`}
            >
              <item.icon className={`h-4 w-4 ${isActive ? 'text-blue-600 dark:text-blue-400' : 'text-slate-400'}`} />
              {item.name}
            </Link>
          )
        })}
      </div>
      
      <div className="p-4 border-t border-slate-200 dark:border-slate-800">
        <Link to="/profile" className="flex items-center gap-3 px-2 py-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
          <div className="h-8 w-8 rounded-full bg-slate-200 dark:bg-slate-700 border border-slate-300 dark:border-slate-600 flex items-center justify-center text-sm font-medium">
            <Settings className="h-4 w-4" />
          </div>
          <div className="flex flex-col">
            <span className="text-sm font-medium text-slate-900 dark:text-white">My Profile</span>
            <span className="text-xs text-slate-500">Manage Account</span>
          </div>
        </Link>
      </div>
    </div>
  )

  return (
    <div className="min-h-screen bg-white dark:bg-slate-950 flex flex-col md:flex-row font-sans">
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
      <div className="flex-1 md:pl-64 print:pl-0 flex flex-col min-h-screen print:min-h-0">
        <main className="flex-1 print:overflow-visible">
          {children}
        </main>
      </div>
    </div>
  )
}
