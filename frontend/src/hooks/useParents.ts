import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';

export function useParents() {
  return useQuery({
    queryKey: ['parents'],
    queryFn: async () => {
      const { data } = await api.get('/parents/');
      return data;
    },
  });
}

export function useCreateParent() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: any) => {
      const res = await api.post('/parents/', data);
      return res.data;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['parents'] }),
  });
}

export function useDeleteParent() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const res = await api.delete(`/parents/${id}`);
      return res.data;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['parents'] }),
  });
}
