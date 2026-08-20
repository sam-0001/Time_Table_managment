import { BrowserRouter, Routes, Route, useNavigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import SetupWizard from './pages/SetupWizard'
import Dashboard from './pages/Dashboard'
import Login from './pages/Login'
import Register from './pages/Register'
import ForgotPassword from './pages/ForgotPassword'
import TeachersPage from './pages/Teachers'
import SubjectsPage from './pages/Subjects'
import ClassesPage from './pages/Classes'
import LeavesPage from './pages/Leaves'
import SettingsPage from './pages/Settings'
import { AppLayout } from './components/layout/AppLayout'

const queryClient = new QueryClient()

function DashboardLanding() {
  const navigate = useNavigate()
  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900 p-8 flex flex-col items-center justify-center font-sans">
      <div className="max-w-4xl w-full text-center space-y-6">
        <div className="inline-block px-4 py-1.5 rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 text-sm font-semibold tracking-wide shadow-sm">
          School Timetable Management System
        </div>
        <h1 className="text-5xl font-extrabold text-slate-900 dark:text-white tracking-tight">
          Intelligent Scheduling for Modern Schools
        </h1>
        <p className="text-lg text-slate-600 dark:text-slate-400 max-w-2xl mx-auto leading-relaxed">
          The ultimate engine to manage teachers, classes, and schedules. Build clash-free timetables automatically with our constraint satisfaction algorithm.
        </p>
        <div className="flex gap-4 justify-center mt-8">
          <button 
            onClick={() => navigate('/setup')}
            className="px-6 py-3 bg-white text-slate-900 border border-slate-200 rounded-lg font-medium hover:bg-slate-50 transition-all shadow-sm"
          >
            Start Setup Wizard
          </button>
          <button 
            onClick={() => navigate('/dashboard')}
            className="px-6 py-3 bg-slate-900 text-white dark:bg-blue-600 dark:text-white rounded-lg font-medium hover:bg-slate-800 dark:hover:bg-blue-700 transition-all shadow-md"
          >
            Go to Dashboard
          </button>
        </div>
      </div>
    </div>
  )
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<DashboardLanding />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/setup" element={<SetupWizard />} />
          <Route path="/dashboard" element={<AppLayout><Dashboard /></AppLayout>} />
          <Route path="/teachers" element={<AppLayout><TeachersPage /></AppLayout>} />
          <Route path="/subjects" element={<AppLayout><SubjectsPage /></AppLayout>} />
          <Route path="/classes" element={<AppLayout><ClassesPage /></AppLayout>} />
          <Route path="/leaves" element={<AppLayout><LeavesPage /></AppLayout>} />
          <Route path="/settings" element={<AppLayout><SettingsPage /></AppLayout>} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

export default App
