import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeAll, beforeEach, describe, expect, it, vi } from "vitest";

import CompanyCsvActions from "@/components/companies/company-csv-actions";
import { ApiError } from "@/lib/api/client";
import { exportCompaniesCsv, importCompaniesCsv } from "@/lib/api/companies";

vi.mock("@/lib/api/companies", () => ({
  importCompaniesCsv: vi.fn(),
  exportCompaniesCsv: vi.fn(),
}));

const importMock = vi.mocked(importCompaniesCsv);
const exportMock = vi.mocked(exportCompaniesCsv);

describe("CompanyCsvActions", () => {
  beforeAll(() => {
    Object.defineProperty(URL, "createObjectURL", {
      configurable: true,
      value: vi.fn(),
      writable: true,
    });
    Object.defineProperty(URL, "revokeObjectURL", {
      configurable: true,
      value: vi.fn(),
      writable: true,
    });
  });

  beforeEach(() => {
    vi.resetAllMocks();
    vi.mocked(URL.createObjectURL).mockReturnValue("blob:companies");
  });

  afterEach(() => {
    cleanup();
  });

  function renderActions(onImportComplete = vi.fn().mockResolvedValue(undefined)) {
    render(<CompanyCsvActions onImportComplete={onImportComplete} />);
    return { onImportComplete };
  }

  async function selectCsv(name = "companies.csv") {
    const file = new File(["name\nDemo\n"], name, { type: "text/csv" });
    const input = screen.getByLabelText("CSV file");
    await userEvent.upload(input, file);
    return file;
  }

  it("accepts a CSV file and enables import", async () => {
    renderActions();
    expect(screen.getByRole("button", { name: "Import CSV" })).toBeDisabled();
    await selectCsv();
    expect(screen.getByText("Selected: companies.csv")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Import CSV" })).toBeEnabled();
  });

  it("rejects an unsafe file type", () => {
    renderActions();
    const input = screen.getByLabelText("CSV file");
    fireEvent.change(input, {
      target: { files: [new File(["not csv"], "notes.txt", { type: "text/plain" })] },
    });
    expect(screen.getByRole("status")).toHaveTextContent("Choose a UTF-8 .csv file.");
    expect(screen.getByRole("button", { name: "Import CSV" })).toBeDisabled();
  });

  it("shows the created count and refreshes the company list after import", async () => {
    const { onImportComplete } = renderActions();
    const file = await selectCsv();
    importMock.mockResolvedValue(30);
    await userEvent.click(screen.getByRole("button", { name: "Import CSV" }));
    await waitFor(() => expect(importMock).toHaveBeenCalledWith(file));
    expect(onImportComplete).toHaveBeenCalledTimes(1);
    expect(screen.getByRole("status")).toHaveTextContent("30 companies imported successfully.");
  });

  it("shows importing state and disables competing actions", async () => {
    let resolveImport: (count: number) => void = () => undefined;
    importMock.mockReturnValue(new Promise((resolve) => { resolveImport = resolve; }));
    renderActions();
    await selectCsv();
    await userEvent.click(screen.getByRole("button", { name: "Import CSV" }));
    expect(screen.getByRole("button", { name: "Importing..." })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Export CSV" })).toBeDisabled();
    resolveImport(1);
    await waitFor(() => expect(screen.getByText("1 company imported successfully.")).toBeInTheDocument());
  });

  it("handles duplicate and validation responses without exposing raw errors", async () => {
    renderActions();
    await selectCsv();
    importMock.mockRejectedValueOnce(new ApiError("raw backend detail", 409));
    await userEvent.click(screen.getByRole("button", { name: "Import CSV" }));
    await waitFor(() => expect(screen.getByRole("status")).toHaveTextContent("already exist"));
    expect(screen.queryByText("raw backend detail")).not.toBeInTheDocument();

    importMock.mockRejectedValueOnce(new ApiError("raw backend detail", 422));
    await userEvent.click(screen.getByRole("button", { name: "Import CSV" }));
    await waitFor(() => expect(screen.getByRole("status")).toHaveTextContent("could not be validated"));
  });

  it("downloads the exported CSV with the server filename", async () => {
    const click = vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => undefined);
    exportMock.mockResolvedValue({ blob: new Blob(["name\nDemo\n"], { type: "text/csv" }), filename: "companies.csv" });
    renderActions();
    await userEvent.click(screen.getByRole("button", { name: "Export CSV" }));
    await waitFor(() => expect(exportMock).toHaveBeenCalledTimes(1));
    expect(click).toHaveBeenCalledTimes(1);
    expect(URL.createObjectURL).toHaveBeenCalledTimes(1);
    expect(URL.revokeObjectURL).toHaveBeenCalledWith("blob:companies");
    expect(screen.getByRole("status")).toHaveTextContent("download started");
  });
});
