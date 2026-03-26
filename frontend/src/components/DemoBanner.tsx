import { useState } from "react";

interface DemoBannerProps {
  mode: string;
}

export default function DemoBanner({ mode }: DemoBannerProps) {
  const [dismissed, setDismissed] = useState(
    () => sessionStorage.getItem("demo-banner-dismissed") === "true",
  );

  if (mode !== "demo" || dismissed) return null;

  return (
    <div
      className="bg-amber-50 border border-amber-200 text-amber-800 px-4 py-2 rounded-md flex items-center justify-between mb-4"
      data-testid="demo-banner"
    >
      <span className="text-sm font-medium">
        Demo Mode — Data shown is simulated.
      </span>
      <button
        onClick={() => {
          sessionStorage.setItem("demo-banner-dismissed", "true");
          setDismissed(true);
        }}
        className="text-amber-600 hover:text-amber-800 text-sm ml-4"
      >
        Dismiss
      </button>
    </div>
  );
}
