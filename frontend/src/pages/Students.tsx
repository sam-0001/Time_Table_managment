import React, { useState } from 'react'
import { useStudents, useCreateStudent, useDeleteStudent } from '@/hooks/useStudents'
import { useParents } from '@/hooks/useParents'
import { useClasses } from '@/hooks/useClasses'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { toast } from 'sonner'
import { Loader2, Plus, Trash2 } from 'lucide-react'

export default function StudentsPage() {
  const { data: students, isLoading } = useStudents()
  const { data: parents } = useParents()
  const { data: classes } = useClasses('temp-academic-year-id')
  const { mutateAsync: createStudent } = useCreateStudent()
  const { mutateAsync: deleteStudent } = useDeleteStudent()
  
  const [isOpen, setIsOpen] = useState(false)
  
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    parent_id: '',
    division_id: '',
    admission_number: '',
    gender: 'Male',
    address: '',
    blood_group: ''
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.division_id) {
      toast.error("Division is required")
      return;
    }
    try {
      await createStudent({
        ...formData,
        parent_id: formData.parent_id || null
      })
      toast.success('Student created successfully')
      setIsOpen(false)
    } catch (error: any) {
      toast.error('Failed to save student')
    }
  }

  const handleDelete = async (id: string) => {
    if (confirm('Are you sure you want to delete this student?')) {
      try {
        await deleteStudent(id)
        toast.success('Student deleted successfully')
      } catch (error) {
        toast.error('Failed to delete student')
      }
    }
  }

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">Students</h2>
        </div>
        <Dialog open={isOpen} onOpenChange={setIsOpen}>
          <DialogTrigger render={<Button className="bg-blue-600"><Plus className="mr-2 h-4 w-4" /> Add Student</Button>} />
          <DialogContent>
            <DialogHeader><DialogTitle>Add New Student</DialogTitle></DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4 pt-4">
              <Input placeholder="Full Name" value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} required />
              <Input type="email" placeholder="Email" value={formData.email} onChange={e => setFormData({...formData, email: e.target.value})} required />
              <Input placeholder="Admission Number" value={formData.admission_number} onChange={e => setFormData({...formData, admission_number: e.target.value})} required />
              
              <select 
                className="w-full p-2 border rounded-md"
                value={formData.division_id} 
                onChange={e => setFormData({...formData, division_id: e.target.value})} 
                required
              >
                <option value="">Select Class & Division</option>
                {classes?.map((c: any) => 
                  c.divisions?.map((d: any) => (
                    <option key={d.id} value={d.id}>{c.name} - {d.name}</option>
                  ))
                )}
              </select>

              <select 
                className="w-full p-2 border rounded-md"
                value={formData.parent_id} 
                onChange={e => setFormData({...formData, parent_id: e.target.value})}
              >
                <option value="">No Parent Assigned</option>
                {parents?.map((p: any) => (
                  <option key={p.id} value={p.id}>{p.name} ({p.phone})</option>
                ))}
              </select>

              <select className="w-full p-2 border rounded-md" value={formData.gender} onChange={e => setFormData({...formData, gender: e.target.value})}>
                <option value="Male">Male</option>
                <option value="Female">Female</option>
              </select>
              
              <Button type="submit" className="w-full bg-blue-600">Save</Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <Card>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="p-8 flex justify-center"><Loader2 className="h-8 w-8 animate-spin text-slate-400" /></div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Admission No</TableHead>
                  <TableHead>Name</TableHead>
                  <TableHead>Class</TableHead>
                  <TableHead>Parent</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {students?.map((student: any) => (
                  <TableRow key={student.id}>
                    <TableCell className="font-medium">{student.admission_number}</TableCell>
                    <TableCell>{student.name}</TableCell>
                    <TableCell>{student.division_name}</TableCell>
                    <TableCell>{student.parent_name || '-'}</TableCell>
                    <TableCell className="text-right">
                      <Button variant="ghost" size="sm" onClick={() => handleDelete(student.id)} className="text-red-500"><Trash2 className="h-4 w-4" /></Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
