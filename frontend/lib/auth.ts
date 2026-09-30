const sessionKey = "xy-growth-intelligence:supabase-session";

export type UserRole = "admin" | "management" | "business_development" | "technical_analyst" | "read_only";
export type AuthProfile = { id: string; email: string; fullName: string; role: UserRole };
export type AuthSession = {
  accessToken: string;
  refreshToken: string;
  expiresAt: number;
  email: string;
  profile?: AuthProfile;
};
type TokenResponse = {
  access_token: string;
  refresh_token: string;
  expires_in: number;
  user: { email?: string };
};

function configuration() {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const anonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
  if (!url || !anonKey || anonKey.startsWith("replace-with")) {
    throw new Error("Supabase Auth is not configured for the frontend.");
  }
  return { url, anonKey };
}

export function getSession(): AuthSession | null {
  if (typeof window === "undefined") return null;
  const value = window.localStorage.getItem(sessionKey);
  if (!value) return null;
  try { return JSON.parse(value) as AuthSession; } catch { clearSession(); return null; }
}

function saveTokenResponse(response: TokenResponse, profile?: AuthProfile): AuthSession {
  const session: AuthSession = {
    accessToken: response.access_token,
    refreshToken: response.refresh_token,
    expiresAt: Date.now() + response.expires_in * 1000,
    email: response.user.email ?? "",
    profile,
  };
  window.localStorage.setItem(sessionKey, JSON.stringify(session));
  return session;
}

export async function signIn(email: string, password: string): Promise<AuthSession> {
  const { url, anonKey } = configuration();
  const response = await fetch(`${url}/auth/v1/token?grant_type=password`, {
    method: "POST",
    headers: { apikey: anonKey, "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!response.ok) throw new Error("Email or password is incorrect.");
  return saveTokenResponse(await response.json());
}

export async function getAccessToken(): Promise<string | null> {
  const session = getSession();
  if (!session) return null;
  if (session.expiresAt > Date.now() + 30_000) return session.accessToken;
  const { url, anonKey } = configuration();
  const response = await fetch(`${url}/auth/v1/token?grant_type=refresh_token`, {
    method: "POST",
    headers: { apikey: anonKey, "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: session.refreshToken }),
  });
  if (!response.ok) { clearSession(); return null; }
  return saveTokenResponse(await response.json(), session.profile).accessToken;
}

export function setProfile(profile: AuthProfile) {
  const session = getSession();
  if (session) window.localStorage.setItem(sessionKey, JSON.stringify({ ...session, profile }));
}

export async function signOut() {
  const session = getSession();
  if (session) {
    const { url, anonKey } = configuration();
    await fetch(`${url}/auth/v1/logout`, {
      method: "POST",
      headers: { apikey: anonKey, Authorization: `Bearer ${session.accessToken}` },
    }).catch(() => undefined);
  }
  clearSession();
}

export function clearSession() {
  if (typeof window !== "undefined") window.localStorage.removeItem(sessionKey);
}

export async function requestPasswordReset(email: string) {
  const { url, anonKey } = configuration();
  const redirectTo = `${window.location.origin}/reset-password`;
  const endpoint = new URL(`${url}/auth/v1/recover`);
  endpoint.searchParams.set("redirect_to", redirectTo);
  const response = await fetch(endpoint, {
    method: "POST",
    headers: { apikey: anonKey, "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
  });
  if (!response.ok) throw new Error("Password reset request failed.");
}

export function acceptRedirectSession(): AuthSession | null {
  const values = new URLSearchParams(window.location.hash.slice(1));
  const accessToken = values.get("access_token");
  const refreshToken = values.get("refresh_token");
  if (!accessToken || !refreshToken) return getSession();
  const session: AuthSession = {
    accessToken,
    refreshToken,
    expiresAt: Date.now() + Number(values.get("expires_in") ?? 3600) * 1000,
    email: "",
  };
  window.localStorage.setItem(sessionKey, JSON.stringify(session));
  window.history.replaceState({}, document.title, window.location.pathname);
  return session;
}

export async function updatePassword(password: string) {
  const token = await getAccessToken();
  if (!token) throw new Error("Invitation or reset link is invalid or expired.");
  const { url, anonKey } = configuration();
  const response = await fetch(`${url}/auth/v1/user`, {
    method: "PUT",
    headers: { apikey: anonKey, Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
    body: JSON.stringify({ password }),
  });
  if (!response.ok) throw new Error("Password could not be updated.");
}
