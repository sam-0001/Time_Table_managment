import { useState } from 'react'
import { useSubjects, useCreateSubject, useDeleteSubject, useUpdateSubject } from '@/hooks/useSubjects'
import { useClasses } from '@/hooks/useClasses'
import { useSettings } from '@/hooks/useSettings'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { toast } from 'sonner'
import { Loader2, Plus, Search, Trash2, Edit } from 'lucide-react'



export default function SubjectsPage() {
  const { data: classes, isLoading: isLoadingClasses } = useClasses()
  const [selectedClassId, setSelectedClassId] = useState<string | null>(null)
  
  // Set default selected class when classes load
  if (classes?.length && !selectedClassId) {
    setSelectedClassId(classes[0].id)
  }

  const { data: settings } = useSettings()
  const { data: subjects, isLoading: isLoadingSubjects } = useSubjects(selectedClassId || undefined)
  const { mutateAsync: createSubject, isPending: isCreating } = useCreateSubject()
  const { mutateAsync: updateSubject, isPending: isUpdating } = useUpdateSubject()
  const { mutateAsync: deleteSubject } = useDeleteSubject()
  
  const [search, setSearch] = useState('')
  const [isOpen, setIsOpen] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [formData, setFormData] = useState({
    name: '',
    code: '',
    weekly_periods: 5,
    double_period_allowed: false,
    is_lab: false
  })

  const filteredSubjects = subjects?.filter(s => 
    s.name.toLowerCase().includes(search.toLowerCase()) || 
    s.code.toLowerCase().includes(search.toLowerCase())
  ) || []

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      if (!selectedClassId) return;
      if (editingId) {
        await updateSubject({
          id: editingId,
          data: formData
        })
        toast.success('Subject updated successfully')
      } else {
        await createSubject({
          ...formData,
          class_id: selectedClassId
        })
        toast.success('Subject created successfully')
      }
      setIsOpen(false)
      setEditingId(null)
      setFormData({ 
        name: '', 
        code: '', 
        weekly_periods: 5, 
        double_period_allowed: false, 
        is_lab: false 
      })
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to save subject')
    }
  }

  const handleEdit = (subject: any) => {
    setEditingId(subject.id)
    setFormData({
      name: subject.name,
      code: subject.code,
      weekly_periods: subject.weekly_periods,
      double_period_allowed: subject.double_period_allowed,
      is_lab: subject.is_lab
    })
    setIsOpen(true)
  }

  const handleDelete = async (id: string) => {
    if (confirm('Are you sure you want to delete this subject?')) {
      try {
        await deleteSubject(id)
        toast.success('Subject deleted successfully')
      } catch (error) {
        toast.error('Failed to delete subject')
      }
    }
  }

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6 animate-in fade-in">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">Subjects Manager</h2>
          <p className="text-slate-500 mt-1">Configure subjects separately for each Standard/Class.</p>
        </div>
      </div>
      
      <div className="grid grid-cols-12 gap-8">
        {/* Classes Sidebar */}
        <div className="col-span-12 md:col-span-3 space-y-4">
          <h3 className="font-semibold text-slate-900 dark:text-slate-100 mb-2">Select Class</h3>
          {isLoadingClasses ? (
            <div className="flex justify-center p-4"><Loader2 className="h-6 w-6 animate-spin text-blue-500" /></div>
          ) : (
            <div className="flex flex-col gap-2">
              {classes?.map(c => (
                <button
                  key={c.id}
                  onClick={() => setSelectedClassId(c.id)}
                  className={`px-4 py-3 text-left rounded-lg transition-colors border ${
                    selectedClassId === c.id 
                      ? 'bg-blue-50 border-blue-200 text-blue-700 font-medium dark:bg-blue-900/30 dark:border-blue-800 dark:text-blue-400' 
                      : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50 dark:bg-slate-900 dark:border-slate-800 dark:text-slate-400 dark:hover:bg-slate-800'
                  }`}
                >
                  Standard {c.name}
                </button>
              ))}
              {classes?.length === 0 && (
                <p className="text-sm text-slate-500 italic">No classes found. Add classes first.</p>
              )}
            </div>
          )}
        </div>

        {/* Subjects Content */}
        <div className="col-span-12 md:col-span-9 space-y-6">
          
          {/* Workload Tracker */}
          {selectedClassId && (
            <div className="grid grid-cols-3 gap-4">
              {(() => {
                const target = settings?.total_weekly_periods || 40;
                const assigned = subjects?.reduce((sum, s) => sum + s.weekly_periods, 0) || 0;
                const remaining = target - assigned;
                
                return (
                  <>
                    <div className="bg-slate-50 dark:bg-slate-900/50 p-4 rounded-xl border border-slate-200 dark:border-slate-800 flex items-center justify-between">
                      <div>
                        <p className="text-sm font-semibold text-slate-500 uppercase">Target Total</p>
                        <p className="text-2xl font-bold text-slate-900 dark:text-white">{target}</p>
                      </div>
                    </div>
                    <div className="bg-slate-50 dark:bg-slate-900/50 p-4 rounded-xl border border-slate-200 dark:border-slate-800 flex items-center justify-between">
                      <div>
                        <p className="text-sm font-semibold text-slate-500 uppercase">Total Assigned</p>
                        <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">{assigned}</p>
                      </div>
                    </div>
                    <div className={`p-4 rounded-xl border flex items-center justify-between ${remaining < 0 ? 'bg-rose-50 border-rose-200 dark:bg-rose-900/20 dark:border-rose-800' : remaining === 0 ? 'bg-emerald-50 border-emerald-200 dark:bg-emerald-900/20 dark:border-emerald-800' : 'bg-amber-50 border-amber-200 dark:bg-amber-900/20 dark:border-amber-800'}`}>
                      <div>
                        <p className="text-sm font-semibold text-slate-500 uppercase">Remaining</p>
                        <p className={`text-2xl font-bold ${remaining < 0 ? 'text-rose-600 dark:text-rose-400' : remaining === 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-amber-600 dark:text-amber-500'}`}>{remaining}</p>
                      </div>
                    </div>
                  </>
                )
              })()}
            </div>
          )}

          <div className="flex justify-between items-center bg-slate-50 dark:bg-slate-900/50 p-4 rounded-xl border border-slate-200 dark:border-slate-800">
            <div className="relative w-72">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
              <Input
                placeholder="Search subjects..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-9 bg-white dark:bg-slate-950 border-slate-300 dark:border-slate-700"
              />
            </div>
            
            <Dialog open={isOpen} onOpenChange={setIsOpen}>
              <DialogTrigger render={
                <Button className="bg-blue-600 hover:bg-blue-700" disabled={!selectedClassId} onClick={() => {
                  setEditingId(null)
                  setFormData({ name: '', code: '', weekly_periods: 5, double_period_allowed: false, is_lab: false })
                }}>
                  <Plus className="mr-2 h-4 w-4" /> Add Subject
                </Button>
              }>
              </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>{editingId ? 'Edit Subject' : 'Add New Subject'}</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4 pt-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Subject Name</label>
                <Input required value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} placeholder="e.g. Mathematics" />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Subject Code</label>
                <Input required value={formData.code} onChange={e => setFormData({...formData, code: e.target.value})} placeholder="e.g. MATH101" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Weekly Periods</label>
                  <Input type="number" required value={formData.weekly_periods} onChange={e => setFormData({...formData, weekly_periods: parseInt(e.target.value)})} />
                </div>
              </div>
              <div className="flex gap-4">
                <label className="flex items-center gap-2 text-sm font-medium">
                  <input type="checkbox" checked={formData.is_lab} onChange={e => setFormData({...formData, is_lab: e.target.checked})} className="rounded border-slate-300" />
                  Is Lab Session
                </label>
                <label className="flex items-center gap-2 text-sm font-medium">
                  <input type="checkbox" checked={formData.double_period_allowed} onChange={e => setFormData({...formData, double_period_allowed: e.target.checked})} className="rounded border-slate-300" />
                  Allow Double Period
                </label>
              </div>
              <Button type="submit" className="w-full" disabled={isCreating || isUpdating}>
                {isCreating || isUpdating ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : (editingId ? 'Update Subject' : 'Save Subject')}
              </Button>
            </form>
          </DialogContent>
        </Dialog>
          </div>
          <Card className="border-slate-200 dark:border-slate-800 shadow-sm mt-4">
            <CardContent className="p-0">
              {isLoadingSubjects ? (
            <div className="flex justify-center p-8"><Loader2 className="h-8 w-8 animate-spin text-blue-500" /></div>
          ) : filteredSubjects.length === 0 ? (
            <div className="text-center p-8 text-slate-500">No subjects found.</div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Code</TableHead>
                  <TableHead>Name</TableHead>
                  <TableHead>Weekly Periods</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredSubjects.map((subject) => (
                  <TableRow key={subject.id}>
                    <TableCell className="font-medium">{subject.code}</TableCell>
                    <TableCell>{subject.name}</TableCell>
                    <TableCell>{subject.weekly_periods}</TableCell>
                    <TableCell>
                      <div className="flex gap-2">
                        {subject.is_lab && <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-purple-100 text-purple-800">Lab</span>}
                        {subject.double_period_allowed && <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-amber-100 text-amber-800">Double Period</span>}
                        {!subject.is_lab && !subject.double_period_allowed && <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-slate-100 text-slate-800">Standard</span>}
                      </div>
                    </TableCell>
                    <TableCell className="text-right">
                      <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => handleEdit(subject)}>
                        <Edit className="h-4 w-4 text-slate-500" />
                      </Button>
                      <Button variant="ghost" size="icon" className="h-8 w-8 text-rose-500 hover:text-rose-600" onClick={() => handleDelete(subject.id)}>
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
