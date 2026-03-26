import { useMemo, useState, useCallback } from "react";
import { AgGridReact } from "ag-grid-react";
import { AllCommunityModule, ModuleRegistry, type ColDef, type CellValueChangedEvent } from "ag-grid-community";
import type { Company } from "../types";

ModuleRegistry.registerModules([AllCommunityModule]);

interface ResultsTableProps {
  results: Company[];
  onCellEdit?: (id: string, field: string, value: unknown) => void;
}

export default function ResultsTable({ results, onCellEdit }: ResultsTableProps) {
  const [quickFilter, setQuickFilter] = useState("");

  const columnDefs = useMemo<ColDef<Company>[]>(
    () => [
      { headerCheckboxSelection: true, checkboxSelection: true, width: 50, sortable: false, filter: false },
      { field: "company_name", headerName: "Company", sortable: true, filter: true, editable: true, flex: 2 },
      { field: "phone_display", headerName: "Phone", flex: 1 },
      { field: "email", headerName: "Email", editable: true, flex: 1.5 },
      { field: "website", headerName: "Website", flex: 1.5 },
      { field: "city", headerName: "City", filter: true, flex: 1 },
      { field: "state", headerName: "State", filter: true, width: 80 },
      { field: "category", headerName: "Category", filter: true, flex: 1 },
      { field: "rating", headerName: "Rating", sortable: true, width: 90 },
      { field: "source", headerName: "Source", filter: true, width: 110 },
      {
        field: "needs_review",
        headerName: "Review",
        width: 90,
        cellRenderer: (params: { value: boolean }) =>
          params.value ? "⚠️" : "✓",
      },
    ],
    [],
  );

  const onCellValueChanged = useCallback(
    (event: CellValueChangedEvent<Company>) => {
      if (onCellEdit && event.data && event.colDef.field) {
        onCellEdit(event.data.id, event.colDef.field, event.newValue);
      }
    },
    [onCellEdit],
  );

  return (
    <div data-testid="results-table">
      <div className="mb-3">
        <input
          type="text"
          value={quickFilter}
          onChange={(e) => setQuickFilter(e.target.value)}
          placeholder="Quick filter..."
          className="border border-gray-300 rounded-md px-3 py-2 text-sm w-64"
          data-testid="quick-filter"
        />
      </div>
      <div className="ag-theme-alpine" style={{ height: 600 }}>
        <AgGridReact<Company>
          rowData={results}
          columnDefs={columnDefs}
          quickFilterText={quickFilter}
          pagination={true}
          paginationPageSize={50}
          rowSelection="multiple"
          onCellValueChanged={onCellValueChanged}
          getRowId={(params) => params.data.id}
        />
      </div>
    </div>
  );
}
