import { useGenerateTimetable, useTimetable } from '@/hooks/useTimetable'
import { useSettings } from '@/hooks/useSettings'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

import { BookOpen, Users, CalendarDays, UserX, Loader2, Printer, Download } from 'lucide-react'
import * as XLSX from 'xlsx'
import { toast } from 'sonner'
import { useNavigate } from 'react-router-dom'
import React, { useState } from 'react'
import { useClasses } from '@/hooks/useClasses'
import { useTeachers } from '@/hooks/useTeachers'

const TEMP_ACADEMIC_YEAR_ID = "temp-academic-year-id" 

export default function Dashboard() {
  const { mutateAsync: generateTimetable, isPending: isGenerating } = useGenerateTimetable()
  const { data: timetable, isLoading: isLoadingTimetable } = useTimetable(TEMP_ACADEMIC_YEAR_ID)
  const { data: settings } = useSettings()
  const { data: classes } = useClasses(TEMP_ACADEMIC_YEAR_ID)
  const { data: teachers } = useTeachers()
  const navigate = useNavigate()

  const [viewMode, setViewMode] = useState<'division' | 'teacher' | 'master'>('division')
  const [selectedDivisionId, setSelectedDivisionId] = useState<string>('')
  const [selectedTeacherId, setSelectedTeacherId] = useState<string>('')

  const allDays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
  
  const scheduleConfig = settings?.weekly_schedule || []
  const activeDaysConfig = scheduleConfig.filter(d => d.is_working)
  const daysOfWeek = activeDaysConfig.length > 0 ? activeDaysConfig.map(d => allDays[d.day]) : ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
  const maxPeriods = activeDaysConfig.length > 0 ? Math.max(...activeDaysConfig.map(d => d.periods)) : (settings?.number_of_periods || 7)
  const periods = Array.from({length: maxPeriods}, (_, i) => i)
  const globalLunchPeriod = activeDaysConfig.find(d => d.lunch_period !== null)?.lunch_period ?? (settings?.lunch_break_period ?? -1)

  const handleGenerate = async () => {
    try {
      const res = await generateTimetable(TEMP_ACADEMIC_YEAR_ID)
      toast.success(res.message || 'Timetable generated successfully')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to generate timetable. Ensure sufficient teachers and subjects are added.')
    }
  }

  const exportToExcel = () => {
    if (!timetable || timetable.length === 0) {
      toast.error("No timetable data to export.")
      return
    }

    const rows = []
    
    // Header section
    let title = "School Timetable"
    let subtitle = ""
    if (viewMode === 'division' && selectedDivisionId) {
      const div = classes?.flatMap(c => c.divisions).find(d => d.id === selectedDivisionId)
      const c = classes?.find(cl => cl.divisions.some(d => d.id === selectedDivisionId))
      const classTeacher = teachers?.find(t => t.class_teacher_of_division_id === selectedDivisionId)
      
      title = `Class: ${c?.name || ''}`
      subtitle = `Division: ${div?.name || ''} ${classTeacher ? '| Class Teacher: ' + (classTeacher.name || classTeacher.employee_id) : ''}`
    } else if (viewMode === 'teacher' && selectedTeacherId) {
      const t = teachers?.find(t => t.id === selectedTeacherId)
      title = `Teacher: ${t?.name || t?.employee_id || ''}`
    }

    rows.push([title])
    if (subtitle) rows.push([subtitle])
    rows.push([]) // Empty row

    // Table Headers
    const daysToRender = activeDaysConfig.length > 0 ? activeDaysConfig : daysOfWeek.map((_, i) => ({ day: i, periods: maxPeriods, lunch_period: globalLunchPeriod }))
    
    const tableHeader = ["Period"]
    daysToRender.forEach(dayConfig => {
      tableHeader.push(allDays[dayConfig.day])
    })
    rows.push(tableHeader)

    // Find the unique lunch periods to handle the break row
    const isStandardLunch = daysToRender.every(d => d.lunch_period === globalLunchPeriod)

    periods.forEach(p => {
      // Lunch break row?
      if (isStandardLunch && p === globalLunchPeriod) {
        const lunchRow = ["LUNCH BREAK"]
        daysToRender.forEach(() => lunchRow.push("-"))
        rows.push(lunchRow)
      }

      const row = [(p + 1).toString()]

      daysToRender.forEach(dayConfig => {
        // If lunch period is not standard and this is a lunch period for this specific day, handle it in the cell
        if (!isStandardLunch && p === dayConfig.lunch_period) {
          row.push("LUNCH BREAK")
          return
        }

        if (p >= (dayConfig.periods || maxPeriods)) {
          row.push("XXXXXXX")
        } else {
          let slots = timetable.filter(t => t.day === dayConfig.day && t.period === p)
          
          if (viewMode === 'division' && selectedDivisionId) {
            slots = slots.filter(t => t.division_id === selectedDivisionId)
          } else if (viewMode === 'teacher' && selectedTeacherId) {
            slots = slots.filter(t => t.teacher_id === selectedTeacherId)
          } else if (viewMode !== 'master') {
            slots = []
          }

          if (slots.length === 0 && viewMode !== 'master' && (selectedDivisionId || selectedTeacherId)) {
            row.push("-")
          } else if (slots.length > 0) {
            const cellLines = slots.map(slot => {
              if (viewMode === 'teacher') return `${slot.subject_name}\n(${slot.class_name}-${slot.division_name})`
              if (viewMode === 'division') return `${slot.subject_name}\n${slot.teacher_name}`
              return `${slot.subject_name}\n${slot.class_name}-${slot.division_name} (${slot.teacher_name})`
            })
            row.push(cellLines.join("\n\n"))
          } else {
            row.push(`Select ${viewMode}`)
          }
        }
      })
      rows.push(row)
    })

    const ws = XLSX.utils.aoa_to_sheet(rows)
    
    // Formatting: Adjust column widths
    const colWidths = [{ wch: 8 }] // Period col
    for (let i = 0; i < daysToRender.length; i++) colWidths.push({ wch: 20 })
    ws['!cols'] = colWidths

    const wb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(wb, ws, "Timetable")
    
    let filename = "Timetable"
    if (viewMode === 'division' && selectedDivisionId) {
      const div = classes?.flatMap(c => c.divisions).find(d => d.id === selectedDivisionId)
      if (div) filename += `_Div_${div.name}`
    } else if (viewMode === 'teacher' && selectedTeacherId) {
      const t = teachers?.find(t => t.id === selectedTeacherId)
      if (t) filename += `_Teacher_${t.name || t.employee_id}`
    }
    
    XLSX.writeFile(wb, `${filename}.xlsx`)
  }

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 font-sans print:bg-white print:min-h-0">
      <div className="border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 print:hidden">
        <div className="flex h-16 items-center px-8">
          <h1 className="text-xl font-bold tracking-tight text-slate-900 dark:text-white flex items-center gap-2">
            <CalendarDays className="h-6 w-6 text-blue-600" />
            Timetable Engine
          </h1>
          <div className="ml-auto flex items-center space-x-4">
            <Button variant="outline" size="sm">Admin</Button>
          </div>
        </div>
      </div>
      
      <div className="p-8 max-w-7xl mx-auto space-y-8 print:p-0 print:m-0 print:max-w-none print:space-y-4">
        <div className="flex justify-between items-center print:hidden">
          <div>
            <h2 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">Dashboard</h2>
            <p className="text-slate-500 mt-1">Overview of your school's scheduling metrics.</p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => navigate('/leaves')}>Mark Leave</Button>
            <Button className="bg-blue-600 hover:bg-blue-700" onClick={handleGenerate} disabled={isGenerating}>
              {isGenerating ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <CalendarDays className="mr-2 h-4 w-4" />}
              {isGenerating ? 'Running Solver...' : 'Generate Timetable'}
            </Button>
          </div>
        </div>
        
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 print:hidden">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Teachers</CardTitle>
              <Users className="h-4 w-4 text-slate-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">Manage via Teachers</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Classes</CardTitle>
              <BookOpen className="h-4 w-4 text-slate-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">Manage via Classes</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Teachers on Leave (Today)</CardTitle>
              <UserX className="h-4 w-4 text-rose-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">See Leaves tab</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Timetable Health</CardTitle>
              <CalendarDays className="h-4 w-4 text-emerald-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-emerald-600">Pending Run</div>
            </CardContent>
          </Card>
        </div>
        
        <Tabs defaultValue="timetable" className="space-y-4">
          <TabsList className="bg-slate-100 dark:bg-slate-800 print:hidden">
            <TabsTrigger value="timetable">School Timetable</TabsTrigger>
            <TabsTrigger value="arrangements">Daily Arrangements</TabsTrigger>
            <TabsTrigger value="teachers">Teacher Workload</TabsTrigger>
          </TabsList>
          
          <TabsContent value="timetable" className="space-y-4">
            <Card className="border-slate-200 dark:border-slate-800 shadow-sm print:border-none print:shadow-none">
              <CardHeader className="flex flex-row items-center justify-between pb-2 print:hidden">
                <div>
                  <CardTitle>Timetable Viewer</CardTitle>
                  <CardDescription>Select a view mode to filter the schedule.</CardDescription>
                </div>
                <div className="flex gap-4 items-center">
                  <select
                    value={viewMode}
                    onChange={(e) => setViewMode(e.target.value as any)}
                    className="flex h-10 w-[180px] rounded-md border border-slate-300 bg-transparent px-3 py-2 text-sm placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-400 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 dark:border-slate-700 dark:text-slate-50 dark:focus:ring-slate-400 dark:focus:ring-offset-slate-900"
                  >
                    <option value="division">Division-wise</option>
                    <option value="teacher">Teacher-wise</option>
                    <option value="master">Master (All)</option>
                  </select>

                  {viewMode === 'division' && (
                    <select
                      value={selectedDivisionId}
                      onChange={(e) => setSelectedDivisionId(e.target.value)}
                      className="flex h-10 w-[180px] rounded-md border border-slate-300 bg-transparent px-3 py-2 text-sm placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-400 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 dark:border-slate-700 dark:text-slate-50 dark:focus:ring-slate-400 dark:focus:ring-offset-slate-900"
                    >
                      <option value="">Select Class</option>
                      {classes?.flatMap(c => 
                        c.divisions.map(d => (
                          <option key={d.id} value={d.id}>{c.name} - {d.name}</option>
                        ))
                      )}
                    </select>
                  )}

                  {viewMode === 'teacher' && (
                    <select
                      value={selectedTeacherId}
                      onChange={(e) => setSelectedTeacherId(e.target.value)}
                      className="flex h-10 w-[180px] rounded-md border border-slate-300 bg-transparent px-3 py-2 text-sm placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-400 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 dark:border-slate-700 dark:text-slate-50 dark:focus:ring-slate-400 dark:focus:ring-offset-slate-900"
                    >
                      <option value="">Select Teacher</option>
                      {teachers?.map(t => (
                        <option key={t.id} value={t.id}>{t.name || t.employee_id}</option>
                      ))}
                    </select>
                  )}

                  <Button variant="outline" size="icon" onClick={() => window.print()} title="Print PDF">
                    <Printer className="h-4 w-4" />
                  </Button>
                  <Button variant="outline" size="icon" onClick={exportToExcel} title="Export Excel">
                    <Download className="h-4 w-4" />
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="print:p-0">
                {isLoadingTimetable ? (
                  <div className="h-[400px] flex items-center justify-center border border-dashed border-slate-300 dark:border-slate-700 rounded-lg bg-slate-50 dark:bg-slate-900/50">
                    <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
                  </div>
                ) : !timetable || timetable.length === 0 ? (
                  <div className="h-[400px] flex items-center justify-center border border-dashed border-slate-300 dark:border-slate-700 rounded-lg bg-slate-50 dark:bg-slate-900/50">
                    <p className="text-sm text-slate-500">Run the solver to populate this grid.</p>
                  </div>
                ) : (
                  <div className="overflow-x-auto border rounded-lg border-slate-200 dark:border-slate-800 print:border-none print:overflow-visible">
                    <table className="w-full text-sm text-left print:text-xs">
                      <thead className="bg-slate-100 dark:bg-slate-900 border-b dark:border-slate-800">
                        <tr>
                          <th className="p-3 text-left font-semibold text-slate-700 dark:text-slate-300 w-32 border-r dark:border-slate-800">Day</th>
                          {periods.map(p => (
                            <React.Fragment key={p}>
                              {p === globalLunchPeriod && (
                                <th className="p-3 text-center font-bold text-orange-700 bg-orange-100 dark:bg-orange-900/40 dark:text-orange-400 border-r dark:border-slate-800 w-16 whitespace-nowrap" style={{ writingMode: 'vertical-rl', transform: 'rotate(180deg)' }}>
                                  Lunch Break
                                </th>
                              )}
                              <th className="p-3 text-left font-semibold text-slate-700 dark:text-slate-300 min-w-[150px] border-r dark:border-slate-800">Period {p + 1}</th>
                            </React.Fragment>
                          ))}
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-200 dark:divide-slate-800">
                        {activeDaysConfig.length > 0 ? activeDaysConfig.map((dayConfig, idx) => (
                          <tr key={idx}>
                            <td className="p-3 font-medium bg-slate-50 dark:bg-slate-900/50 border-r dark:border-slate-800">
                              {allDays[dayConfig.day]}
                            </td>
                            {periods.map(p => {
                              let cellContent = null
                              
                              if (p >= dayConfig.periods) {
                                cellContent = <td key={`slot-${p}`} className="p-2 border-r dark:border-slate-800 bg-slate-100 dark:bg-slate-900/30 text-center text-slate-400 text-xs">No Period</td>
                              } else {
                                let slots = timetable.filter(t => t.day === dayConfig.day && t.period === p)
                                if (viewMode === 'division' && selectedDivisionId) {
                                  slots = slots.filter(t => t.division_id === selectedDivisionId)
                                } else if (viewMode === 'teacher' && selectedTeacherId) {
                                  slots = slots.filter(t => t.teacher_id === selectedTeacherId)
                                } else if (viewMode !== 'master') {
                                  slots = [] // Empty until selected
                                }

                                if (slots.length === 0 && viewMode !== 'master' && (selectedDivisionId || selectedTeacherId)) {
                                  cellContent = <td key={`slot-${p}`} className="p-2 border-r dark:border-slate-800 text-center text-slate-300 dark:text-slate-700">-</td>
                                } else {
                                  cellContent = (
                                    <td key={`slot-${p}`} className="p-2 border-r dark:border-slate-800 min-w-[150px] align-top">
                                      {slots.length > 0 ? slots.map(slot => (
                                        <div key={slot.id} className="mb-2 p-2 bg-blue-50 dark:bg-blue-900/20 border border-blue-100 dark:border-blue-800 rounded text-xs text-center flex flex-col justify-center h-full">
                                          <div className="font-bold text-slate-900 dark:text-white text-sm mb-1">{slot.subject_name}</div>
                                          {viewMode === 'teacher' && (
                                            <div className="text-slate-700 dark:text-slate-300 font-medium">{slot.class_name}-{slot.division_name}</div>
                                          )}
                                          {viewMode === 'division' && (
                                            <div className="text-slate-600 dark:text-slate-400 font-medium">{slot.teacher_name}</div>
                                          )}
                                          {viewMode === 'master' && (
                                            <>
                                              <div className="text-slate-700 dark:text-slate-300">{slot.class_name}-{slot.division_name}</div>
                                              <div className="text-slate-500 mt-1">{slot.teacher_name}</div>
                                            </>
                                          )}
                                        </div>
                                      )) : (
                                        <div className="text-center text-slate-300 dark:text-slate-700 flex items-center justify-center h-full">Select {viewMode}</div>
                                      )}
                                    </td>
                                  )
                                }
                              }

                              return (
                                <React.Fragment key={p}>
                                  {p === globalLunchPeriod && (
                                    <td className="p-2 border-r dark:border-slate-800 bg-orange-50 dark:bg-orange-900/20 text-center text-orange-600 dark:text-orange-400 font-medium text-xs">
                                      {dayConfig.lunch_period === globalLunchPeriod ? 'Lunch' : '-'}
                                    </td>
                                  )}
                                  {cellContent}
                                </React.Fragment>
                              )
                            })}
                          </tr>
                        )) : daysOfWeek.map((dayName, dayIndex) => (
                          <tr key={dayIndex}>
                            <td className="p-3 font-medium bg-slate-50 dark:bg-slate-900/50 border-r dark:border-slate-800">
                              {dayName}
                            </td>
                            {periods.map(p => {
                              let slots = timetable.filter(t => t.day === dayIndex && t.period === p)
                              if (viewMode === 'division' && selectedDivisionId) {
                                slots = slots.filter(t => t.division_id === selectedDivisionId)
                              } else if (viewMode === 'teacher' && selectedTeacherId) {
                                slots = slots.filter(t => t.teacher_id === selectedTeacherId)
                              } else if (viewMode !== 'master') {
                                slots = []
                              }

                              let cellContent = null
                              if (slots.length === 0 && viewMode !== 'master' && (selectedDivisionId || selectedTeacherId)) {
                                cellContent = <td key={`slot-${p}`} className="p-2 border-r dark:border-slate-800 text-center text-slate-300 dark:text-slate-700">-</td>
                              } else {
                                cellContent = (
                                  <td key={`slot-${p}`} className="p-2 border-r dark:border-slate-800 min-w-[150px] align-top">
                                    {slots.length > 0 ? slots.map(slot => (
                                      <div key={slot.id} className="mb-2 p-2 bg-blue-50 dark:bg-blue-900/20 border border-blue-100 dark:border-blue-800 rounded text-xs text-center flex flex-col justify-center h-full">
                                        <div className="font-bold text-slate-900 dark:text-white text-sm mb-1">{slot.subject_name}</div>
                                        {viewMode === 'teacher' && (
                                          <div className="text-slate-700 dark:text-slate-300 font-medium">{slot.class_name}-{slot.division_name}</div>
                                        )}
                                        {viewMode === 'division' && (
                                          <div className="text-slate-600 dark:text-slate-400 font-medium">{slot.teacher_name}</div>
                                        )}
                                        {viewMode === 'master' && (
                                          <>
                                            <div className="text-slate-700 dark:text-slate-300">{slot.class_name}-{slot.division_name}</div>
                                            <div className="text-slate-500 mt-1">{slot.teacher_name}</div>
                                          </>
                                        )}
                                      </div>
                                    )) : (
                                      <div className="text-center text-slate-300 dark:text-slate-700 flex items-center justify-center h-full">Select {viewMode}</div>
                                    )}
                                  </td>
                                )
                              }

                              return (
                                <React.Fragment key={p}>
                                  {p === globalLunchPeriod && (
                                    <td className="p-2 border-r dark:border-slate-800 bg-orange-50 dark:bg-orange-900/20 text-center text-orange-600 dark:text-orange-400 font-medium text-xs">
                                      Lunch
                                    </td>
                                  )}
                                  {cellContent}
                                </React.Fragment>
                              )
                            })}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
          
          <TabsContent value="arrangements" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Today's Substitutions</CardTitle>
                <CardDescription>Auto-generated arrangements for absent teachers.</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center p-8 text-slate-500">
                  Visit the "Leaves & Arr." tab to generate.
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
