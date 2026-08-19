import { fireEvent, render, screen } from "@testing-library/react";
import React from "react";
import { describe, expect, it, vi } from "vitest";

import { EmptyState, ErrorState, LoadingState } from "@/components/ui/async-state";

describe("async state components", () => {
  it("announces loading progress to assistive technology", () => {
    render(<LoadingState title="Loading companies..." />);

    expect(screen.getByRole("status")).toHaveTextContent("Loading companies...");
  });

  it("shows an actionable empty state", () => {
    render(
      <EmptyState
        title="No companies yet"
        description="Add a company to start building the CRM."
        action={<button type="button">Add company</button>}
      />,
    );

    expect(screen.getByRole("heading", { name: "No companies yet" })).toBeVisible();
    expect(screen.getByRole("button", { name: "Add company" })).toBeEnabled();
  });

  it("exposes errors as alerts and runs the retry action", () => {
    const onRetry = vi.fn();

    render(
      <ErrorState
        title="Companies could not be loaded"
        description="The API is unavailable."
        onRetry={onRetry}
      />,
    );

    expect(screen.getByRole("alert")).toHaveTextContent("The API is unavailable.");
    fireEvent.click(screen.getByRole("button", { name: "Try again" }));
    expect(onRetry).toHaveBeenCalledOnce();
  });
});
