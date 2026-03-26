import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import ProgressBar from "../../src/components/ProgressBar";

describe("ProgressBar", () => {
  it("displays percentage from pages_processed/pages_total", () => {
    render(
      <ProgressBar
        pagesProcessed={5}
        pagesTotal={20}
        itemsFound={87}
        errors={0}
        status="running"
      />,
    );

    expect(screen.getByText("Page 5/20 — 87 items found")).toBeInTheDocument();
    expect(screen.getByText("25%")).toBeInTheDocument();

    const fill = screen.getByTestId("progress-fill");
    expect(fill.style.width).toBe("25%");
  });

  it("shows blue for running", () => {
    render(
      <ProgressBar pagesProcessed={3} pagesTotal={10} itemsFound={10} errors={0} status="running" />,
    );
    const fill = screen.getByTestId("progress-fill");
    expect(fill.className).toContain("bg-blue-500");
  });

  it("shows green for completed", () => {
    render(
      <ProgressBar pagesProcessed={10} pagesTotal={10} itemsFound={100} errors={0} status="completed" />,
    );
    const fill = screen.getByTestId("progress-fill");
    expect(fill.className).toContain("bg-green-500");
    expect(screen.getByText("100%")).toBeInTheDocument();
  });

  it("shows red for failed", () => {
    render(
      <ProgressBar pagesProcessed={5} pagesTotal={10} itemsFound={30} errors={2} status="failed" />,
    );
    const fill = screen.getByTestId("progress-fill");
    expect(fill.className).toContain("bg-red-500");
    expect(screen.getByText("2 errors")).toBeInTheDocument();
  });

  it("shows indeterminate when pagesTotal is null", () => {
    render(
      <ProgressBar pagesProcessed={5} pagesTotal={null} itemsFound={30} errors={0} status="running" />,
    );
    const fill = screen.getByTestId("progress-fill");
    expect(fill.className).toContain("animate-pulse");
    expect(screen.queryByText("%")).not.toBeInTheDocument();
  });
});
