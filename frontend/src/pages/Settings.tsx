import { useEffect, useState } from "react";
import { useMode } from "../hooks/useMode";
import ModeSwitch from "../components/ModeSwitch";
import * as api from "../api/client";
import type { Source } from "../types";

export default function Settings() {
  const { mode, setMode, isLoading: modeLoading } = useMode();
  const [sources, setSources] = useState<Source[]>([]);
  const [validating, setValidating] = useState<Record<string, string | null>>({});

  useEffect(() => {
    api.getSources().then(setSources).catch(() => {});
  }, []);

  async function handleValidate(name: string) {
    setValidating((prev) => ({ ...prev, [name]: "checking" }));
    try {
      const res = await fetch(`/api/v1/sources/${name}/validate`, {
        method: "POST",
      });
      if (res.ok) {
        setValidating((prev) => ({ ...prev, [name]: "ok" }));
      } else {
        setValidating((prev) => ({ ...prev, [name]: "error" }));
      }
    } catch {
      setValidating((prev) => ({ ...prev, [name]: "error" }));
    }
  }

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Settings</h2>

      <div className="space-y-8">
        <section>
          <h3 className="text-lg font-semibold mb-3">Mode</h3>
          <ModeSwitch mode={mode} onSwitch={setMode} isLoading={modeLoading} />
        </section>

        <section>
          <h3 className="text-lg font-semibold mb-3">Available Sources</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {sources.map((source) => (
              <div
                key={source.name}
                className="bg-white border border-gray-200 rounded-lg p-4"
                data-testid={`source-card-${source.name}`}
              >
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium">{source.display_name}</h4>
                  <div className="flex gap-2">
                    <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded">
                      {source.renderer}
                    </span>
                    {source.proxy_required && (
                      <span className="text-xs bg-amber-100 text-amber-700 px-2 py-0.5 rounded">
                        Proxy
                      </span>
                    )}
                  </div>
                </div>
                <button
                  onClick={() => handleValidate(source.name)}
                  disabled={validating[source.name] === "checking"}
                  className="text-xs text-blue-600 hover:underline"
                >
                  {validating[source.name] === "checking"
                    ? "Validating..."
                    : validating[source.name] === "ok"
                      ? "✓ Valid"
                      : validating[source.name] === "error"
                        ? "✗ Error"
                        : "Validate Config"}
                </button>
              </div>
            ))}
          </div>
        </section>

        <section>
          <h3 className="text-lg font-semibold mb-3">About</h3>
          <p className="text-sm text-gray-600">
            Lead Gen Scraper v0.1.0
          </p>
        </section>
      </div>
    </div>
  );
}
