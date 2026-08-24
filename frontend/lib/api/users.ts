import { apiRequest } from "@/lib/api/client";

export type CurrentUser = {
  id: string;
  email: string;
  full_name: string;
  role: "admin" | "management" | "business_development" | "technical_analyst" | "read_only";
};

export type UserProfile = CurrentUser & {
  active: boolean;
  last_login_at: string | null;
  created_at: string;
  updated_at: string;
};
export type AuditLog = {
  id: string;
  user_id: string | null;
  user_name: string | null;
  entity_type: string;
  entity_id: string;
  action: string;
  changed_at: string;
};

export async function getCurrentUser() {
  return apiRequest<CurrentUser>("/users/me");
}

export async function getUsers(): Promise<UserProfile[]> {
  return (await apiRequest<{ items: UserProfile[] }>("/users")).items;
}

export async function inviteUser(values: {
  email: string;
  fullName: string;
  role: CurrentUser["role"];
}) {
  return apiRequest("/users/invitations", {
    method: "POST",
    body: JSON.stringify({
      email: values.email,
      full_name: values.fullName,
      role: values.role,
      redirect_to: `${window.location.origin}/accept-invite`,
    }),
  });
}

export async function updateUser(id: string, values: {
  email?: string;
  full_name?: string;
  role?: CurrentUser["role"];
  active?: boolean;
}) {
  return apiRequest<UserProfile>(`/users/${id}`, {
    method: "PATCH",
    body: JSON.stringify(values),
  });
}

export async function deleteUser(id: string) {
  return apiRequest<void>(`/users/${id}`, { method: "DELETE" });
}

export async function getAuditLogs(): Promise<AuditLog[]> {
  return (await apiRequest<{ items: AuditLog[] }>("/users/audit-logs")).items;
}
