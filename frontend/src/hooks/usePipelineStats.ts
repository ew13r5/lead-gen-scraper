import { useApi } from "./useApi";
import * as api from "../api/client";
import type { PipelineStage } from "../types";

export function usePipelineStats(taskId: string | null) {
  const { data, isLoading, error, refetch } = useApi(
    () =>
      taskId
        ? api.getPipelineStats(taskId)
        : Promise.resolve({ task_id: "", stages: [] }),
    [taskId],
  );

  return {
    stages: (data?.stages ?? []) as PipelineStage[],
    isLoading,
    error,
    refetch,
  };
}
