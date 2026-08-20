import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query';
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

export function useLeaves(date: string) {
  return useQuery({
    queryKey: ['leaves', date],
    queryFn: async () => {
      const { data } = await api.get(`/leaves/?date=${date}`);
      return data;
    },
  });
}

export function useArrangements(date: string) {
  return useQuery({
    queryKey: ['arrangements', date],
    queryFn: async () => {
      const { data } = await api.get(`/leaves/arrangements?date=${date}`);
      return data;
    },
  });
}

export function useDeleteLeave() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (leave_id: string) => {
      await api.delete(`/leaves/${leave_id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['leaves'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard_metrics'] });
    },
  });
}
