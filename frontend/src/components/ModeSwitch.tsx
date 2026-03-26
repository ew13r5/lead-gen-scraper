import type { AppMode } from "../types";

interface ModeSwitchProps {
  mode: AppMode;
  onSwitch: (mode: AppMode) => void;
  isLoading?: boolean;
}

export default function ModeSwitch({
  mode,
  onSwitch,
  isLoading,
}: ModeSwitchProps) {
  return (
    <div className="inline-flex rounded-md border border-gray-300 bg-white" data-testid="mode-switch">
      <button
        onClick={() => onSwitch("live")}
        disabled={isLoading}
        className={`px-3 py-1.5 text-sm rounded-l-md flex items-center gap-1.5 transition-colors ${
          mode === "live"
            ? "bg-green-50 text-green-700 font-semibold"
            : "text-gray-500 hover:bg-gray-50"
        }`}
      >
        <span className="w-2 h-2 rounded-full bg-green-500" />
        Live
      </button>
      <button
        onClick={() => onSwitch("demo")}
        disabled={isLoading}
        className={`px-3 py-1.5 text-sm rounded-r-md flex items-center gap-1.5 transition-colors ${
          mode === "demo"
            ? "bg-orange-50 text-orange-700 font-semibold"
            : "text-gray-500 hover:bg-gray-50"
        }`}
      >
        <span className="w-2 h-2 rounded-full bg-orange-500" />
        Demo
      </button>
    </div>
  );
}
