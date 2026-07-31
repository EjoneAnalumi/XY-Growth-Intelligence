import { apiRequest } from "@/lib/api/client";
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
