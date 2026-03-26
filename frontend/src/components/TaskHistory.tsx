import { useNavigate } from "react-router-dom";
import type { ScrapeTask, CreateTaskPayload } from "../types";

interface TaskHistoryProps {
  tasks: ScrapeTask[];
  onRerun?: (payload: CreateTaskPayload) => Promise<ScrapeTask>;
  onDelete?: (id: string) => Promise<void>;
  limit?: number;
}

const statusStyles: Record<string, string> = {
  pending: "bg-gray-100 text-gray-700",
  running: "bg-blue-100 text-blue-700",
  completed: "bg-green-100 text-green-700",
  failed: "bg-red-100 text-red-700",
};

export default function TaskHistory({
  tasks,
  onRerun,
  onDelete,
  limit,
}: TaskHistoryProps) {
  const navigate = useNavigate();
  const displayed = limit ? tasks.slice(0, limit) : tasks;

  async function handleRerun(task: ScrapeTask) {
    if (!onRerun) return;
    const newTask = await onRerun({
      source: task.source,
      query: task.query,
      location: task.location,
      limit: task.limit ?? 100,
      enrich: false,
    });
    navigate(`/tasks/${newTask.id}`);
  }

  if (displayed.length === 0) {
    return <p className="text-gray-500 text-sm">No tasks yet.</p>;
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden" data-testid="task-history">
      <table className="w-full text-sm">
        <thead className="bg-gray-50">
          <tr>
            <th className="text-left px-4 py-2 font-medium text-gray-600">Source</th>
            <th className="text-left px-4 py-2 font-medium text-gray-600">Query</th>
            <th className="text-left px-4 py-2 font-medium text-gray-600">Location</th>
            <th className="text-left px-4 py-2 font-medium text-gray-600">Status</th>
            <th className="text-right px-4 py-2 font-medium text-gray-600">Items</th>
            <th className="text-right px-4 py-2 font-medium text-gray-600">Date</th>
            <th className="text-right px-4 py-2 font-medium text-gray-600">Actions</th>
          </tr>
        </thead>
        <tbody>
          {displayed.map((task) => (
            <tr key={task.id} className="border-t border-gray-100">
              <td className="px-4 py-2">{task.source}</td>
              <td className="px-4 py-2">{task.query}</td>
              <td className="px-4 py-2">{task.location}</td>
              <td className="px-4 py-2">
                <span
                  className={`inline-block px-2 py-0.5 rounded-full text-xs font-medium ${
                    statusStyles[task.status] ?? statusStyles.pending
                  }`}
                  data-testid={`status-${task.id}`}
                >
                  {task.status}
                </span>
              </td>
              <td className="px-4 py-2 text-right">{task.total_scraped}</td>
              <td className="px-4 py-2 text-right text-gray-500">
                {new Date(task.created_at).toLocaleDateString()}
              </td>
              <td className="px-4 py-2 text-right">
                <div className="flex gap-1 justify-end">
                  {task.status === "completed" && (
                    <button
                      onClick={() => navigate(`/results?task_id=${task.id}`)}
                      className="text-blue-600 hover:underline text-xs"
                    >
                      Results
                    </button>
                  )}
                  {onRerun && (
                    <button
                      onClick={() => handleRerun(task)}
                      className="text-green-600 hover:underline text-xs"
                      data-testid={`rerun-${task.id}`}
                    >
                      Re-run
                    </button>
                  )}
                  {onDelete && (
                    <button
                      onClick={() => onDelete(task.id)}
                      className="text-red-600 hover:underline text-xs"
                      data-testid={`delete-${task.id}`}
                    >
                      Delete
                    </button>
                  )}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
