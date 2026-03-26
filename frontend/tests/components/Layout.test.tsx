import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, it, expect } from "vitest";
import App from "../../src/App";

function renderApp(initialRoute = "/") {
  return render(
    <MemoryRouter initialEntries={[initialRoute]}>
      <App />
    </MemoryRouter>,
  );
}

describe("Layout", () => {
  it("renders sidebar with navigation links", () => {
    renderApp();
    const sidebar = screen.getByTestId("sidebar");
    expect(sidebar).toHaveTextContent("Dashboard");
    expect(sidebar).toHaveTextContent("New Task");
    expect(sidebar).toHaveTextContent("Results");
    expect(sidebar).toHaveTextContent("Settings");
  });

  it("highlights active route", () => {
    renderApp("/results");
    const sidebar = screen.getByTestId("sidebar");
    const resultsLink = sidebar.querySelector('a[href="/results"]');
    expect(resultsLink?.className).toContain("bg-gray-200");
    expect(resultsLink?.className).toContain("font-semibold");

    const dashboardLink = sidebar.querySelector('a[href="/"]');
    expect(dashboardLink?.className).not.toContain("bg-gray-200");
  });

  it("renders Dashboard page at /", () => {
    renderApp("/");
    expect(screen.getAllByText("Dashboard").length).toBeGreaterThanOrEqual(1);
    const heading = screen.getByRole("heading", { name: "Dashboard" });
    expect(heading).toBeInTheDocument();
  });

  it("renders New Task page at /tasks/new", () => {
    renderApp("/tasks/new");
    const heading = screen.getByRole("heading", { name: "New Task" });
    expect(heading).toBeInTheDocument();
  });

  it("renders Results page at /results", () => {
    renderApp("/results");
    const heading = screen.getByRole("heading", { name: "Results" });
    expect(heading).toBeInTheDocument();
  });

  it("renders Settings page at /settings", () => {
    renderApp("/settings");
    const heading = screen.getByRole("heading", { name: "Settings" });
    expect(heading).toBeInTheDocument();
  });
});
