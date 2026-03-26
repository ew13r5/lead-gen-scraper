import axios from "axios";
import type {
  ScrapeTask,
  Company,
  CreateTaskPayload,
  ResultsFilter,
  PaginatedResponse,
  ExportRequest,
  ExportLog,
  Source,
  PipelineResponse,
  AppMode,
} from "../types";

const api = axios.create({
  baseURL: "/api/v1",
});

export async function getTasks(
  page = 1,
  pageSize = 20,
): Promise<PaginatedResponse<ScrapeTask>> {
  const { data } = await api.get("/tasks/", {
    params: { page, page_size: pageSize },
  });
  return data;
}

export async function createTask(
  payload: CreateTaskPayload,
): Promise<ScrapeTask> {
  const { data } = await api.post("/tasks/", payload);
  return data;
}

export async function getTask(id: string): Promise<ScrapeTask> {
  const { data } = await api.get(`/tasks/${id}`);
  return data;
}

export async function deleteTask(id: string): Promise<void> {
  await api.delete(`/tasks/${id}`);
}

export async function getResults(
  filters: ResultsFilter = {},
): Promise<PaginatedResponse<Company>> {
  const { data } = await api.get("/results/", { params: filters });
  return data;
}

export async function getResult(id: string): Promise<Company> {
  const { data } = await api.get(`/results/${id}`);
  return data;
}

export async function updateResult(
  id: string,
  fields: Partial<Company>,
): Promise<Company> {
  const { data } = await api.patch(`/results/${id}`, fields);
  return data;
}

export async function triggerExport(
  request: ExportRequest,
): Promise<ExportLog> {
  const { data } = await api.post("/export/", request);
  return data;
}

export function downloadExportUrl(id: string): string {
  return `/api/v1/export/${id}/download`;
}

export async function getSources(): Promise<Source[]> {
  const { data } = await api.get("/sources/");
  return data;
}

export async function getPipelineStats(
  taskId: string,
): Promise<PipelineResponse> {
  const { data } = await api.get(`/pipeline/${taskId}`);
  return data;
}

export async function getMode(): Promise<AppMode> {
  const { data } = await api.get("/mode/");
  return data.mode;
}

export async function setMode(mode: AppMode): Promise<AppMode> {
  const { data } = await api.put("/mode/", { mode });
  return data.mode;
}

export async function seedDemo(count = 500): Promise<{ seeded: number }> {
  const { data } = await api.post("/demo/seed", { count });
  return data;
}

export async function resetDemo(): Promise<void> {
  await api.post("/demo/reset");
}
