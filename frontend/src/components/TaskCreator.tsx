import { useState, useEffect, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import * as api from "../api/client";
import type { Source, CreateTaskPayload } from "../types";

interface TaskCreatorProps {
  onCreated?: () => void;
}

export default function TaskCreator({ onCreated }: TaskCreatorProps) {
  const navigate = useNavigate();
  const [sources, setSources] = useState<Source[]>([]);
  const [source, setSource] = useState("");
  const [query, setQuery] = useState("");
  const [location, setLocation] = useState("");
  const [limit, setLimit] = useState(100);
  const [enrich, setEnrich] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    api.getSources().then(setSources).catch(() => {});
  }, []);

  function validate(): boolean {
    const errs: Record<string, string> = {};
    if (!source) errs.source = "Source is required";
    if (!query.trim()) errs.query = "Query is required";
    if (!location.trim()) errs.location = "Location is required";
    setErrors(errs);
    return Object.keys(errs).length === 0;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!validate()) return;

    setSubmitting(true);
    try {
      const payload: CreateTaskPayload = {
        source,
        query: query.trim(),
        location: location.trim(),
        limit,
        enrich,
      };
      const task = await api.createTask(payload);
      onCreated?.();
      navigate(`/tasks/${task.id}`);
    } catch {
      setErrors({ form: "Failed to create task" });
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4" data-testid="task-creator">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Source
        </label>
        <select
          value={source}
          onChange={(e) => setSource(e.target.value)}
          className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
          data-testid="source-select"
        >
          <option value="">Select source...</option>
          {sources.map((s) => (
            <option key={s.name} value={s.name}>
              {s.display_name}
            </option>
          ))}
        </select>
        {errors.source && (
          <p className="text-red-500 text-xs mt-1">{errors.source}</p>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Query
        </label>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="e.g. plumbers, dentists, lawyers"
          className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
          data-testid="query-input"
        />
        {errors.query && (
          <p className="text-red-500 text-xs mt-1">{errors.query}</p>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Location
        </label>
        <input
          type="text"
          value={location}
          onChange={(e) => setLocation(e.target.value)}
          placeholder="e.g. New York, NY"
          className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
          data-testid="location-input"
        />
        {errors.location && (
          <p className="text-red-500 text-xs mt-1">{errors.location}</p>
        )}
      </div>

      <div className="flex gap-4">
        <div className="flex-1">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Limit
          </label>
          <input
            type="number"
            value={limit}
            onChange={(e) => setLimit(Number(e.target.value))}
            min={1}
            max={10000}
            className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
          />
        </div>
        <div className="flex items-end pb-2">
          <label className="flex items-center gap-2 text-sm text-gray-700">
            <input
              type="checkbox"
              checked={enrich}
              onChange={(e) => setEnrich(e.target.checked)}
              className="rounded border-gray-300"
            />
            Enrich data
          </label>
        </div>
      </div>

      {errors.form && (
        <p className="text-red-500 text-sm">{errors.form}</p>
      )}

      <button
        type="submit"
        disabled={submitting}
        className="w-full bg-blue-600 text-white rounded-md px-4 py-2 text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
      >
        {submitting ? "Creating..." : "Start Scraping"}
      </button>
    </form>
  );
}
