import React, { useState } from 'react'
import { useAttendance, useSaveAttendance } from '@/hooks/useAttendance'
import { useClasses } from '@/hooks/useClasses'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { toast } from 'sonner'
import { Loader2, Save, Check, X } from 'lucide-react'

export default function AttendancePage() {
  const { data: classes } = useClasses('temp-academic-year-id')
  
  const [selectedDivision, setSelectedDivision] = useState('')
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0])
  
  const { data: attendanceData, isLoading } = useAttendance(selectedDivision, selectedDate)
  const { mutateAsync: saveAttendance, isPending: isSaving } = useSaveAttendance()
  
  const [localRecords, setLocalRecords] = useState<Record<string, string>>({})

  // Sync local records when data loads
  React.useEffect(() => {
    if (attendanceData) {
      const map: Record<string, string> = {}
      attendanceData.forEach((a: any) => {
        map[a.student_id] = a.status
      })
      setLocalRecords(map)
    }
  }, [attendanceData])

  const handleStatusChange = (studentId: string, status: string) => {
    setLocalRecords(prev => ({ ...prev, [studentId]: status }))
  }

  const handleSave = async () => {
    if (!selectedDivision || !selectedDate) return
    
    const records = Object.entries(localRecords).map(([studentId, status]) => ({
      student_id: studentId,
      status: status,
      remarks: ''
    }))
    
    try {
      await saveAttendance({
        division_id: selectedDivision,
        date: selectedDate,
        records
      })
      toast.success('Attendance saved successfully')
    } catch (error) {
      toast.error('Failed to save attendance')
    }
  }

  const markAll = (status: string) => {
    if (!attendanceData) return
    const map: Record<string, string> = {}
    attendanceData.forEach((a: any) => {
      map[a.student_id] = status
    })
    setLocalRecords(map)
  }

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">Attendance</h2>
        </div>
      </div>

      <Card>
        <CardContent className="p-6">
          <div className="flex gap-4 items-end">
            <div className="w-1/3">
              <label className="block text-sm font-medium mb-2">Class & Division</label>
              <select 
                className="w-full p-2 border rounded-md"
                value={selectedDivision} 
                onChange={e => setSelectedDivision(e.target.value)}
              >
                <option value="">Select Division</option>
                {classes?.map((c: any) => 
                  c.divisions?.map((d: any) => (
                    <option key={d.id} value={d.id}>{c.name} - {d.name}</option>
                  ))
                )}
              </select>
            </div>
            
            <div className="w-1/3">
              <label className="block text-sm font-medium mb-2">Date</label>
              <input 
                type="date" 
                className="w-full p-2 border rounded-md"
                value={selectedDate}
                onChange={e => setSelectedDate(e.target.value)}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {selectedDivision && (
        <Card>
          <CardContent className="p-0">
            {isLoading ? (
              <div className="p-8 flex justify-center"><Loader2 className="h-8 w-8 animate-spin text-slate-400" /></div>
            ) : attendanceData?.length === 0 ? (
              <div className="p-8 text-center text-slate-500">No students found in this division.</div>
            ) : (
              <div>
                <div className="p-4 border-b flex justify-between items-center bg-slate-50 dark:bg-slate-800">
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm" onClick={() => markAll('PRESENT')} className="text-green-600"><Check className="mr-1 w-4 h-4" /> Mark All Present</Button>
                    <Button variant="outline" size="sm" onClick={() => markAll('ABSENT')} className="text-red-600"><X className="mr-1 w-4 h-4" /> Mark All Absent</Button>
                  </div>
                  <Button onClick={handleSave} disabled={isSaving} className="bg-blue-600">
                    {isSaving ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Save className="w-4 h-4 mr-2" />}
                    Save Attendance
                  </Button>
                </div>
                
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Admission No</TableHead>
                      <TableHead>Name</TableHead>
                      <TableHead>Status</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {attendanceData?.map((student: any) => {
                      const status = localRecords[student.student_id] || 'PRESENT'
                      return (
                        <TableRow key={student.student_id}>
                          <TableCell className="font-medium">{student.admission_number}</TableCell>
                          <TableCell>{student.student_name}</TableCell>
                          <TableCell>
                            <div className="flex gap-2">
                              <Button 
                                size="sm" 
                                variant={status === 'PRESENT' ? 'default' : 'outline'}
                                className={status === 'PRESENT' ? 'bg-green-600 hover:bg-green-700' : ''}
                                onClick={() => handleStatusChange(student.student_id, 'PRESENT')}
                              >
                                Present
                              </Button>
                              <Button 
                                size="sm" 
                                variant={status === 'ABSENT' ? 'destructive' : 'outline'}
                                onClick={() => handleStatusChange(student.student_id, 'ABSENT')}
                              >
                                Absent
                              </Button>
                              <Button 
                                size="sm" 
                                variant={status === 'LATE' ? 'default' : 'outline'}
                                className={status === 'LATE' ? 'bg-yellow-500 hover:bg-yellow-600 text-white' : ''}
                                onClick={() => handleStatusChange(student.student_id, 'LATE')}
                              >
                                Late
                              </Button>
                            </div>
                          </TableCell>
                        </TableRow>
                      )
                    })}
                  </TableBody>
                </Table>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
