import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';

export interface DailySchedule {
  day: number;
  is_working: boolean;
  periods: number;
  lunch_period: number | null;
}

export interface SchoolSettings {
  id: string;
  working_days: number;
  start_time: string;
  end_time: string;
  number_of_periods: number;
  period_duration: number;
  lunch_break_period: number;
  assembly_duration: number;
  total_weekly_periods: number;
  max_weekly_teacher_periods: number;
  weekly_schedule: DailySchedule[] | null;
}

export function useSettings() {
  return useQuery({
    queryKey: ['settings'],
    queryFn: async () => {
      const { data } = await api.get<SchoolSettings>('/school/settings');
      return data;
    },
  });
}

export function useUpdateSettings() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (input: Partial<SchoolSettings>) => {
      const { data } = await api.put<SchoolSettings>('/school/settings', input);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings'] });
    },
  });
}
