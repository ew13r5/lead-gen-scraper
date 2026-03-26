interface ProgressBarProps {
  pagesProcessed: number;
  pagesTotal: number | null;
  itemsFound: number;
  errors: number;
  status: string;
}

export default function ProgressBar({
  pagesProcessed,
  pagesTotal,
  itemsFound,
  errors,
  status,
}: ProgressBarProps) {
  const indeterminate = !pagesTotal;
  const percent = pagesTotal ? Math.round((pagesProcessed / pagesTotal) * 100) : 0;

  const barColor =
    status === "completed"
      ? "bg-green-500"
      : status === "failed"
        ? "bg-red-500"
        : "bg-blue-500";

  return (
    <div data-testid="progress-bar">
      <div className="flex justify-between text-sm text-gray-600 mb-1">
        <span>
          {pagesTotal
            ? `Page ${pagesProcessed}/${pagesTotal} — ${itemsFound} items found`
            : `${pagesProcessed} pages processed — ${itemsFound} items found`}
        </span>
        <span>
          {errors > 0 && (
            <span className="text-red-500">{errors} errors</span>
          )}
        </span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
        {indeterminate ? (
          <div
            className={`h-full ${barColor} animate-pulse rounded-full`}
            style={{ width: "100%" }}
            data-testid="progress-fill"
          />
        ) : (
          <div
            className={`h-full ${barColor} rounded-full transition-all duration-500`}
            style={{ width: `${percent}%` }}
            data-testid="progress-fill"
          />
        )}
      </div>
      {!indeterminate && (
        <p className="text-xs text-gray-500 mt-1 text-right">{percent}%</p>
      )}
    </div>
  );
}
