import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';

export interface Subject {
  id: string;
  class_id: string;
  name: string;
  code: string;
  weekly_periods: number;
  double_period_allowed: boolean;
  is_lab: boolean;
}

export interface CreateSubjectInput {
  class_id: string;
  name: string;
  code: string;
  weekly_periods: number;
  double_period_allowed: boolean;
  is_lab: boolean;
}

export interface UpdateSubjectInput {
  name?: string;
  code?: string;
  weekly_periods?: number;
  double_period_allowed?: boolean;
  is_lab?: boolean;
}

export function useSubjects(class_id?: string) {
  return useQuery({
    queryKey: ['subjects', class_id],
    queryFn: async () => {
      const params = class_id ? { class_id } : {};
      const { data } = await api.get<Subject[]>('/subjects/', { params });
      return data;
    },
  });
}

export function useCreateSubject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (input: CreateSubjectInput) => {
      const { data } = await api.post<Subject>('/subjects/', input);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['subjects'] });
    },
  });
}

export function useDeleteSubject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/subjects/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['subjects'] });
    },
  });
}

export function useUpdateSubject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: UpdateSubjectInput }) => {
      const response = await api.put<Subject>(`/subjects/${id}`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['subjects'] });
    },
  });
}
