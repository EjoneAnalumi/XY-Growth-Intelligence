import { getMockSession } from "@/lib/auth";

const defaultApiBaseUrl = "http://localhost:8000";

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

export function getApiBaseUrl() {
  return process.env.NEXT_PUBLIC_API_BASE_URL ?? defaultApiBaseUrl;
}

export async function apiRequest<T>(path: string, init: RequestInit = {}): Promise<T> {
  const session = getMockSession();

  if (!session) {
    throw new ApiError("You must sign in before using the API.", 401);
  }

  const response = await fetch(`${getApiBaseUrl()}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${session.token}`,
      ...init.headers,
    },
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    const message =
      typeof body?.detail === "string" ? body.detail : `API request failed with ${response.status}.`;

    throw new ApiError(message, response.status);
  }

  return response.json() as Promise<T>;
}
