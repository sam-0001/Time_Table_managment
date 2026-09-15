import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';

export function useStudents() {
  return useQuery({
    queryKey: ['students'],
    queryFn: async () => {
      const { data } = await api.get('/students/');
      return data;
    },
  });
}

export function useCreateStudent() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: any) => {
      const res = await api.post('/students/', data);
      return res.data;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['students'] }),
  });
}

export function useDeleteStudent() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const res = await api.delete(`/students/${id}`);
      return res.data;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['students'] }),
  });
}
