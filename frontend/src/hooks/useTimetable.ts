import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';

export interface TimetableSlot {
  id: string;
  division_id: string;
  division_name: string;
  class_name: string;
  subject_id: string;
  subject_name: string;
  teacher_id: string;
  teacher_name: string;
  day: number;
  period: number;
}

export function useTimetable(academic_year_id: string) {
  return useQuery({
    queryKey: ['timetable', academic_year_id],
    queryFn: async () => {
      const { data } = await api.get<TimetableSlot[]>(`/timetable/?academic_year_id=${academic_year_id}`);
      return data;
    },
    enabled: !!academic_year_id
  });
}

export function useGenerateTimetable() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (academic_year_id: string) => {
      const { data } = await api.post(`/timetable/generate?academic_year_id=${academic_year_id}`);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['timetable'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard_metrics'] });
    },
  });
}
