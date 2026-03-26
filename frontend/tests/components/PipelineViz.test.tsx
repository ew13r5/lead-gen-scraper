import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import PipelineViz from "../../src/components/PipelineViz";
import type { PipelineStage } from "../../src/types";

const mockStages: PipelineStage[] = [
  { stage: "scraped", count_in: 0, count_out: 1200, count_removed: 0, count_modified: 0, duration_ms: 5000, details: null },
  { stage: "cleaned", count_in: 1200, count_out: 1150, count_removed: 50, count_modified: 100, duration_ms: 1000, details: null },
  { stage: "validated", count_in: 1150, count_out: 1100, count_removed: 50, count_modified: 200, duration_ms: 800, details: null },
  { stage: "deduped", count_in: 1100, count_out: 950, count_removed: 150, count_modified: 0, duration_ms: 2000, details: null },
  { stage: "exported", count_in: 950, count_out: 950, count_removed: 0, count_modified: 0, duration_ms: 500, details: null },
];

describe("PipelineViz", () => {
  it("renders all stages with counts", () => {
    render(<PipelineViz stages={mockStages} />);

    expect(screen.getByTestId("stage-scraped")).toHaveTextContent("1200");
    expect(screen.getByTestId("stage-cleaned")).toHaveTextContent("1150");
    expect(screen.getByTestId("stage-validated")).toHaveTextContent("1100");
    expect(screen.getByTestId("stage-deduped")).toHaveTextContent("950");
    expect(screen.getByTestId("stage-exported")).toHaveTextContent("950");
  });

  it("shows count differences between stages as arrows", () => {
    render(<PipelineViz stages={mockStages} />);

    expect(screen.getByTestId("arrow-cleaned")).toHaveTextContent("-50");
    expect(screen.getByTestId("arrow-validated")).toHaveTextContent("-50");
    expect(screen.getByTestId("arrow-deduped")).toHaveTextContent("-150");
    expect(screen.getByTestId("arrow-exported")).toHaveTextContent("0");
  });

  it("color codes loss: red for >=10%, yellow for <10%, green for none", () => {
    render(<PipelineViz stages={mockStages} />);

    // deduped lost 150/1100 = ~13.6% → red
    expect(screen.getByTestId("arrow-deduped").className).toContain("text-red-600");

    // cleaned lost 50/1200 = ~4.2% → yellow
    expect(screen.getByTestId("arrow-cleaned").className).toContain("text-yellow-600");

    // exported lost 0 → green
    expect(screen.getByTestId("arrow-exported").className).toContain("text-green-600");
  });

  it("shows empty state when no stages", () => {
    render(<PipelineViz stages={[]} />);
    expect(screen.getByText("No pipeline data available.")).toBeInTheDocument();
  });

  it("shows loading skeleton", () => {
    render(<PipelineViz stages={[]} isLoading />);
    const viz = screen.getByTestId("pipeline-viz");
    expect(viz.querySelectorAll(".animate-pulse").length).toBeGreaterThan(0);
  });
});
