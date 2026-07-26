import { useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';

export interface MarkLeaveInput {
  teacher_id: string;
  date: string;
  reason?: string;
}

export function useMarkLeave() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (input: MarkLeaveInput) => {
      const { data } = await api.post('/leaves/', input);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dashboard_metrics'] });
    },
  });
}

export function useGenerateArrangements() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (target_date: string) => {
      const { data } = await api.post(`/leaves/generate-arrangements?target_date=${target_date}`);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['arrangements'] });
    },
  });
}
