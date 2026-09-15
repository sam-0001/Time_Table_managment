import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';

export function useAttendance(divisionId: string, date: string) {
  return useQuery({
    queryKey: ['attendance', divisionId, date],
    queryFn: async () => {
      if (!divisionId || !date) return [];
      const { data } = await api.get(`/attendance/?division_id=${divisionId}&date=${date}`);
      return data;
    },
    enabled: !!divisionId && !!date,
  });
}

export function useSaveAttendance() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: { division_id: string, date: string, records: any[] }) => {
      const res = await api.post('/attendance/', data);
      return res.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['attendance', variables.division_id, variables.date] })
    },
  });
}
