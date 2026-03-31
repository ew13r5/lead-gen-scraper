import { useNavigate } from "react-router-dom";
import { useTasks } from "../hooks/useTasks";
import { useMode } from "../hooks/useMode";
import DemoBanner from "../components/DemoBanner";
import ModeSwitch from "../components/ModeSwitch";

export default function Dashboard() {
  const navigate = useNavigate();
  const { tasks, isLoading } = useTasks();
  const { mode, setMode, isLoading: modeLoading } = useMode();

  const lastCompleted = tasks.find((t) => t.status === "completed");

  const activeTasks = tasks.filter(
    (t) => t.status === "running" || t.status === "pending",
  ).length;
  const completedTasks = tasks.filter((t) => t.status === "completed").length;
  const totalScraped = tasks.reduce((sum, t) => sum + t.total_scraped, 0);
  const totalDeduped = tasks.reduce((sum, t) => sum + t.total_deduped, 0);
  const totalCleaned = tasks.reduce((sum, t) => sum + t.total_cleaned, 0);
  const duplicatesRemoved = totalScraped - totalDeduped;
  const qualityRate = totalScraped > 0 ? Math.round((totalDeduped / totalScraped) * 100) : 0;

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold">Dashboard</h2>
        <ModeSwitch mode={mode} onSwitch={setMode} isLoading={modeLoading} />
      </div>

      <DemoBanner mode={mode} />

      {/* Stats Cards - Row 1 */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
        <div className="bg-white rounded-lg border border-gray-200 p-4" data-testid="card-tasks">
          <p className="text-xs text-gray-500 uppercase tracking-wide">Total Tasks</p>
          <p className="text-3xl font-bold mt-1">{isLoading ? "—" : tasks.length}</p>
          <div className="flex gap-2 mt-2 text-xs">
            <span className="text-green-600">{completedTasks} completed</span>
            {activeTasks > 0 && <span className="text-blue-600">{activeTasks} active</span>}
          </div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4" data-testid="card-scraped">
          <p className="text-xs text-gray-500 uppercase tracking-wide">Companies Scraped</p>
          <p className="text-3xl font-bold mt-1">{isLoading ? "—" : totalScraped.toLocaleString()}</p>
          <p className="text-xs text-gray-400 mt-2">Raw records before pipeline</p>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <p className="text-xs text-gray-500 uppercase tracking-wide">Unique Leads</p>
          <p className="text-3xl font-bold mt-1 text-green-600">{isLoading ? "—" : totalDeduped.toLocaleString()}</p>
          <p className="text-xs text-gray-400 mt-2">After deduplication</p>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <p className="text-xs text-gray-500 uppercase tracking-wide">Data Quality</p>
          <p className="text-3xl font-bold mt-1">{isLoading ? "—" : `${qualityRate}%`}</p>
          <p className="text-xs text-gray-400 mt-2">{duplicatesRemoved} duplicates removed</p>
        </div>
      </div>

      {/* Pipeline Summary - Row 2 */}
      <div className="bg-white rounded-lg border border-gray-200 p-5 mb-4">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">Pipeline Summary</h3>
          {lastCompleted && (
            <span className="text-xs text-gray-400">Last task: {lastCompleted.source}</span>
          )}
        </div>
        <div className="flex items-center justify-between">
          {[
            { label: "Scraped", value: totalScraped, color: "border-l-blue-500" },
            { label: "Cleaned", value: totalCleaned, color: "border-l-cyan-500" },
            { label: "Deduplicated", value: totalDeduped, color: "border-l-purple-500" },
          ].map((item, i) => (
            <div key={item.label} className="flex items-center gap-3">
              {i > 0 && (
                <div className="text-gray-300 text-lg">→</div>
              )}
              <div className={`border-l-4 ${item.color} pl-3`}>
                <p className="text-xs text-gray-500">{item.label}</p>
                <p className="text-xl font-bold">{isLoading ? "—" : item.value.toLocaleString()}</p>
              </div>
            </div>
          ))}
          <div className="border-l-4 border-l-green-500 pl-3 bg-green-50 rounded-r-md py-1 pr-3">
            <p className="text-xs text-green-600 font-medium">Yield Rate</p>
            <p className="text-xl font-bold text-green-700">{isLoading ? "—" : `${qualityRate}%`}</p>
          </div>
        </div>
      </div>

      {/* Sources + Actions Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="md:col-span-2 bg-white rounded-lg border border-gray-200 p-5">
          <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-3">Available Sources</h3>
          <div className="flex flex-wrap gap-2">
            {[
              { name: "YellowPages", type: "static", color: "bg-yellow-50 text-yellow-700 border-yellow-200" },
              { name: "Yelp", type: "static", color: "bg-red-50 text-red-700 border-red-200" },
              { name: "BBB", type: "static", color: "bg-blue-50 text-blue-700 border-blue-200" },
              { name: "Clutch", type: "static", color: "bg-indigo-50 text-indigo-700 border-indigo-200" },
              { name: "Crunchbase", type: "playwright", color: "bg-emerald-50 text-emerald-700 border-emerald-200" },
            ].map((s) => (
              <div key={s.name} className={`${s.color} border rounded-lg px-3 py-2 text-sm`}>
                <span className="font-medium">{s.name}</span>
                <span className="ml-1.5 text-xs opacity-60">{s.type}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-5 flex flex-col justify-center gap-3">
          <button
            onClick={() => navigate("/tasks/new")}
            className="w-full bg-blue-600 text-white rounded-md px-4 py-2.5 text-sm font-medium hover:bg-blue-700 transition-colors"
          >
            + New Scraping Task
          </button>
          <button
            onClick={() => navigate("/results")}
            className="w-full bg-white border border-gray-300 text-gray-700 rounded-md px-4 py-2.5 text-sm font-medium hover:bg-gray-50 transition-colors"
          >
            View All Results
          </button>
        </div>
      </div>

      {/* Recent Tasks */}
      {tasks.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-3">Recent Tasks</h3>
          <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="text-left px-4 py-2.5 font-medium text-gray-600">Source</th>
                  <th className="text-left px-4 py-2.5 font-medium text-gray-600">Query</th>
                  <th className="text-left px-4 py-2.5 font-medium text-gray-600">Location</th>
                  <th className="text-left px-4 py-2.5 font-medium text-gray-600">Status</th>
                  <th className="text-right px-4 py-2.5 font-medium text-gray-600">Scraped</th>
                  <th className="text-right px-4 py-2.5 font-medium text-gray-600">Cleaned</th>
                  <th className="text-right px-4 py-2.5 font-medium text-gray-600">Unique</th>
                  <th className="text-right px-4 py-2.5 font-medium text-gray-600">Yield</th>
                </tr>
              </thead>
              <tbody>
                {tasks.slice(0, 5).map((task) => {
                  const yieldRate = task.total_scraped > 0
                    ? Math.round((task.total_deduped / task.total_scraped) * 100)
                    : 0;
                  return (
                    <tr
                      key={task.id}
                      onClick={() => navigate(`/tasks/${task.id}`)}
                      className="border-t border-gray-100 cursor-pointer hover:bg-gray-50"
                    >
                      <td className="px-4 py-2.5 font-medium">{task.source}</td>
                      <td className="px-4 py-2.5 text-gray-600">{task.query}</td>
                      <td className="px-4 py-2.5 text-gray-600">{task.location}</td>
                      <td className="px-4 py-2.5">
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
                      <td className="px-4 py-2.5 text-right">{task.total_scraped}</td>
                      <td className="px-4 py-2.5 text-right">{task.total_cleaned}</td>
                      <td className="px-4 py-2.5 text-right font-medium text-green-600">{task.total_deduped}</td>
                      <td className="px-4 py-2.5 text-right">
                        <span className={`text-xs font-medium ${yieldRate >= 50 ? "text-green-600" : "text-amber-600"}`}>
                          {yieldRate}%
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
