import { useCallback, useState } from "react";
import { useApi } from "./useApi";
import * as api from "../api/client";
import type { AppMode } from "../types";

export function useMode() {
  const [optimisticMode, setOptimisticMode] = useState<AppMode | null>(null);
  const { data, isLoading, error, refetch } = useApi(() => api.getMode(), []);

  const mode = optimisticMode ?? data ?? "demo";

  const switchMode = useCallback(
    async (newMode: AppMode) => {
      setOptimisticMode(newMode);
      try {
        await api.setMode(newMode);
        refetch();
      } catch {
        setOptimisticMode(null);
        refetch();
      }
    },
    [refetch],
  );

  return {
    mode,
    isLoading,
    error,
    setMode: switchMode,
  };
}
