import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';

export function useExams(divisionId?: string) {
  return useQuery({
    queryKey: ['exams', divisionId],
    queryFn: async () => {
      const url = divisionId ? `/exams/?division_id=${divisionId}` : `/exams/`;
      const { data } = await api.get(url);
      return data;
    },
  });
}

export function useCreateExam() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: any) => {
      const res = await api.post('/exams/', data);
      return res.data;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['exams'] }),
  });
}

export function useDeleteExam() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const res = await api.delete(`/exams/${id}`);
      return res.data;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['exams'] }),
  });
}

export function useExamResults(examId: string) {
  return useQuery({
    queryKey: ['exam_results', examId],
    queryFn: async () => {
      if (!examId) return [];
      const { data } = await api.get(`/exams/${examId}/results`);
      return data;
    },
    enabled: !!examId
  });
}

export function useSaveExamResults() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: { examId: string, records: any[] }) => {
      const res = await api.post(`/exams/${payload.examId}/results`, { records: payload.records });
      return res.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['exam_results', variables.examId] })
    },
  });
}
