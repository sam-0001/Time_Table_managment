import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';

export interface Teacher {
  id: string;
  name: string | null;
  email: string | null;
  employee_id: string;
  mobile: string | null;
  qualification: string | null;
  assignments: {subject_id: string; division_id: string}[];
  max_daily_periods: number;
  max_weekly_periods: number;
  is_active: boolean;
  class_teacher_of_division_id: string | null;
}

export interface CreateTeacherInput {
  name: string;
  email: string;
  employee_id: string;
  mobile?: string;
  qualification?: string;
  assignments: {subject_id: string; division_id: string}[];
  max_daily_periods?: number;
  max_weekly_periods?: number;
  class_teacher_of_division_id?: string | null;
}

export interface UpdateTeacherInput {
  name?: string;
  email?: string;
  mobile?: string;
  qualification?: string;
  assignments?: {subject_id: string; division_id: string}[];
  max_daily_periods?: number;
  max_weekly_periods?: number;
  is_active?: boolean;
  class_teacher_of_division_id?: string | null;
}

export function useTeachers() {
  return useQuery({
    queryKey: ['teachers'],
    queryFn: async () => {
      const { data } = await api.get<Teacher[]>('/teachers/');
      return data;
    },
  });
}

export function useCreateTeacher() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (input: CreateTeacherInput) => {
      const { data } = await api.post<Teacher>('/teachers/', input);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['teachers'] });
    },
  });
}

export function useDeleteTeacher() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/teachers/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['teachers'] });
    },
  });
}

export function useUpdateTeacher() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: UpdateTeacherInput }) => {
      const { data: responseData } = await api.put<Teacher>(`/teachers/${id}`, data);
      return responseData;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['teachers'] });
    },
  });
}
