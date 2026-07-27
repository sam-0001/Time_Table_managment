import { useState } from 'react'
import { useMarkLeave, useGenerateArrangements, useLeaves, useArrangements, useDeleteLeave } from '@/hooks/useLeaves'
import { useTeachers } from '@/hooks/useTeachers'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { toast } from 'sonner'
import { Loader2, Plus, CalendarIcon, Activity, Trash2 } from 'lucide-react'

export default function LeavesPage() {
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0])
  const { data: teachers } = useTeachers()
  const { data: leaves, isLoading: isLoadingLeaves } = useLeaves(selectedDate)
  const { data: arrangements, isLoading: isLoadingArrangements } = useArrangements(selectedDate)
  
  const { mutateAsync: markLeave, isPending: isMarking } = useMarkLeave()
  const { mutateAsync: generateArrangements, isPending: isGenerating } = useGenerateArrangements()
  const { mutateAsync: deleteLeave, isPending: isDeleting } = useDeleteLeave()
  
  const [isOpen, setIsOpen] = useState(false)
  const [formData, setFormData] = useState({
    teacher_id: '',
    date: new Date().toISOString().split('T')[0],
    leave_type: 'FULL',
    reason: ''
  })

  const handleMarkLeave = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await markLeave(formData)
      toast.success('Leave marked successfully')
      setIsOpen(false)
      setFormData({ teacher_id: '', date: new Date().toISOString().split('T')[0], leave_type: 'FULL', reason: '' })
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to mark leave')
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this leave?')) return
    try {
      await deleteLeave(id)
      toast.success('Leave deleted successfully')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to delete leave')
    }
  }

  const handleGenerate = async () => {
    try {
      const res = await generateArrangements(selectedDate)
      toast.success(`Generated ${res.substitutions_made} arrangements successfully`)
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to generate arrangements')
    }
  }

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6 animate-in fade-in">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h2 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">Leaves & Arrangements</h2>
          <p className="text-slate-500 mt-1">Manage teacher absences and auto-generate substitutions.</p>
        </div>
        
        <div className="flex flex-wrap gap-2 items-center">
          <Input 
            type="date" 
            value={selectedDate} 
            onChange={(e) => setSelectedDate(e.target.value)}
            className="w-auto"
          />
          
          <Button variant="outline" onClick={handleGenerate} disabled={isGenerating} className="text-emerald-600 border-emerald-200 hover:bg-emerald-50 dark:hover:bg-emerald-900/20">
            {isGenerating ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Activity className="mr-2 h-4 w-4" />}
            Auto-Generate Subs
          </Button>
          
          <Dialog open={isOpen} onOpenChange={setIsOpen}>
            <DialogTrigger render={
              <Button className="bg-blue-600 hover:bg-blue-700">
                <Plus className="mr-2 h-4 w-4" /> Mark Leave
              </Button>
            }>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Mark Teacher on Leave</DialogTitle>
              </DialogHeader>
              <form onSubmit={handleMarkLeave} className="space-y-4 pt-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Teacher</label>
                  <select 
                    required 
                    value={formData.teacher_id} 
                    onChange={e => setFormData({...formData, teacher_id: e.target.value})}
                    className="flex h-10 w-full rounded-md border border-slate-300 bg-transparent px-3 py-2 text-sm placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-400 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 dark:border-slate-700 dark:text-slate-50 dark:focus:ring-slate-400 dark:focus:ring-offset-slate-900"
                  >
                    <option value="">Select a teacher...</option>
                    {teachers?.map((t: any) => (
                      <option key={t.id} value={t.id}>{t.employee_id} - {t.name || 'Unnamed Teacher'}</option>
                    ))}
                  </select>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Date</label>
                    <Input type="date" required value={formData.date} onChange={e => setFormData({...formData, date: e.target.value})} />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Leave Type</label>
                    <select 
                      required 
                      value={formData.leave_type} 
                      onChange={e => setFormData({...formData, leave_type: e.target.value})}
                      className="flex h-10 w-full rounded-md border border-slate-300 bg-transparent px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-400 dark:border-slate-700 dark:bg-slate-900"
                    >
                      <option value="FULL">Full Day</option>
                      <option value="FIRST_HALF">First Half (Before Lunch)</option>
                      <option value="SECOND_HALF">Second Half (After Lunch)</option>
                    </select>
                  </div>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Reason (Optional)</label>
                  <Input value={formData.reason} onChange={e => setFormData({...formData, reason: e.target.value})} />
                </div>
                <Button type="submit" className="w-full" disabled={isMarking}>
                  {isMarking ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : 'Mark Leave'}
                </Button>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CalendarIcon className="h-5 w-5 text-slate-500" /> Leaves on {selectedDate}
            </CardTitle>
            <CardDescription>Teachers absent on the selected date.</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoadingLeaves ? (
              <div className="flex justify-center p-8"><Loader2 className="h-6 w-6 animate-spin text-slate-400" /></div>
            ) : leaves?.length === 0 ? (
              <div className="flex justify-center p-8 text-slate-500">No leaves marked for this date.</div>
            ) : (
              <div className="space-y-3">
                {leaves?.map((leave: any) => (
                  <div key={leave.id} className="flex justify-between items-center p-3 rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/50">
                    <div>
                      <p className="font-medium">{leave.teacher_name}</p>
                      <p className="text-sm text-slate-500">
                        {leave.leave_type === 'FULL' ? 'Full Day' : leave.leave_type === 'FIRST_HALF' ? 'First Half' : 'Second Half'} 
                        {leave.reason ? ` - ${leave.reason}` : ''}
                      </p>
                    </div>
                    <Button variant="ghost" size="icon" onClick={() => handleDelete(leave.id)} disabled={isDeleting} className="text-red-500 hover:text-red-700 hover:bg-red-50">
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-emerald-500" /> Arrangements on {selectedDate}
            </CardTitle>
            <CardDescription>Substitutions assigned for absences.</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoadingArrangements ? (
              <div className="flex justify-center p-8"><Loader2 className="h-6 w-6 animate-spin text-slate-400" /></div>
            ) : arrangements?.length === 0 ? (
              <div className="flex justify-center p-8 text-slate-500">No arrangements needed or generated.</div>
            ) : (
              <div className="space-y-3">
                {arrangements?.map((sub: any) => (
                  <div key={sub.id} className="flex flex-col p-3 rounded-lg border border-emerald-100 dark:border-emerald-900/30 bg-emerald-50/50 dark:bg-emerald-900/10">
                    <div className="flex justify-between items-start">
                      <p className="font-medium text-emerald-700 dark:text-emerald-400">
                        {sub.substitute_teacher_name} <span className="text-slate-500 font-normal">substituting for</span> {sub.original_teacher_name}
                      </p>
                      <span className="text-xs font-medium bg-emerald-100 dark:bg-emerald-900/50 text-emerald-700 dark:text-emerald-400 px-2 py-1 rounded">
                        Period {sub.period + 1}
                      </span>
                    </div>
                    <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">
                      {sub.division_name} • {sub.subject_name}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
