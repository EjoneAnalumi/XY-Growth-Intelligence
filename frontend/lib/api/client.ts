import { clearSession, getAccessToken } from "@/lib/auth";

const defaultApiBaseUrl = "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  details?: unknown;

  constructor(message: string, status: number, details?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.details = details;
  }
}

export function getApiBaseUrl() {
  return process.env.NEXT_PUBLIC_API_BASE_URL ?? defaultApiBaseUrl;
}

export async function apiRequest<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = await getAccessToken();

  if (!token) {
    throw new ApiError("You must sign in before using the API.", 401);
  }

  const response = await fetch(`${getApiBaseUrl()}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...init.headers,
    },
  });

  if (!response.ok) {
    if (response.status === 401) clearSession();
    const body = await response.json().catch(() => null);
    const message =
      typeof body?.detail === "string" ? body.detail : `API request failed with ${response.status}.`;

    throw new ApiError(message, response.status, body?.error?.details);
  }

  return response.json() as Promise<T>;
}
