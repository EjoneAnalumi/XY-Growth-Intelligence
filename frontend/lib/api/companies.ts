import { companies } from "@/lib/mock/companies";


export async function getCompanies() {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve(companies);
    }, 1000);
  });
}