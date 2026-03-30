export interface Company {
  id: string;
  company_name: string;
  phone_display: string | null;
  email: string | null;
  email_validated: boolean;
  website: string | null;
  website_alive: boolean | null;
  address: string | null;
  city: string | null;
  state: string | null;
  zip: string | null;
  category: string | null;
  rating: number | null;
  review_count: number | null;
  source: string | null;
  source_url: string | null;
  social_links: Record<string, string> | null;
  needs_review: boolean;
  created_at: string | null;
}

export interface ScrapeTask {
  id: string;
  source: string;
  query: string;
  location: string;
  limit: number | null;
  mode: string;
  status: string;
  total_scraped: number;
  total_cleaned: number;
  total_deduped: number;
  total_exported: number;
  started_at: string | null;
  completed_at: string | null;
  error_message: string | null;
  created_at: string;
}

export interface TaskProgress {
  type?: "progress" | "task_completed" | "task_failed" | "results_update";
  pages_processed: number;
  pages_total: number | null;
  items_found: number;
  errors: number;
  stage: string;
  task_id?: string;
  total_scraped?: number;
  total_cleaned?: number;
  total_deduped?: number;
  error?: string;
  new_count?: number;
  total?: number;
}

export interface PipelineStage {
  stage: string;
  count_in: number;
  count_out: number;
  count_removed: number;
  count_modified: number;
  duration_ms: number | null;
  details: Record<string, unknown> | null;
}

export interface PipelineResponse {
  task_id: string;
  stages: PipelineStage[];
}

export interface ExportLog {
  id: string;
  task_id: string;
  format: string;
  file_path: string | null;
  rows_exported: number;
  exported_at: string;
}

export interface Source {
  name: string;
  display_name: string;
  renderer: string;
  proxy_required: boolean;
}

export interface CreateTaskPayload {
  source: string;
  query: string;
  location: string;
  limit: number;
  enrich: boolean;
}

export interface ResultsFilter {
  task_id?: string;
  source?: string;
  category?: string;
  needs_review?: boolean;
  search?: string;
  page?: number;
  page_size?: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export interface ExportRequest {
  task_id: string;
  format: "csv" | "excel" | "json" | "sheets";
  options?: Record<string, unknown>;
}

export type AppMode = "live" | "demo";
