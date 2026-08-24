import { ApiError, apiRequest, getApiBaseUrl } from "@/lib/api/client";
import { getAccessToken } from "@/lib/auth";
import type { Company, CompanyFormValues } from "@/types/company";

type CompanyApiResponse = {
  id: string;
  name: string;
  domain: string | null;
  industry: string | null;
  headquarters_country: string | null;
  status: string;
};

type CompanyListApiResponse = {
  items: CompanyApiResponse[];
  total: number;
};

function mapCompany(company: CompanyApiResponse): Company {
  return {
    id: company.id,
    name: company.name,
    domain: company.domain ?? "",
    industry: company.industry ?? "",
    country: company.headquarters_country ?? "",
    status: company.status,
  };
}

export async function getCompanies(): Promise<Company[]> {
  const response = await apiRequest<CompanyListApiResponse>("/companies");
  return response.items.map(mapCompany);
}

export async function createCompany(payload: CompanyFormValues): Promise<Company> {
  const response = await apiRequest<CompanyApiResponse>("/companies", {
    method: "POST",
    body: JSON.stringify({
      name: payload.name,
      domain: payload.domain,
      industry: payload.industry,
      headquarters_country: payload.country,
      status: "prospect",
    }),
  });

  return mapCompany(response);
}

export async function updateCompany(id: string, payload: CompanyFormValues): Promise<Company> {
  const response = await apiRequest<CompanyApiResponse>(`/companies/${id}`, {
    method: "PATCH",
    body: JSON.stringify({
      name: payload.name,
      domain: payload.domain,
      industry: payload.industry,
      headquarters_country: payload.country,
    }),
  });
  return mapCompany(response);
}

export async function archiveCompany(id: string): Promise<void> {
  await apiRequest(`/companies/${id}`, { method: "DELETE" });
}

export type CompanyCsvExport = {
  blob: Blob;
  filename: string;
};

async function requestCompanyCsv(path: string, init: RequestInit): Promise<Response> {
  const token = await getAccessToken();

  if (!token) {
    throw new ApiError("You must sign in before using the API.", 401);
  }

  const response = await fetch(`${getApiBaseUrl()}${path}`, {
    ...init,
    headers: {
      Authorization: `Bearer ${token}`,
      ...init.headers,
    },
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    const message = typeof body?.detail === "string" ? body.detail : "CSV request failed.";
    throw new ApiError(message, response.status, body?.error?.details);
  }

  return response;
}

export async function importCompaniesCsv(file: File): Promise<number> {
  const response = await requestCompanyCsv("/companies/import", {
    method: "POST",
    headers: { "Content-Type": "text/csv; charset=utf-8" },
    body: await file.arrayBuffer(),
  });
  const payload = (await response.json()) as { created: number };
  return payload.created;
}

export async function exportCompaniesCsv(): Promise<CompanyCsvExport> {
  const response = await requestCompanyCsv("/companies/export", { method: "GET" });
  const disposition = response.headers.get("content-disposition") ?? "";
  const filename = /filename="?([^";]+)"?/i.exec(disposition)?.[1] ?? "companies.csv";

  return { blob: await response.blob(), filename };
}
