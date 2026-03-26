import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, it, expect, vi, beforeAll, afterAll, afterEach } from "vitest";
import { http, HttpResponse } from "msw";
import { setupServer } from "msw/node";
import TaskHistory from "../../src/components/TaskHistory";
import App from "../../src/App";
import type { ScrapeTask } from "../../src/types";

const mockTasks: ScrapeTask[] = [
  {
    id: "t1",
    source: "yellowpages",
    query: "plumbers",
    location: "NY",
    limit: 100,
    mode: "demo",
    status: "completed",
    total_scraped: 50,
    total_cleaned: 45,
    total_deduped: 40,
    total_exported: 40,
    started_at: null,
    completed_at: null,
    error_message: null,
    created_at: "2026-01-01T00:00:00Z",
  },
  {
    id: "t2",
    source: "yelp",
    query: "dentists",
    location: "LA",
    limit: 200,
    mode: "demo",
    status: "failed",
    total_scraped: 10,
    total_cleaned: 0,
    total_deduped: 0,
    total_exported: 0,
    started_at: null,
    completed_at: null,
    error_message: "Timeout",
    created_at: "2026-01-02T00:00:00Z",
  },
  {
    id: "t3",
    source: "bbb",
    query: "lawyers",
    location: "Chicago",
    limit: 50,
    mode: "live",
    status: "running",
    total_scraped: 25,
    total_cleaned: 0,
    total_deduped: 0,
    total_exported: 0,
    started_at: null,
    completed_at: null,
    error_message: null,
    created_at: "2026-01-03T00:00:00Z",
  },
];

const server = setupServer(
  http.get("/api/v1/mode/", () => HttpResponse.json({ mode: "live" })),
  http.get("/api/v1/sources/", () =>
    HttpResponse.json([
      { name: "yellowpages", display_name: "Yellow Pages", renderer: "static", proxy_required: true },
      { name: "yelp", display_name: "Yelp", renderer: "static", proxy_required: true },
    ]),
  ),
  http.get("/api/v1/tasks/", () =>
    HttpResponse.json({ items: mockTasks, total: 3, page: 1, page_size: 20 }),
  ),
);

beforeAll(() => server.listen({ onUnhandledRequest: "bypass" }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe("TaskHistory", () => {
  it("lists tasks with status badges", () => {
    render(
      <MemoryRouter>
        <TaskHistory tasks={mockTasks} />
      </MemoryRouter>,
    );

    expect(screen.getByTestId("status-t1")).toHaveTextContent("completed");
    expect(screen.getByTestId("status-t1").className).toContain("bg-green-100");

    expect(screen.getByTestId("status-t2")).toHaveTextContent("failed");
    expect(screen.getByTestId("status-t2").className).toContain("bg-red-100");

    expect(screen.getByTestId("status-t3")).toHaveTextContent("running");
    expect(screen.getByTestId("status-t3").className).toContain("bg-blue-100");
  });

  it("re-run calls createTask with same params", async () => {
    const rerunFn = vi.fn().mockResolvedValue({ ...mockTasks[0], id: "t-new" });
    render(
      <MemoryRouter>
        <TaskHistory tasks={mockTasks} onRerun={rerunFn} />
      </MemoryRouter>,
    );

    fireEvent.click(screen.getByTestId("rerun-t1"));

    await waitFor(() => {
      expect(rerunFn).toHaveBeenCalledWith({
        source: "yellowpages",
        query: "plumbers",
        location: "NY",
        limit: 100,
        enrich: false,
      });
    });
  });
});

describe("Settings page", () => {
  it("shows ModeSwitch and sources list", async () => {
    render(
      <MemoryRouter initialEntries={["/settings"]}>
        <App />
      </MemoryRouter>,
    );

    await waitFor(() => {
      expect(screen.getByTestId("mode-switch")).toBeInTheDocument();
    });

    await waitFor(() => {
      expect(screen.getByTestId("source-card-yellowpages")).toBeInTheDocument();
      expect(screen.getByTestId("source-card-yelp")).toBeInTheDocument();
    });
  });
});
