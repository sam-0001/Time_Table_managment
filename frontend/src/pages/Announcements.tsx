import React, { useState } from 'react'
import { useAnnouncements, useCreateAnnouncement, useDeleteAnnouncement } from '@/hooks/useAnnouncements'
import { useClasses } from '@/hooks/useClasses'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { toast } from 'sonner'
import { Loader2, Plus, Trash2, Megaphone } from 'lucide-react'

export default function AnnouncementsPage() {
  const { data: classes } = useClasses('temp-academic-year-id')
  
  const [selectedFilter, setSelectedFilter] = useState('')
  const { data: announcements, isLoading } = useAnnouncements(selectedFilter)
  
  const { mutateAsync: createAnnouncement } = useCreateAnnouncement()
  const { mutateAsync: deleteAnnouncement } = useDeleteAnnouncement()
  
  const [isAddOpen, setIsAddOpen] = useState(false)
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    division_id: ''
  })

  const handleAddSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await createAnnouncement({
        ...formData,
        division_id: formData.division_id || undefined
      })
      toast.success('Announcement posted successfully')
      setIsAddOpen(false)
      setFormData({ title: '', description: '', division_id: '' })
    } catch (error) {
      toast.error('Failed to post announcement')
    }
  }

  const handleDelete = async (id: string) => {
    if (confirm('Delete this announcement?')) {
      try {
        await deleteAnnouncement(id)
        toast.success('Announcement deleted')
      } catch (error) {
        toast.error('Failed to delete')
      }
    }
  }

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">Notice Board</h2>
          <p className="text-slate-500 mt-1">Broadcast messages to students, parents, and teachers.</p>
        </div>
        <Dialog open={isAddOpen} onOpenChange={setIsAddOpen}>
          <DialogTrigger><Button className="bg-blue-600"><Plus className="mr-2 h-4 w-4" /> New Notice</Button></DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Post an Announcement</DialogTitle></DialogHeader>
            <form onSubmit={handleAddSubmit} className="space-y-4 pt-4">
              <Input placeholder="Title" value={formData.title} onChange={e => setFormData({...formData, title: e.target.value})} required />
              
              <textarea 
                className="w-full p-2 border rounded-md min-h-[100px]" 
                placeholder="Message description..."
                value={formData.description} 
                onChange={e => setFormData({...formData, description: e.target.value})} 
                required 
              />
              
              <select className="w-full p-2 border rounded-md" value={formData.division_id} onChange={e => setFormData({...formData, division_id: e.target.value})}>
                <option value="">School Wide (Everyone)</option>
                {classes?.map((c: any) => c.divisions?.map((d: any) => <option key={d.id} value={d.id}>{c.name} - {d.name}</option>))}
              </select>

              <Button type="submit" className="w-full bg-blue-600">Post Announcement</Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="flex gap-4 items-center bg-white p-4 rounded-xl shadow-sm border border-slate-100">
        <label className="text-sm font-medium">Filter by View:</label>
        <select className="p-2 border rounded-md w-64" value={selectedFilter} onChange={e => setSelectedFilter(e.target.value)}>
          <option value="">All Announcements</option>
          {classes?.map((c: any) => c.divisions?.map((d: any) => <option key={d.id} value={d.id}>{c.name} - {d.name}</option>))}
        </select>
      </div>

      <div className="space-y-4">
        {isLoading ? (
          <div className="p-8 flex justify-center"><Loader2 className="h-8 w-8 animate-spin" /></div>
        ) : announcements?.length === 0 ? (
          <div className="text-center py-12 bg-slate-50 rounded-xl border border-dashed border-slate-200">
            <Megaphone className="mx-auto h-12 w-12 text-slate-300 mb-4" />
            <h3 className="text-lg font-medium text-slate-900">No Announcements</h3>
            <p className="text-slate-500">There are currently no active notices to display.</p>
          </div>
        ) : (
          announcements?.map((ann: any) => (
            <Card key={ann.id} className="overflow-hidden border-l-4 border-l-blue-500">
              <CardContent className="p-6">
                <div className="flex justify-between items-start">
                  <div>
                    <div className="flex items-center gap-3 mb-2">
                      <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold ${ann.division_id ? 'bg-purple-100 text-purple-700' : 'bg-green-100 text-green-700'}`}>
                        {ann.division_name}
                      </span>
                      <span className="text-sm text-slate-500">{new Date(ann.date).toLocaleDateString()} at {new Date(ann.date).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
                    </div>
                    <h3 className="text-xl font-bold text-slate-900 mb-2">{ann.title}</h3>
                    <p className="text-slate-600 whitespace-pre-wrap">{ann.description}</p>
                  </div>
                  <Button variant="ghost" size="sm" onClick={() => handleDelete(ann.id)} className="text-red-500"><Trash2 className="h-4 w-4" /></Button>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  )
}
