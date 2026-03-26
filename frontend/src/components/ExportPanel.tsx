import { useState } from "react";
import * as api from "../api/client";

interface ExportPanelProps {
  taskId: string;
  disabled?: boolean;
}

type ExportFormat = "csv" | "excel" | "json";

export default function ExportPanel({ taskId, disabled }: ExportPanelProps) {
  const [loading, setLoading] = useState<Record<ExportFormat, boolean>>({
    csv: false,
    excel: false,
    json: false,
  });

  async function handleExport(format: ExportFormat) {
    setLoading((prev) => ({ ...prev, [format]: true }));
    try {
      const result = await api.triggerExport({ task_id: taskId, format });
      const url = api.downloadExportUrl(result.id);
      const a = document.createElement("a");
      a.href = url;
      a.download = "";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    } catch {
      // error handling could be added
    } finally {
      setLoading((prev) => ({ ...prev, [format]: false }));
    }
  }

  const buttons: { format: ExportFormat; label: string }[] = [
    { format: "csv", label: "CSV" },
    { format: "excel", label: "Excel" },
    { format: "json", label: "JSON" },
  ];

  return (
    <div className="flex gap-2" data-testid="export-panel">
      {buttons.map(({ format, label }) => (
        <button
          key={format}
          onClick={() => handleExport(format)}
          disabled={disabled || loading[format]}
          className="border border-gray-300 rounded-md px-3 py-1.5 text-sm hover:bg-gray-50 disabled:opacity-50"
          data-testid={`export-${format}`}
        >
          {loading[format] ? `${label}...` : label}
        </button>
      ))}
    </div>
  );
}
