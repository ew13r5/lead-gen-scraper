import { describe, it, expect, beforeAll, afterAll, afterEach } from "vitest";
import { http, HttpResponse } from "msw";
import { setupServer } from "msw/node";
import { getTasks, createTask, getSources } from "../../src/api/client";
import type { PaginatedResponse, ScrapeTask, Source } from "../../src/types";

const mockTasks: PaginatedResponse<ScrapeTask> = {
  items: [
    {
      id: "t1",
      source: "yellowpages",
      query: "plumbers",
      location: "New York, NY",
      limit: 100,
      mode: "demo",
      status: "completed",
      total_scraped: 100,
      total_cleaned: 95,
      total_deduped: 80,
      total_exported: 80,
      started_at: "2026-01-01T00:00:00Z",
      completed_at: "2026-01-01T00:05:00Z",
      error_message: null,
      created_at: "2026-01-01T00:00:00Z",
    },
  ],
  total: 1,
  page: 1,
  page_size: 20,
};

const mockSources: Source[] = [
  {
    name: "yellowpages",
    display_name: "Yellow Pages",
    renderer: "static",
    proxy_required: true,
  },
];

const server = setupServer(
  http.get("/api/v1/tasks/", () => HttpResponse.json(mockTasks)),
  http.post("/api/v1/tasks/", async ({ request }) => {
    const body = (await request.json()) as Record<string, unknown>;
    return HttpResponse.json({
      id: "t-new",
      source: body.source,
      query: body.query,
      location: body.location,
      limit: body.limit,
      mode: "live",
      status: "pending",
      total_scraped: 0,
      total_cleaned: 0,
      total_deduped: 0,
      total_exported: 0,
      started_at: null,
      completed_at: null,
      error_message: null,
      created_at: "2026-01-01T00:00:00Z",
    });
  }),
  http.get("/api/v1/sources/", () => HttpResponse.json(mockSources)),
);

beforeAll(() => server.listen({ onUnhandledRequest: "error" }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe("API client", () => {
  it("getTasks returns typed ScrapeTask[]", async () => {
    const result = await getTasks();
    expect(result.items).toHaveLength(1);
    expect(result.items[0].source).toBe("yellowpages");
    expect(result.total).toBe(1);
  });

  it("createTask sends correct POST body", async () => {
    const task = await createTask({
      source: "yelp",
      query: "dentists",
      location: "LA, CA",
      limit: 50,
      enrich: false,
    });
    expect(task.id).toBe("t-new");
    expect(task.source).toBe("yelp");
    expect(task.query).toBe("dentists");
    expect(task.status).toBe("pending");
  });

  it("handles network error gracefully", async () => {
    server.use(
      http.get("/api/v1/sources/", () => HttpResponse.error()),
    );
    await expect(getSources()).rejects.toThrow();
  });
});
