import { apiRequest } from "@/lib/api/client";

export type CurrentUser = {
  id: string;
  email: string;
  full_name: string;
  role: "admin" | "management" | "business_development" | "technical_analyst" | "read_only";
};

export async function getCurrentUser() {
  return apiRequest<CurrentUser>("/users/me");
}
