import { useRef, useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { useWebSocket } from "../hooks/useWebSocket";
import { useApi } from "../hooks/useApi";
import * as api from "../api/client";
import ProgressBar from "../components/ProgressBar";

export default function TaskProgress() {
  const { id } = useParams<{ id: string }>();
  const { data: task, refetch } = useApi(
    () => api.getTask(id!),
    [id],
  );

  const wsUrl = id
    ? `${location.protocol === "https:" ? "wss:" : "ws:"}//${location.host}/ws/tasks/${id}/progress`
    : null;

  const { isConnected, progress } = useWebSocket(wsUrl);
  const [logs, setLogs] = useState<string[]>([]);
  const logRef = useRef<HTMLDivElement>(null);
  const prevStageRef = useRef<string | null>(null);

  useEffect(() => {
    if (progress && progress.stage !== prevStageRef.current) {
      prevStageRef.current = progress.stage;
      const ts = new Date().toLocaleTimeString();
      setLogs((prev) => [...prev, `[${ts}] Stage: ${progress.stage}`]);
    }
  }, [progress]);

  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [logs]);

  useEffect(() => {
    if (task?.status === "completed" || task?.status === "failed") return;
    const interval = setInterval(refetch, 5000);
    return () => clearInterval(interval);
  }, [task?.status, refetch]);

  const status = task?.status ?? "pending";
  const isCompleted = status === "completed";
  const isFailed = status === "failed";

  return (
    <div>
      <div className="flex items-center gap-3 mb-6">
        <h2 className="text-2xl font-bold">Task Progress</h2>
        {isCompleted && (
          <span className="bg-green-100 text-green-700 px-3 py-1 rounded-full text-sm font-medium" data-testid="completed-badge">
            Completed
          </span>
        )}
        {isFailed && (
          <span className="bg-red-100 text-red-700 px-3 py-1 rounded-full text-sm font-medium" data-testid="failed-badge">
            Failed
          </span>
        )}
        <span
          className={`ml-auto w-2.5 h-2.5 rounded-full ${isConnected ? "bg-green-500" : "bg-gray-300"}`}
          title={isConnected ? "Connected" : "Disconnected"}
        />
      </div>

      {task && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6 text-sm">
          <div className="bg-white border border-gray-200 rounded-md p-3">
            <p className="text-gray-500">Source</p>
            <p className="font-medium">{task.source}</p>
          </div>
          <div className="bg-white border border-gray-200 rounded-md p-3">
            <p className="text-gray-500">Query</p>
            <p className="font-medium">{task.query}</p>
          </div>
          <div className="bg-white border border-gray-200 rounded-md p-3">
            <p className="text-gray-500">Location</p>
            <p className="font-medium">{task.location}</p>
          </div>
          <div className="bg-white border border-gray-200 rounded-md p-3">
            <p className="text-gray-500">Limit</p>
            <p className="font-medium">{task.limit ?? "—"}</p>
          </div>
        </div>
      )}

      <div className="mb-6">
        <ProgressBar
          pagesProcessed={progress?.pages_processed ?? 0}
          pagesTotal={progress?.pages_total ?? null}
          itemsFound={progress?.items_found ?? task?.total_scraped ?? 0}
          errors={progress?.errors ?? 0}
          status={status}
        />
      </div>

      {task && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6 text-sm">
          <div className="text-center">
            <p className="text-gray-500">Scraped</p>
            <p className="text-xl font-bold">{task.total_scraped}</p>
          </div>
          <div className="text-center">
            <p className="text-gray-500">Cleaned</p>
            <p className="text-xl font-bold">{task.total_cleaned}</p>
          </div>
          <div className="text-center">
            <p className="text-gray-500">Deduped</p>
            <p className="text-xl font-bold">{task.total_deduped}</p>
          </div>
          <div className="text-center">
            <p className="text-gray-500">Exported</p>
            <p className="text-xl font-bold">{task.total_exported}</p>
          </div>
        </div>
      )}

      {isFailed && task?.error_message && (
        <div className="bg-red-50 border border-red-200 text-red-800 rounded-md p-4 mb-6" data-testid="error-alert">
          <p className="font-medium">Error</p>
          <p className="text-sm mt-1">{task.error_message}</p>
        </div>
      )}

      <div className="mb-6">
        <h3 className="text-sm font-medium text-gray-700 mb-2">Log</h3>
        <div
          ref={logRef}
          className="bg-gray-900 text-green-400 font-mono text-xs p-4 rounded-md h-48 overflow-y-auto"
          data-testid="log-stream"
        >
          {logs.length === 0 ? (
            <p className="text-gray-500">Waiting for events...</p>
          ) : (
            logs.map((line, i) => <p key={i}>{line}</p>)
          )}
        </div>
      </div>

      {isCompleted && (
        <Link
          to="/results"
          className="inline-block bg-blue-600 text-white rounded-md px-4 py-2 text-sm font-medium hover:bg-blue-700"
        >
          View Results
        </Link>
      )}
    </div>
  );
}
