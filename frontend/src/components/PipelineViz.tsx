import type { PipelineStage } from "../types";

interface PipelineVizProps {
  stages: PipelineStage[];
  isLoading?: boolean;
}

const STAGE_COLORS: Record<string, string> = {
  scraped: "border-l-blue-500",
  cleaned: "border-l-cyan-500",
  validated: "border-l-indigo-500",
  deduped: "border-l-purple-500",
  enriched: "border-l-amber-500",
  exported: "border-l-green-500",
};

function lossColor(loss: number, total: number): string {
  if (total === 0 || loss === 0) return "text-green-600";
  const pct = loss / total;
  if (pct >= 0.1) return "text-red-600";
  if (pct > 0) return "text-yellow-600";
  return "text-green-600";
}

export default function PipelineViz({ stages, isLoading }: PipelineVizProps) {
  if (isLoading) {
    return (
      <div className="flex items-center gap-4 py-4" data-testid="pipeline-viz">
        {[1, 2, 3, 4].map((i) => (
          <div
            key={i}
            className="bg-gray-200 animate-pulse rounded-lg h-20 min-w-[120px]"
          />
        ))}
      </div>
    );
  }

  if (stages.length === 0) {
    return (
      <p className="text-gray-500 text-sm py-4" data-testid="pipeline-viz">
        No pipeline data available.
      </p>
    );
  }

  return (
    <div
      className="flex items-center gap-2 py-4 overflow-x-auto"
      data-testid="pipeline-viz"
    >
      {stages.map((stage, i) => {
        const borderColor = STAGE_COLORS[stage.stage] ?? "border-l-gray-400";
        const prevOut = i > 0 ? stages[i - 1].count_out : null;
        const diff = prevOut !== null ? stage.count_out - prevOut : null;

        return (
          <div key={stage.stage} className="flex items-center gap-2">
            {i > 0 && (
              <div className="flex flex-col items-center min-w-[40px]">
                <span className="text-gray-400 text-lg">→</span>
                {diff !== null && (
                  <span
                    className={`text-xs font-medium ${lossColor(Math.abs(diff), prevOut!)}`}
                    data-testid={`arrow-${stage.stage}`}
                  >
                    {diff <= 0 ? diff : `+${diff}`}
                  </span>
                )}
              </div>
            )}
            <div
              className={`bg-white rounded-lg shadow p-4 min-w-[120px] text-center border-l-4 ${borderColor}`}
              data-testid={`stage-${stage.stage}`}
            >
              <p className="text-xs text-gray-500 uppercase tracking-wide">
                {stage.stage}
              </p>
              <p className="text-xl font-bold mt-1">{stage.count_out}</p>
            </div>
          </div>
        );
      })}
    </div>
  );
}
