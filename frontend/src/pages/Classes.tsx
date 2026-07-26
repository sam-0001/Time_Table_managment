import { useState } from 'react'
import { useClasses, useCreateClass, useUpdateClass, useDeleteClass } from '@/hooks/useClasses'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { toast } from 'sonner'
import { Loader2, Plus, Search, Layers, X, Edit, Trash2 } from 'lucide-react'

const TEMP_ACADEMIC_YEAR_ID = "temp-academic-year-id" 

export default function ClassesPage() {
  const { data: classes, isLoading } = useClasses(TEMP_ACADEMIC_YEAR_ID)
  const { mutateAsync: createClass, isPending: isCreating } = useCreateClass()
  const { mutateAsync: updateClass, isPending: isUpdating } = useUpdateClass()
  const { mutateAsync: deleteClass } = useDeleteClass()
  
  const [search, setSearch] = useState('')
  const [isOpen, setIsOpen] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  
  const [formData, setFormData] = useState({
    academic_year_id: TEMP_ACADEMIC_YEAR_ID,
    name: '',
    level: 10,
    divisions: [{ name: 'A' }]
  })

  const filteredClasses = classes?.filter(c => 
    c.name.toLowerCase().includes(search.toLowerCase())
  ) || []

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      if (editingId) {
        await updateClass({ id: editingId, data: formData })
        toast.success('Class updated successfully')
      } else {
        await createClass(formData)
        toast.success('Class created successfully')
      }
      setIsOpen(false)
      setEditingId(null)
      setFormData({ 
        academic_year_id: TEMP_ACADEMIC_YEAR_ID,
        name: '', 
        level: 10,
        divisions: [{ name: 'A' }]
      })
    } catch (error: any) {
      toast.error(error.response?.data?.detail || `Failed to ${editingId ? 'update' : 'create'} class`)
    }
  }

  const handleEdit = (cls: any) => {
    setFormData({
      academic_year_id: cls.academic_year_id,
      name: cls.name,
      level: cls.level,
      divisions: cls.divisions.map((d: any) => ({
        name: d.name,
        class_teacher_id: d.class_teacher_id,
        classroom_id: d.classroom_id
      }))
    })
    setEditingId(cls.id)
    setIsOpen(true)
  }

  const handleDelete = async (id: string) => {
    if (confirm('Are you sure you want to delete this class? This will also remove all its divisions and associated subjects.')) {
      try {
        await deleteClass(id)
        toast.success('Class deleted successfully')
      } catch (error) {
        toast.error('Failed to delete class')
      }
    }
  }

  const addDivision = () => {
    setFormData(prev => ({
      ...prev,
      divisions: [...prev.divisions, { name: '' }]
    }))
  }

  const updateDivision = (index: number, val: string) => {
    const newDivs = [...formData.divisions]
    newDivs[index].name = val
    setFormData(prev => ({ ...prev, divisions: newDivs }))
  }

  const removeDivision = (index: number) => {
    if (formData.divisions.length === 1) return
    const newDivs = [...formData.divisions]
    newDivs.splice(index, 1)
    setFormData(prev => ({ ...prev, divisions: newDivs }))
  }

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6 animate-in fade-in">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">Classes & Divisions</h2>
          <p className="text-slate-500 mt-1">Manage standard classes and their sections.</p>
        </div>
        
        <Dialog open={isOpen} onOpenChange={(val) => {
          setIsOpen(val)
          if (!val) {
            setEditingId(null)
            setFormData({ 
              academic_year_id: TEMP_ACADEMIC_YEAR_ID,
              name: '', 
              level: 10,
              divisions: [{ name: 'A' }]
            })
          }
        }}>
          <DialogTrigger render={
            <Button className="bg-blue-600 hover:bg-blue-700">
              <Plus className="mr-2 h-4 w-4" /> Add Class
            </Button>
          }>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>{editingId ? 'Edit Class' : 'Add New Class'}</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4 pt-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Class Name</label>
                  <Input required value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} placeholder="e.g. 10th Standard" />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Level (for sorting)</label>
                  <Input type="number" required value={formData.level} onChange={e => setFormData({...formData, level: parseInt(e.target.value)})} placeholder="e.g. 10" />
                </div>
              </div>
              
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <label className="text-sm font-medium">Divisions</label>
                  <Button type="button" variant="outline" size="sm" onClick={addDivision}>
                    <Plus className="h-3 w-3 mr-1" /> Add
                  </Button>
                </div>
                
                {formData.divisions.map((div, idx) => (
                  <div key={idx} className="flex gap-2 items-center">
                    <Input 
                      required 
                      value={div.name} 
                      onChange={e => updateDivision(idx, e.target.value)} 
                      placeholder={`Division ${idx + 1} (e.g. A, B)`} 
                    />
                    <Button type="button" variant="ghost" size="icon" onClick={() => removeDivision(idx)} disabled={formData.divisions.length === 1}>
                      <X className="h-4 w-4 text-rose-500" />
                    </Button>
                  </div>
                ))}
              </div>

              <Button type="submit" className="w-full" disabled={isCreating || isUpdating}>
                {(isCreating || isUpdating) ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : editingId ? 'Update Class' : 'Save Class'}
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <Card>
        <CardHeader className="py-4">
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-slate-500" />
            <Input
              placeholder="Search by Class Name..."
              className="pl-9 max-w-sm"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex justify-center p-8"><Loader2 className="h-8 w-8 animate-spin text-blue-500" /></div>
          ) : filteredClasses.length === 0 ? (
            <div className="text-center p-8 text-slate-500">No classes found.</div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredClasses.map((cls) => (
                <Card key={cls.id} className="shadow-sm hover:shadow-md transition-shadow">
                  <CardHeader className="pb-2">
                    <CardTitle className="flex justify-between items-center">
                      <div className="flex items-center gap-2">
                        <Layers className="h-4 w-4 text-slate-400" />
                        <span>{cls.name}</span>
                      </div>
                      <div className="flex gap-1">
                        <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => handleEdit(cls)}>
                          <Edit className="h-3.5 w-3.5 text-slate-500" />
                        </Button>
                        <Button variant="ghost" size="icon" className="h-7 w-7 text-rose-500 hover:text-rose-600" onClick={() => handleDelete(cls.id)}>
                          <Trash2 className="h-3.5 w-3.5" />
                        </Button>
                      </div>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-1">
                      <p className="text-sm text-slate-500">Level: {cls.level}</p>
                      <div className="flex flex-wrap gap-2 mt-3">
                        {cls.divisions?.map(d => (
                          <span key={d.id} className="inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium bg-blue-50 text-blue-700 border border-blue-200">
                            Div {d.name}
                          </span>
                        ))}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
