import { useNavigate } from "react-router-dom";
import { useTasks } from "../hooks/useTasks";
import { useMode } from "../hooks/useMode";
import DemoBanner from "../components/DemoBanner";
import ModeSwitch from "../components/ModeSwitch";
import * as api from "../api/client";
import { useState } from "react";

export default function Dashboard() {
  const navigate = useNavigate();
  const { tasks, isLoading } = useTasks();
  const { mode, setMode, isLoading: modeLoading } = useMode();
  const [seeding, setSeeding] = useState(false);

  const activeTasks = tasks.filter(
    (t) => t.status === "running" || t.status === "pending",
  ).length;
  const totalScraped = tasks.reduce((sum, t) => sum + t.total_scraped, 0);

  async function handleSeedDemo() {
    setSeeding(true);
    try {
      await api.seedDemo(500);
    } finally {
      setSeeding(false);
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold">Dashboard</h2>
        <ModeSwitch mode={mode} onSwitch={setMode} isLoading={modeLoading} />
      </div>

      <DemoBanner mode={mode} />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="bg-white rounded-lg border border-gray-200 p-4" data-testid="card-active">
          <p className="text-sm text-gray-500">Active Tasks</p>
          <p className="text-2xl font-bold mt-1">{isLoading ? "—" : activeTasks}</p>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4" data-testid="card-scraped">
          <p className="text-sm text-gray-500">Companies Scraped</p>
          <p className="text-2xl font-bold mt-1">{isLoading ? "—" : totalScraped}</p>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4" data-testid="card-tasks">
          <p className="text-sm text-gray-500">Total Tasks</p>
          <p className="text-2xl font-bold mt-1">{isLoading ? "—" : tasks.length}</p>
        </div>
      </div>

      <div className="flex gap-3 mb-8">
        <button
          onClick={() => navigate("/tasks/new")}
          className="bg-blue-600 text-white rounded-md px-4 py-2 text-sm font-medium hover:bg-blue-700"
        >
          New Task
        </button>
        {mode === "demo" && (
          <button
            onClick={handleSeedDemo}
            disabled={seeding}
            className="bg-orange-500 text-white rounded-md px-4 py-2 text-sm font-medium hover:bg-orange-600 disabled:opacity-50"
          >
            {seeding ? "Seeding..." : "Seed Demo Data"}
          </button>
        )}
      </div>

      {tasks.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold mb-3">Recent Tasks</h3>
          <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="text-left px-4 py-2 font-medium text-gray-600">Source</th>
                  <th className="text-left px-4 py-2 font-medium text-gray-600">Query</th>
                  <th className="text-left px-4 py-2 font-medium text-gray-600">Status</th>
                  <th className="text-right px-4 py-2 font-medium text-gray-600">Scraped</th>
                </tr>
              </thead>
              <tbody>
                {tasks.slice(0, 5).map((task) => (
                  <tr
                    key={task.id}
                    onClick={() => navigate(`/tasks/${task.id}`)}
                    className="border-t border-gray-100 cursor-pointer hover:bg-gray-50"
                  >
                    <td className="px-4 py-2">{task.source}</td>
                    <td className="px-4 py-2">{task.query}</td>
                    <td className="px-4 py-2">
                      <span
                        className={`inline-block px-2 py-0.5 rounded-full text-xs font-medium ${
                          task.status === "completed"
                            ? "bg-green-100 text-green-700"
                            : task.status === "running"
                              ? "bg-blue-100 text-blue-700"
                              : task.status === "failed"
                                ? "bg-red-100 text-red-700"
                                : "bg-gray-100 text-gray-700"
                        }`}
                      >
                        {task.status}
                      </span>
                    </td>
                    <td className="px-4 py-2 text-right">{task.total_scraped}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
