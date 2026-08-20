import React, { useState, useRef } from 'react'
import { useSubjects } from '@/hooks/useSubjects'
import { useTeachers, useCreateTeacher, useDeleteTeacher, useUpdateTeacher } from '@/hooks/useTeachers'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { toast } from 'sonner'
import { Loader2, Plus, Search, Trash2, Edit, Download, Upload, Eye, BookOpen, User } from 'lucide-react'
import { api } from '@/lib/api'

import { useClasses } from '@/hooks/useClasses'
export default function TeachersPage() {
  const { data: teachers, isLoading, refetch } = useTeachers()
  const { data: subjects } = useSubjects()
  const { data: classes } = useClasses('temp-academic-year-id')
  const { mutateAsync: createTeacher, isPending: isCreating } = useCreateTeacher()
  const { mutateAsync: updateTeacher, isPending: isUpdating } = useUpdateTeacher()
  const { mutateAsync: deleteTeacher } = useDeleteTeacher()
  
  const [search, setSearch] = useState('')
  const [isOpen, setIsOpen] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [viewingTeacher, setViewingTeacher] = useState<any>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    employee_id: '',
    mobile: '',
    qualification: '',
    assignments: [] as {subject_id: string, division_id: string}[],
    max_weekly_periods: 32,
    max_daily_periods: 7,
    class_teacher_of_division_id: null as string | null
  })

  const filteredTeachers = teachers?.filter(t => 
    t.employee_id.toLowerCase().includes(search.toLowerCase())
  ) || []

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      if (editingId) {
        await updateTeacher({ id: editingId, data: formData })
        toast.success('Teacher updated successfully')
      } else {
        await createTeacher(formData)
        toast.success('Teacher created successfully')
      }
      setIsOpen(false)
      setEditingId(null)
      setFormData({ name: '', email: '', employee_id: '', mobile: '', qualification: '', assignments: [], max_weekly_periods: 32, max_daily_periods: 7, class_teacher_of_division_id: null })
    } catch (error: any) {
      if (error.response?.data?.detail) {
        const detail = error.response.data.detail;
        if (typeof detail === 'string') {
          toast.error(detail);
        } else if (Array.isArray(detail)) {
          toast.error(detail.map((d: any) => `${d.loc.join('.')}: ${d.msg}`).join('\n'));
        } else {
          toast.error(JSON.stringify(detail));
        }
      } else {
        toast.error('Failed to save teacher');
      }
    }
  }

  const handleEdit = (teacher: any) => {
    setEditingId(teacher.id)
    setFormData({
      name: teacher.name || '',
      email: teacher.email || '',
      employee_id: teacher.employee_id,
      mobile: teacher.mobile || '',
      qualification: teacher.qualification || '',
      assignments: [...teacher.assignments],
      max_weekly_periods: teacher.max_weekly_periods,
      max_daily_periods: teacher.max_daily_periods,
      class_teacher_of_division_id: teacher.class_teacher_of_division_id || null
    })
    setIsOpen(true)
  }

  const handleDelete = async (id: string) => {
    if (confirm('Are you sure you want to delete this teacher?')) {
      try {
        await deleteTeacher(id)
        toast.success('Teacher deleted successfully')
      } catch (error) {
        toast.error('Failed to delete teacher')
      }
    }
  }

  const handleExport = async () => {
    try {
      const response = await api.get('/import-export/export/teachers', { responseType: 'blob' })
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', 'teachers_export.xlsx')
      document.body.appendChild(link)
      link.click()
      link.remove()
      toast.success('Export started')
    } catch (error) {
      toast.error('Export failed')
    }
  }

  const handleImport = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    
    const formData = new FormData()
    formData.append('file', file)
    
    const loadingToast = toast.loading('Importing teachers...')
    try {
      await api.post('/import-export/import/teachers', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      toast.success('Teachers imported successfully', { id: loadingToast })
      refetch()
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Import failed', { id: loadingToast })
    }
    
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6 animate-in fade-in">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">Teachers</h2>
          <p className="text-slate-500 mt-1">Manage teaching staff and workload limits.</p>
        </div>
        
        <div className="flex gap-2">
          <input type="file" ref={fileInputRef} className="hidden" accept=".xlsx,.xls" onChange={handleImport} />
          <Button variant="outline" onClick={() => fileInputRef.current?.click()}>
            <Upload className="mr-2 h-4 w-4" /> Import Excel
          </Button>
          <Button variant="outline" onClick={handleExport}>
            <Download className="mr-2 h-4 w-4" /> Export Excel
          </Button>
          
          <Dialog open={isOpen} onOpenChange={setIsOpen}>
            <DialogTrigger render={
              <Button className="bg-blue-600 hover:bg-blue-700" onClick={() => {
                setEditingId(null)
                setFormData({ name: '', email: '', employee_id: '', mobile: '', qualification: '', assignments: [], max_weekly_periods: 32, max_daily_periods: 7, class_teacher_of_division_id: null })
              }}>
                <Plus className="mr-2 h-4 w-4" /> Add Teacher
              </Button>
            }>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>{editingId ? 'Edit Teacher' : 'Add New Teacher'}</DialogTitle>
              </DialogHeader>
              <form onSubmit={handleSubmit} className="space-y-4 pt-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Name</label>
                    <Input required value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} placeholder="e.g. John Doe" />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Email (Login) - Optional</label>
                    <Input type="email" value={formData.email} onChange={e => setFormData({...formData, email: e.target.value})} placeholder="e.g. john@school.edu" />
                  </div>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Employee ID</label>
                  <Input disabled={!!editingId} value={formData.employee_id} onChange={e => setFormData({...formData, employee_id: e.target.value})} placeholder="Auto-generated if empty" />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Mobile</label>
                    <Input value={formData.mobile} onChange={e => setFormData({...formData, mobile: e.target.value})} />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Qualification</label>
                    <Input value={formData.qualification} onChange={e => setFormData({...formData, qualification: e.target.value})} />
                  </div>
                </div>
                
                <div className="space-y-2">
                  <label className="text-sm font-medium text-purple-700 dark:text-purple-400">Class Teacher Assignment (Optional)</label>
                  <select
                    value={formData.class_teacher_of_division_id || ""}
                    onChange={(e) => setFormData({...formData, class_teacher_of_division_id: e.target.value || null})}
                    className="flex h-10 w-full rounded-md border border-purple-200 bg-purple-50 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-400 dark:bg-purple-950/30 dark:border-purple-800 dark:text-slate-50"
                  >
                    <option value="">None</option>
                    {classes?.flatMap(c => c.divisions.map(d => (
                      <option key={d.id} value={d.id}>Std {c.name} - Div {d.name}</option>
                    )))}
                  </select>
                  <p className="text-xs text-slate-500">Class Teachers are prioritized to take Period 1 of their assigned class for attendance.</p>
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <label className="text-sm font-medium">Assigned Subjects & Divisions</label>
                    <Button type="button" variant="outline" size="sm" onClick={() => setFormData({...formData, assignments: [...formData.assignments, {subject_id: '', division_id: ''}]})}>
                      <Plus className="h-3 w-3 mr-1" /> Add
                    </Button>
                  </div>
                  <div className="space-y-2 max-h-48 overflow-y-auto pr-2">
                    {formData.assignments.map((assign, idx) => {
                      // Calculate taken assignments for this row
                      const taken = new Set<string>();
                      teachers?.forEach(t => {
                        if (editingId && t.id === editingId) return;
                        t.assignments.forEach((a: any) => {
                          taken.add(`${a.subject_id}-${a.division_id}`);
                        });
                      });
                      formData.assignments.forEach((a, formIdx) => {
                        if (formIdx !== idx && a.subject_id && a.division_id) {
                          taken.add(`${a.subject_id}-${a.division_id}`);
                        }
                      });

                      return (
                      <div key={idx} className="flex gap-2 items-center">
                        <select
                          required
                          value={assign.subject_id}
                          onChange={(e) => {
                            const newAssigns = [...formData.assignments]
                            newAssigns[idx].subject_id = e.target.value
                            newAssigns[idx].division_id = '' // Reset division when subject changes
                            setFormData({...formData, assignments: newAssigns})
                          }}
                          className="flex h-10 w-1/2 rounded-md border border-slate-300 bg-transparent px-3 py-2 text-sm placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-400 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 dark:border-slate-700 dark:text-slate-50 dark:focus:ring-slate-400 dark:focus:ring-offset-slate-900"
                        >
                          <option value="">Select Subject</option>
                          {subjects?.filter(s => {
                             if (assign.subject_id === s.id) return true;
                             const sClass = classes?.find(c => c.id === s.class_id);
                             if (!sClass) return false;
                             return sClass.divisions.some(d => !taken.has(`${s.id}-${d.id}`));
                          }).map(s => {
                            const cName = classes?.find(c => c.id === s.class_id)?.name || '';
                            return (
                              <option key={s.id} value={s.id}>
                                {cName ? `Std ${cName} - ` : ''}{s.name} ({s.code})
                              </option>
                            )
                          })}
                        </select>
                        
                        <select
                          required
                          value={assign.division_id}
                          onChange={(e) => {
                            const newAssigns = [...formData.assignments]
                            newAssigns[idx].division_id = e.target.value
                            setFormData({...formData, assignments: newAssigns})
                          }}
                          className="flex h-10 w-1/2 rounded-md border border-slate-300 bg-transparent px-3 py-2 text-sm placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-400 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 dark:border-slate-700 dark:text-slate-50 dark:focus:ring-slate-400 dark:focus:ring-offset-slate-900"
                          disabled={!assign.subject_id}
                        >
                          <option value="">Select Division</option>
                          {classes?.filter(c => {
                            if (!assign.subject_id) return true;
                            const selectedSubject = subjects?.find(s => s.id === assign.subject_id);
                            return c.id === selectedSubject?.class_id;
                          }).flatMap(c => c.divisions.filter(d => {
                             if (assign.division_id === d.id) return true;
                             return !taken.has(`${assign.subject_id}-${d.id}`);
                          }).map(d => (
                            <option key={d.id} value={d.id}>Div {d.name}</option>
                          )))}
                        </select>
                        
                        <Button type="button" variant="ghost" size="icon" className="text-rose-500" onClick={() => {
                          const newAssigns = formData.assignments.filter((_, i) => i !== idx)
                          setFormData({...formData, assignments: newAssigns})
                        }}>
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                      );
                    })}
                  </div>
                </div>
                <Button type="submit" className="w-full" disabled={isCreating || isUpdating}>
                  {isCreating || isUpdating ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : (editingId ? 'Update Teacher' : 'Save Teacher')}
                </Button>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      <Card>
        <CardHeader className="py-4">
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-slate-500" />
            <Input
              placeholder="Search by Employee ID..."
              className="pl-9 max-w-sm"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex justify-center p-8"><Loader2 className="h-8 w-8 animate-spin text-blue-500" /></div>
          ) : filteredTeachers.length === 0 ? (
            <div className="text-center p-8 text-slate-500">No teachers found.</div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Teacher</TableHead>
                  <TableHead>Employee ID</TableHead>
                  <TableHead>Mobile</TableHead>
                  <TableHead>Qualification</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredTeachers.map((teacher) => (
                  <TableRow key={teacher.id}>
                    <TableCell>
                      <div className="font-medium text-slate-900 dark:text-slate-100">{teacher.name || '-'}</div>
                      <div className="text-xs text-slate-500">{teacher.email || '-'}</div>
                    </TableCell>
                    <TableCell className="font-medium">{teacher.employee_id}</TableCell>
                    <TableCell>{teacher.mobile || '-'}</TableCell>
                    <TableCell>{teacher.qualification || '-'}</TableCell>
                    <TableCell>
                      {teacher.is_active ? (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800">Active</span>
                      ) : (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-slate-100 text-slate-800">Inactive</span>
                      )}
                    </TableCell>
                    <TableCell className="text-right">
                      <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => setViewingTeacher(teacher)}>
                        <Eye className="h-4 w-4 text-slate-500" />
                      </Button>
                      <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => handleEdit(teacher)}>
                        <Edit className="h-4 w-4 text-slate-500" />
                      </Button>
                      <Button variant="ghost" size="icon" className="h-8 w-8 text-rose-500 hover:text-rose-600" onClick={() => handleDelete(teacher.id)}>
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

      {/* View Teacher Details Dialog */}
      <Dialog open={!!viewingTeacher} onOpenChange={(open) => !open && setViewingTeacher(null)}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <User className="h-5 w-5 text-blue-600" />
              Teacher Profile
            </DialogTitle>
          </DialogHeader>
          
          {viewingTeacher && (
            <div className="space-y-6 pt-4">
              <div className="flex flex-col gap-1 border-b pb-4">
                <h3 className="text-xl font-bold text-slate-900 dark:text-white">{viewingTeacher.name || viewingTeacher.employee_id}</h3>
                <p className="text-sm text-slate-500 flex items-center gap-2">
                  <span className="font-mono bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded">{viewingTeacher.employee_id}</span>
                  {viewingTeacher.email && <span>• {viewingTeacher.email}</span>}
                </p>
                {viewingTeacher.mobile && <p className="text-sm text-slate-600 dark:text-slate-400">📱 {viewingTeacher.mobile}</p>}
                {viewingTeacher.qualification && <p className="text-sm text-slate-600 dark:text-slate-400">🎓 {viewingTeacher.qualification}</p>}
              </div>

              {viewingTeacher.class_teacher_of_division_id && (
                <div className="bg-purple-50 dark:bg-purple-900/20 border border-purple-100 dark:border-purple-800 p-3 rounded-lg flex items-start gap-3">
                  <User className="h-5 w-5 text-purple-600 mt-0.5" />
                  <div>
                    <p className="text-sm font-semibold text-purple-900 dark:text-purple-300">Class Teacher</p>
                    <p className="text-sm text-purple-700 dark:text-purple-400">
                      {(() => {
                        const div = classes?.flatMap((c: any) => c.divisions).find((d: any) => d.id === viewingTeacher.class_teacher_of_division_id);
                        const cls = classes?.find((c: any) => c.divisions.some((d: any) => d.id === viewingTeacher.class_teacher_of_division_id));
                        return cls && div ? `Std ${cls.name} - Div ${div.name}` : 'Unknown Class';
                      })()}
                    </p>
                  </div>
                </div>
              )}

              <div className="space-y-3">
                <h4 className="text-sm font-semibold flex items-center gap-2 text-slate-900 dark:text-white">
                  <BookOpen className="h-4 w-4 text-blue-600" />
                  Assigned Subjects
                </h4>
                
                {viewingTeacher.assignments && viewingTeacher.assignments.length > 0 ? (
                  <div className="grid gap-2">
                    {viewingTeacher.assignments.map((assign: any, idx: number) => {
                      const subject = subjects?.find((s: any) => s.id === assign.subject_id);
                      const cls = classes?.find((c: any) => c.id === subject?.class_id);
                      const div = cls?.divisions.find((d: any) => d.id === assign.division_id);
                      return (
                        <div key={idx} className="bg-slate-50 dark:bg-slate-800/50 p-2 rounded border border-slate-100 dark:border-slate-800 flex justify-between items-center">
                          <div>
                            <p className="text-sm font-medium text-slate-900 dark:text-slate-100">{subject?.name || 'Unknown Subject'}</p>
                            <p className="text-xs text-slate-500">Std {cls?.name} - Div {div?.name}</p>
                          </div>
                          <span className="text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300 px-2 py-1 rounded">
                            {subject?.weekly_periods || 0} p/w
                          </span>
                        </div>
                      )
                    })}
                  </div>
                ) : (
                  <p className="text-sm text-slate-500 italic">No subjects assigned yet.</p>
                )}
              </div>
              
              <div className="grid grid-cols-2 gap-4 pt-2 border-t">
                {(() => {
                  const totalAssignedPeriods = viewingTeacher.assignments?.reduce((sum: number, assign: any) => {
                    const subject = subjects?.find((s: any) => s.id === assign.subject_id);
                    return sum + (subject?.weekly_periods || 0);
                  }, 0) || 0;
                  const remainingPeriods = viewingTeacher.max_weekly_periods - totalAssignedPeriods;
                  
                  return (
                    <>
                      <div className="bg-slate-50 dark:bg-slate-800/50 p-3 rounded-lg text-center">
                        <p className="text-2xl font-bold text-slate-900 dark:text-white">{viewingTeacher.max_weekly_periods}</p>
                        <p className="text-xs text-slate-500 uppercase font-semibold">Max Weekly Limit</p>
                      </div>
                      <div className="bg-slate-50 dark:bg-slate-800/50 p-3 rounded-lg text-center">
                        <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">{totalAssignedPeriods}</p>
                        <p className="text-xs text-slate-500 uppercase font-semibold">Total Assigned</p>
                      </div>
                      <div className="bg-slate-50 dark:bg-slate-800/50 p-3 rounded-lg text-center">
                        <p className={`text-2xl font-bold ${remainingPeriods < 0 ? 'text-rose-500' : 'text-emerald-600 dark:text-emerald-400'}`}>{remainingPeriods}</p>
                        <p className="text-xs text-slate-500 uppercase font-semibold">Remaining Periods</p>
                      </div>
                      <div className="bg-slate-50 dark:bg-slate-800/50 p-3 rounded-lg text-center">
                        <p className="text-2xl font-bold text-slate-900 dark:text-white">{viewingTeacher.max_daily_periods}</p>
                        <p className="text-xs text-slate-500 uppercase font-semibold">Max Daily Limit</p>
                      </div>
                    </>
                  );
                })()}
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}
