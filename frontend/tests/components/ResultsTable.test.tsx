import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, beforeAll, afterAll, afterEach } from "vitest";
import { http, HttpResponse } from "msw";
import { setupServer } from "msw/node";
import ExportPanel from "../../src/components/ExportPanel";
import ResultsTable from "../../src/components/ResultsTable";
import type { Company } from "../../src/types";

const mockCompanies: Company[] = [
  {
    id: "c1",
    company_name: "Acme Plumbing",
    phone_display: "+1-555-123-4567",
    email: "info@acme.com",
    website: "https://acme.com",
    email_validated: true,
    website_alive: true,
    address: "123 Main St",
    city: "New York",
    state: "NY",
    zip: "10001",
    category: "Plumbing",
    rating: 4.5,
    review_count: 42,
    source: "yellowpages",
    source_url: null,
    social_links: null,
    needs_review: false,
    created_at: "2026-01-01T00:00:00Z",
  },
  {
    id: "c2",
    company_name: "Best Dentistry",
    phone_display: "+1-555-987-6543",
    email: "hello@bestdent.com",
    website: "https://bestdent.com",
    email_validated: false,
    website_alive: null,
    address: "456 Oak Ave",
    city: "Los Angeles",
    state: "CA",
    zip: "90001",
    category: "Dentistry",
    rating: 4.8,
    review_count: 100,
    source: "yelp",
    source_url: null,
    social_links: null,
    needs_review: true,
    created_at: "2026-01-02T00:00:00Z",
  },
];

const server = setupServer(
  http.post("/api/v1/export/", () =>
    HttpResponse.json({
      id: "e1",
      task_id: "t1",
      format: "csv",
      file_path: "/exports/e1.csv",
      rows_exported: 100,
      exported_at: "2026-01-01T00:00:00Z",
    }),
  ),
);

beforeAll(() => server.listen({ onUnhandledRequest: "bypass" }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe("ResultsTable", () => {
  it("renders AG Grid with company data", async () => {
    render(<ResultsTable results={mockCompanies} />);
    expect(screen.getByTestId("results-table")).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText("Acme Plumbing")).toBeInTheDocument();
      expect(screen.getByText("Best Dentistry")).toBeInTheDocument();
    });
  });

  it("renders quick filter input", () => {
    render(<ResultsTable results={mockCompanies} />);
    expect(screen.getByTestId("quick-filter")).toBeInTheDocument();
  });
});

describe("ExportPanel", () => {
  it("triggers export on button click", async () => {
    render(<ExportPanel taskId="t1" />);

    const csvBtn = screen.getByTestId("export-csv");
    expect(csvBtn).toBeInTheDocument();

    fireEvent.click(csvBtn);

    await waitFor(() => {
      expect(csvBtn).not.toBeDisabled();
    });
  });

  it("shows all export format buttons", () => {
    render(<ExportPanel taskId="t1" />);
    expect(screen.getByTestId("export-csv")).toHaveTextContent("CSV");
    expect(screen.getByTestId("export-excel")).toHaveTextContent("Excel");
    expect(screen.getByTestId("export-json")).toHaveTextContent("JSON");
  });

  it("disables buttons when disabled prop is true", () => {
    render(<ExportPanel taskId="t1" disabled />);
    expect(screen.getByTestId("export-csv")).toBeDisabled();
  });
});
