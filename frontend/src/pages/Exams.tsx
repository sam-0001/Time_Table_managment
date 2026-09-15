import React, { useState, useEffect } from 'react'
import { useExams, useCreateExam, useDeleteExam, useExamResults, useSaveExamResults } from '@/hooks/useExams'
import { useClasses } from '@/hooks/useClasses'
import { useSubjects } from '@/hooks/useSubjects'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { toast } from 'sonner'
import { Loader2, Plus, Trash2, Edit3, Save } from 'lucide-react'

export default function ExamsPage() {
  const { data: classes } = useClasses('temp-academic-year-id')
  const { data: subjects } = useSubjects()
  
  const [selectedDivision, setSelectedDivision] = useState('')
  const { data: exams, isLoading } = useExams(selectedDivision)
  const { mutateAsync: createExam } = useCreateExam()
  const { mutateAsync: deleteExam } = useDeleteExam()
  
  const [isAddOpen, setIsAddOpen] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    date: new Date().toISOString().split('T')[0],
    division_id: '',
    subject_id: '',
    max_marks: 100
  })

  // Results mode state
  const [selectedExam, setSelectedExam] = useState<any>(null)
  
  const handleAddSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await createExam(formData)
      toast.success('Exam created successfully')
      setIsAddOpen(false)
      setFormData({ ...formData, name: '' })
    } catch (error) {
      toast.error('Failed to create exam')
    }
  }

  const handleDelete = async (id: string) => {
    if (confirm('Delete this exam and all its results?')) {
      try {
        await deleteExam(id)
        toast.success('Exam deleted')
      } catch (error) {
        toast.error('Failed to delete')
      }
    }
  }

  if (selectedExam) {
    return <ExamResultsView exam={selectedExam} onBack={() => setSelectedExam(null)} />
  }

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">Exams & Grading</h2>
        <Dialog open={isAddOpen} onOpenChange={setIsAddOpen}>
          <DialogTrigger><Button className="bg-blue-600"><Plus className="mr-2 h-4 w-4" /> Add Exam</Button></DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Schedule New Exam</DialogTitle></DialogHeader>
            <form onSubmit={handleAddSubmit} className="space-y-4 pt-4">
              <Input placeholder="Exam Name (e.g. Midterm)" value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} required />
              <Input type="date" value={formData.date} onChange={e => setFormData({...formData, date: e.target.value})} required />
              
              <select className="w-full p-2 border rounded-md" value={formData.division_id} onChange={e => setFormData({...formData, division_id: e.target.value})} required>
                <option value="">Select Class & Division</option>
                {classes?.map((c: any) => c.divisions?.map((d: any) => <option key={d.id} value={d.id}>{c.name} - {d.name}</option>))}
              </select>

              <select className="w-full p-2 border rounded-md" value={formData.subject_id} onChange={e => setFormData({...formData, subject_id: e.target.value})} required>
                <option value="">Select Subject</option>
                {subjects?.map((s: any) => <option key={s.id} value={s.id}>{s.name}</option>)}
              </select>

              <Input type="number" placeholder="Max Marks" value={formData.max_marks} onChange={e => setFormData({...formData, max_marks: Number(e.target.value)})} required />
              
              <Button type="submit" className="w-full bg-blue-600">Save</Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <Card>
        <CardContent className="p-6">
          <div className="w-1/3">
            <label className="block text-sm font-medium mb-2">Filter by Class</label>
            <select className="w-full p-2 border rounded-md" value={selectedDivision} onChange={e => setSelectedDivision(e.target.value)}>
              <option value="">All Classes</option>
              {classes?.map((c: any) => c.divisions?.map((d: any) => <option key={d.id} value={d.id}>{c.name} - {d.name}</option>))}
            </select>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="p-8 flex justify-center"><Loader2 className="h-8 w-8 animate-spin" /></div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Date</TableHead>
                  <TableHead>Exam Name</TableHead>
                  <TableHead>Class</TableHead>
                  <TableHead>Subject</TableHead>
                  <TableHead>Max Marks</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {exams?.map((exam: any) => (
                  <TableRow key={exam.id}>
                    <TableCell>{exam.date}</TableCell>
                    <TableCell className="font-medium">{exam.name}</TableCell>
                    <TableCell>{exam.division_name}</TableCell>
                    <TableCell>{exam.subject_name}</TableCell>
                    <TableCell>{exam.max_marks}</TableCell>
                    <TableCell className="text-right">
                      <Button variant="outline" size="sm" onClick={() => setSelectedExam(exam)} className="mr-2">
                        <Edit3 className="h-4 w-4 mr-2" /> Enter Marks
                      </Button>
                      <Button variant="ghost" size="sm" onClick={() => handleDelete(exam.id)} className="text-red-500"><Trash2 className="h-4 w-4" /></Button>
                    </TableCell>
                  </TableRow>
                ))}
                {exams?.length === 0 && <TableRow><TableCell colSpan={6} className="text-center py-8 text-slate-500">No exams scheduled.</TableCell></TableRow>}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

function ExamResultsView({ exam, onBack }: { exam: any, onBack: () => void }) {
  const { data: results, isLoading } = useExamResults(exam.id)
  const { mutateAsync: saveResults, isPending } = useSaveExamResults()
  
  const [localScores, setLocalScores] = useState<Record<string, string>>({})

  useEffect(() => {
    if (results) {
      const map: Record<string, string> = {}
      results.forEach((r: any) => {
        map[r.student_id] = r.score !== null ? String(r.score) : ''
      })
      setLocalScores(map)
    }
  }, [results])

  const handleSave = async () => {
    const records = Object.entries(localScores).map(([studentId, scoreStr]) => ({
      student_id: studentId,
      score: scoreStr === '' ? null : Number(scoreStr),
      remarks: ''
    }))
    
    try {
      await saveResults({ examId: exam.id, records })
      toast.success('Marks saved successfully')
    } catch (error) {
      toast.error('Failed to save marks')
    }
  }

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <Button variant="link" onClick={onBack} className="p-0 h-auto mb-2 text-slate-500 hover:text-slate-900">&larr; Back to Exams</Button>
          <h2 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">{exam.name} Results</h2>
          <p className="text-slate-500">{exam.division_name} • {exam.subject_name} • Max Marks: {exam.max_marks}</p>
        </div>
        <Button onClick={handleSave} disabled={isPending} className="bg-blue-600">
          {isPending ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Save className="w-4 h-4 mr-2" />}
          Save Marks
        </Button>
      </div>

      <Card>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="p-8 flex justify-center"><Loader2 className="h-8 w-8 animate-spin" /></div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Admission No</TableHead>
                  <TableHead>Student Name</TableHead>
                  <TableHead className="w-[200px]">Marks Obtained</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {results?.map((r: any) => (
                  <TableRow key={r.student_id}>
                    <TableCell className="font-medium">{r.admission_number}</TableCell>
                    <TableCell>{r.student_name}</TableCell>
                    <TableCell>
                      <Input 
                        type="number" 
                        max={exam.max_marks}
                        min={0}
                        value={localScores[r.student_id] ?? ''}
                        onChange={(e) => setLocalScores(prev => ({...prev, [r.student_id]: e.target.value}))}
                        className="w-24"
                        placeholder="-"
                      />
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
