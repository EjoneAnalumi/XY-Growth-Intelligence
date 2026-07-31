import { companies } from "@/lib/mock/companies";
import type { Company } from "@/types/company";

export async function getCompanies(): Promise<Company[]> {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve(companies);
    }, 1000);
  });
}
