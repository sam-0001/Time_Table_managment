import React, { useState } from 'react'
import { useParents, useCreateParent, useDeleteParent } from '@/hooks/useParents'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { toast } from 'sonner'
import { Loader2, Plus, Trash2 } from 'lucide-react'

export default function ParentsPage() {
  const { data: parents, isLoading } = useParents()
  const { mutateAsync: createParent } = useCreateParent()
  const { mutateAsync: deleteParent } = useDeleteParent()
  
  const [isOpen, setIsOpen] = useState(false)
  
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    address: '',
    blood_group: ''
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await createParent(formData)
      toast.success('Parent created successfully')
      setIsOpen(false)
      setFormData({ name: '', email: '', phone: '', address: '', blood_group: '' })
    } catch (error: any) {
      toast.error('Failed to save parent')
    }
  }

  const handleDelete = async (id: string) => {
    if (confirm('Are you sure you want to delete this parent?')) {
      try {
        await deleteParent(id)
        toast.success('Parent deleted successfully')
      } catch (error) {
        toast.error('Failed to delete parent')
      }
    }
  }

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">Parents</h2>
        </div>
        <Dialog open={isOpen} onOpenChange={setIsOpen}>
          <DialogTrigger render={<Button className="bg-blue-600"><Plus className="mr-2 h-4 w-4" /> Add Parent</Button>} />
          <DialogContent>
            <DialogHeader><DialogTitle>Add New Parent</DialogTitle></DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4 pt-4">
              <Input placeholder="Full Name" value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} required />
              <Input type="email" placeholder="Email" value={formData.email} onChange={e => setFormData({...formData, email: e.target.value})} required />
              <Input placeholder="Phone" value={formData.phone} onChange={e => setFormData({...formData, phone: e.target.value})} required />
              <Input placeholder="Address" value={formData.address} onChange={e => setFormData({...formData, address: e.target.value})} />
              <Input placeholder="Blood Group" value={formData.blood_group} onChange={e => setFormData({...formData, blood_group: e.target.value})} />
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
                  <TableHead>Name</TableHead>
                  <TableHead>Email</TableHead>
                  <TableHead>Phone</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {parents?.map((parent: any) => (
                  <TableRow key={parent.id}>
                    <TableCell className="font-medium">{parent.name}</TableCell>
                    <TableCell>{parent.email}</TableCell>
                    <TableCell>{parent.phone}</TableCell>
                    <TableCell className="text-right">
                      <Button variant="ghost" size="sm" onClick={() => handleDelete(parent.id)} className="text-red-500"><Trash2 className="h-4 w-4" /></Button>
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
