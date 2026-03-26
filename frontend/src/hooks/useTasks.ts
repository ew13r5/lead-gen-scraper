import { useCallback, useState } from "react";
import { useApi } from "./useApi";
import * as api from "../api/client";
import type { ScrapeTask, CreateTaskPayload } from "../types";

export function useTasks() {
  const [page, setPage] = useState(1);
  const {
    data,
    isLoading,
    error,
    refetch,
  } = useApi(() => api.getTasks(page), [page]);

  const createTask = useCallback(
    async (payload: CreateTaskPayload): Promise<ScrapeTask> => {
      const task = await api.createTask(payload);
      refetch();
      return task;
    },
    [refetch],
  );

  const deleteTask = useCallback(
    async (id: string): Promise<void> => {
      await api.deleteTask(id);
      refetch();
    },
    [refetch],
  );

  return {
    tasks: data?.items ?? [],
    total: data?.total ?? 0,
    page,
    setPage,
    isLoading,
    error,
    createTask,
    deleteTask,
    refetch,
  };
}
