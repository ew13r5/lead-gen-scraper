import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, it, expect, beforeAll, afterAll, afterEach } from "vitest";
import { http, HttpResponse } from "msw";
import { setupServer } from "msw/node";
import App from "../../src/App";
import DemoBanner from "../../src/components/DemoBanner";
import ModeSwitch from "../../src/components/ModeSwitch";

const mockTaskList = {
  items: [
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
      status: "running",
      total_scraped: 30,
      total_cleaned: 0,
      total_deduped: 0,
      total_exported: 0,
      started_at: null,
      completed_at: null,
      error_message: null,
      created_at: "2026-01-02T00:00:00Z",
    },
  ],
  total: 2,
  page: 1,
  page_size: 20,
};

const server = setupServer(
  http.get("/api/v1/tasks/", () => HttpResponse.json(mockTaskList)),
  http.get("/api/v1/mode/", () => HttpResponse.json({ mode: "demo" })),
  http.get("/api/v1/sources/", () =>
    HttpResponse.json([
      { name: "yellowpages", display_name: "Yellow Pages", renderer: "static", proxy_required: true },
    ]),
  ),
);

beforeAll(() => server.listen({ onUnhandledRequest: "bypass" }));
afterEach(() => {
  server.resetHandlers();
  sessionStorage.clear();
});
afterAll(() => server.close());

describe("Dashboard", () => {
  it("shows task count and recent tasks", async () => {
    render(
      <MemoryRouter initialEntries={["/"]}>
        <App />
      </MemoryRouter>,
    );

    await waitFor(() => {
      expect(screen.getByTestId("card-tasks")).toHaveTextContent("2");
    });

    expect(screen.getByTestId("card-scraped")).toHaveTextContent("80");
    expect(screen.getByText("plumbers")).toBeInTheDocument();
  });
});

describe("DemoBanner", () => {
  it("shows in demo mode", () => {
    render(<DemoBanner mode="demo" />);
    expect(screen.getByTestId("demo-banner")).toBeInTheDocument();
  });

  it("hides in live mode", () => {
    render(<DemoBanner mode="live" />);
    expect(screen.queryByTestId("demo-banner")).not.toBeInTheDocument();
  });
});

describe("ModeSwitch", () => {
  it("toggles between Live and Demo", () => {
    let current = "demo" as string;
    const { rerender } = render(
      <ModeSwitch mode="demo" onSwitch={(m) => (current = m)} />,
    );

    fireEvent.click(screen.getByText("Live"));
    expect(current).toBe("live");

    rerender(
      <ModeSwitch mode="live" onSwitch={(m) => (current = m)} />,
    );

    fireEvent.click(screen.getByText("Demo"));
    expect(current).toBe("demo");
  });
});

describe("TaskCreator", () => {
  it("renders source dropdown from API", async () => {
    render(
      <MemoryRouter initialEntries={["/tasks/new"]}>
        <App />
      </MemoryRouter>,
    );

    await waitFor(() => {
      expect(screen.getByText("Yellow Pages")).toBeInTheDocument();
    });
  });

  it("validates required fields", async () => {
    render(
      <MemoryRouter initialEntries={["/tasks/new"]}>
        <App />
      </MemoryRouter>,
    );

    await waitFor(() => {
      expect(screen.getByText("Start Scraping")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText("Start Scraping"));

    await waitFor(() => {
      expect(screen.getByText("Source is required")).toBeInTheDocument();
      expect(screen.getByText("Query is required")).toBeInTheDocument();
      expect(screen.getByText("Location is required")).toBeInTheDocument();
    });
  });
});
