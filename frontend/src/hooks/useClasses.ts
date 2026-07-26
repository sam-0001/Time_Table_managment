import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';

export interface Division {
  id: string;
  class_id: string;
  name: string;
  class_teacher_id: string | null;
  classroom_id: string | null;
}

export interface SchoolClass {
  id: string;
  academic_year_id: string;
  name: string;
  level: number;
  divisions: Division[];
}

export interface CreateClassInput {
  academic_year_id: string;
  name: string;
  level: number;
  divisions: {
    name: string;
    class_teacher_id?: string | null;
    classroom_id?: string | null;
  }[];
}

export function useClasses(academic_year_id?: string) {
  return useQuery({
    queryKey: ['classes', academic_year_id],
    queryFn: async () => {
      const params = academic_year_id ? { academic_year_id } : {};
      const { data } = await api.get<SchoolClass[]>('/classes/', { params });
      return data;
    },
  });
}

export function useCreateClass() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (input: CreateClassInput) => {
      const { data } = await api.post<SchoolClass>('/classes/', input);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['classes'] });
    },
  });
}

export function useUpdateClass() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, data }: { id: string, data: CreateClassInput }) => {
      const { data: res } = await api.put<SchoolClass>(`/classes/${id}`, data);
      return res;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['classes'] });
    },
  });
}

export function useDeleteClass() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/classes/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['classes'] });
    },
  });
}
