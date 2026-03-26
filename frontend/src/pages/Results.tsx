import { useCallback } from "react";
import { useResults } from "../hooks/useResults";
import ResultsTable from "../components/ResultsTable";
import ExportPanel from "../components/ExportPanel";
import * as api from "../api/client";

export default function Results() {
  const {
    results,
    total,
    isLoading,
    filters,
    setFilters,
    refetch,
  } = useResults();

  const handleCellEdit = useCallback(
    async (id: string, field: string, value: unknown) => {
      await api.updateResult(id, { [field]: value } as Partial<typeof results[0]>);
      refetch();
    },
    [refetch],
  );

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold">Results</h2>
          <p className="text-sm text-gray-500 mt-1">
            {isLoading ? "Loading..." : `${total} companies`}
          </p>
        </div>
        {filters.task_id && (
          <ExportPanel taskId={filters.task_id} disabled={isLoading} />
        )}
      </div>

      <div className="flex gap-3 mb-4">
        <select
          value={filters.source ?? ""}
          onChange={(e) => setFilters({ source: e.target.value || undefined })}
          className="border border-gray-300 rounded-md px-3 py-2 text-sm"
        >
          <option value="">All Sources</option>
          <option value="yellowpages">Yellow Pages</option>
          <option value="yelp">Yelp</option>
          <option value="bbb">BBB</option>
          <option value="clutch">Clutch</option>
        </select>

        <select
          value={filters.needs_review === undefined ? "" : String(filters.needs_review)}
          onChange={(e) =>
            setFilters({
              needs_review: e.target.value === "" ? undefined : e.target.value === "true",
            })
          }
          className="border border-gray-300 rounded-md px-3 py-2 text-sm"
        >
          <option value="">All Records</option>
          <option value="true">Needs Review</option>
          <option value="false">Reviewed</option>
        </select>

        <input
          type="text"
          value={filters.search ?? ""}
          onChange={(e) => setFilters({ search: e.target.value || undefined })}
          placeholder="Search companies..."
          className="border border-gray-300 rounded-md px-3 py-2 text-sm flex-1"
        />
      </div>

      <ResultsTable results={results} onCellEdit={handleCellEdit} />
    </div>
  );
}
