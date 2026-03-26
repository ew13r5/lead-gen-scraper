import TaskCreator from "../components/TaskCreator";

export default function NewTask() {
  return (
    <div className="max-w-lg">
      <h2 className="text-2xl font-bold mb-6">New Task</h2>
      <TaskCreator />
    </div>
  );
}
