import { useState, useEffect, useRef, useCallback } from "react";
import { useApi } from "./useApi";
import * as api from "../api/client";
import type { ResultsFilter, Company } from "../types";

export function useResults(initialFilters: ResultsFilter = {}) {
  const [filters, setFilters] = useState<ResultsFilter>(initialFilters);
  const [page, setPage] = useState(1);
  const [debouncedSearch, setDebouncedSearch] = useState(filters.search);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (timerRef.current) clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => {
      setDebouncedSearch(filters.search);
    }, 300);
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [filters.search]);

  const effectiveFilters = { ...filters, search: debouncedSearch, page };

  const { data, isLoading, error, refetch } = useApi(
    () => api.getResults(effectiveFilters),
    [JSON.stringify(effectiveFilters)],
  );

  const updateFilters = useCallback((newFilters: Partial<ResultsFilter>) => {
    setFilters((prev) => ({ ...prev, ...newFilters }));
    setPage(1);
  }, []);

  return {
    results: (data?.items ?? []) as Company[],
    total: data?.total ?? 0,
    page,
    setPage,
    isLoading,
    error,
    filters,
    setFilters: updateFilters,
    refetch,
  };
}
