import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useState, useEffect } from 'react'
import { toast } from 'sonner'
import { Loader2, Save } from 'lucide-react'
import { useSettings, useUpdateSettings, DailySchedule } from '@/hooks/useSettings'
import { Checkbox } from '@/components/ui/checkbox'

export default function SettingsPage() {
  const { data: settings, isLoading } = useSettings()
  const { mutateAsync: updateSettings, isPending: isSaving } = useUpdateSettings()
  
  const [formData, setFormData] = useState({
    start_time: '08:00',
    end_time: '14:00',
    period_duration: 45,
    assembly_duration: 15,
    total_weekly_periods: 40,
    max_weekly_teacher_periods: 32,
  })
  
  const defaultSchedule: DailySchedule[] = [
    { day: 0, is_working: true, periods: 7, lunch_period: 4 },
    { day: 1, is_working: true, periods: 7, lunch_period: 4 },
    { day: 2, is_working: true, periods: 7, lunch_period: 4 },
    { day: 3, is_working: true, periods: 7, lunch_period: 4 },
    { day: 4, is_working: true, periods: 7, lunch_period: 4 },
    { day: 5, is_working: false, periods: 4, lunch_period: null },
    { day: 6, is_working: false, periods: 0, lunch_period: null },
  ]
  const [schedule, setSchedule] = useState<DailySchedule[]>(defaultSchedule)
  
  useEffect(() => {
    if (settings) {
      setFormData({
        start_time: settings.start_time,
        end_time: settings.end_time,
        period_duration: settings.period_duration,
        assembly_duration: settings.assembly_duration,
        total_weekly_periods: settings.total_weekly_periods || 40,
        max_weekly_teacher_periods: settings.max_weekly_teacher_periods || 32,
      })
      if (settings.weekly_schedule && settings.weekly_schedule.length === 7) {
        setSchedule(settings.weekly_schedule)
      }
    }
  }, [settings])

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await updateSettings({
        ...formData,
        weekly_schedule: schedule
      })
      toast.success('Settings saved successfully')
    } catch (error) {
      toast.error('Failed to save settings')
    }
  }

  const daysOfWeek = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

  if (isLoading) return <div className="p-8 flex justify-center"><Loader2 className="h-8 w-8 animate-spin text-blue-500" /></div>

  return (
    <div className="p-8 max-w-4xl mx-auto space-y-6 animate-in fade-in">
      <div>
        <h2 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">Settings</h2>
        <p className="text-slate-500 mt-1">Configure global school timings and timetable preferences.</p>
      </div>

      <form onSubmit={handleSave}>
        <Card>
          <CardHeader>
            <CardTitle>School Timings</CardTitle>
            <CardDescription>These settings govern how the timetable engine allocates periods.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-2 gap-6 mb-8">
              <div className="space-y-2">
                <label className="text-sm font-medium">Start Time</label>
                <Input type="time" required value={formData.start_time} onChange={e => setFormData({...formData, start_time: e.target.value})} />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">End Time</label>
                <Input type="time" required value={formData.end_time} onChange={e => setFormData({...formData, end_time: e.target.value})} />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Period Duration (mins)</label>
                <Input type="number" required value={formData.period_duration} onChange={e => setFormData({...formData, period_duration: parseInt(e.target.value)})} />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Assembly Duration (mins)</label>
                <Input type="number" required value={formData.assembly_duration} onChange={e => setFormData({...formData, assembly_duration: parseInt(e.target.value)})} />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Total Weekly Periods Target</label>
                <Input type="number" required value={formData.total_weekly_periods} onChange={e => setFormData({...formData, total_weekly_periods: parseInt(e.target.value)})} />
                <p className="text-xs text-slate-500">Expected total periods (e.g. 45 or 48) used for workload planning.</p>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Global Max Weekly Teacher Workload</label>
                <Input type="number" required value={formData.max_weekly_teacher_periods} onChange={e => setFormData({...formData, max_weekly_teacher_periods: parseInt(e.target.value)})} />
                <p className="text-xs text-slate-500">The baseline maximum periods a teacher should teach per week.</p>
              </div>
            </div>

            <div className="space-y-4">
              <h3 className="text-lg font-semibold border-b pb-2">Weekly Schedule Configurator</h3>
              <p className="text-sm text-slate-500 mb-4">Define working days, custom periods, and lunch breaks per day. E.g. half-days on Saturday.</p>
              
              <div className="border rounded-md divide-y overflow-hidden">
                <div className="grid grid-cols-12 gap-4 p-3 bg-slate-50 font-medium text-sm">
                  <div className="col-span-3">Day</div>
                  <div className="col-span-2 text-center">Working?</div>
                  <div className="col-span-3">Total Periods</div>
                  <div className="col-span-4">Lunch Break (After Period)</div>
                </div>
                {schedule.map((dayConfig, idx) => (
                  <div key={idx} className="grid grid-cols-12 gap-4 p-3 items-center text-sm hover:bg-slate-50/50">
                    <div className="col-span-3 font-medium">{daysOfWeek[dayConfig.day]}</div>
                    <div className="col-span-2 flex justify-center">
                      <Checkbox 
                        checked={dayConfig.is_working} 
                        onCheckedChange={(checked) => {
                          const newSched = [...schedule]
                          newSched[idx].is_working = checked === true
                          setSchedule(newSched)
                        }}
                      />
                    </div>
                    <div className="col-span-3">
                      <Input 
                        type="number" min={0} max={15} 
                        disabled={!dayConfig.is_working}
                        value={dayConfig.periods} 
                        onChange={(e) => {
                          const newSched = [...schedule]
                          newSched[idx].periods = parseInt(e.target.value) || 0
                          setSchedule(newSched)
                        }}
                        className="h-8"
                      />
                    </div>
                    <div className="col-span-4">
                      <Input 
                        type="number" min={0} max={15}
                        disabled={!dayConfig.is_working}
                        value={dayConfig.lunch_period === null ? '' : dayConfig.lunch_period} 
                        placeholder="e.g. 4"
                        onChange={(e) => {
                          const newSched = [...schedule]
                          newSched[idx].lunch_period = e.target.value ? parseInt(e.target.value) : null
                          setSchedule(newSched)
                        }}
                        className="h-8"
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="flex justify-end pt-4">
              <Button type="submit" disabled={isSaving} className="bg-blue-600 hover:bg-blue-700">
                {isSaving ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Save className="mr-2 h-4 w-4" />}
                Save Settings
              </Button>
            </div>
          </CardContent>
        </Card>
      </form>
    </div>
  )
}
