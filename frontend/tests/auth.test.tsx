import { afterEach, describe, expect, it, vi } from "vitest";

import { getAccessToken, getSession, requestPasswordReset } from "@/lib/auth";

afterEach(() => {
  vi.unstubAllGlobals();
  vi.unstubAllEnvs();
  vi.restoreAllMocks();
});

describe("password recovery", () => {
  it("preserves the role profile after a real token refresh response", async () => {
    const stored = new Map<string, string>();
    vi.stubGlobal("localStorage", {
      getItem: (key: string) => stored.get(key) ?? null,
      setItem: (key: string, value: string) => stored.set(key, value),
      removeItem: (key: string) => stored.delete(key),
      clear: () => stored.clear(),
    });
    vi.stubEnv("NEXT_PUBLIC_SUPABASE_URL", "http://supabase.test");
    vi.stubEnv("NEXT_PUBLIC_SUPABASE_ANON_KEY", "anon-test");
    window.localStorage.setItem("xy-growth-intelligence:supabase-session", JSON.stringify({
      accessToken: "expired-synthetic-token", refreshToken: "synthetic-refresh", expiresAt: 0,
      email: "staff@example.test", profile: { id: "synthetic", role: "admin", fullName: "Synthetic" },
    }));
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: true, json: async () => ({
      access_token: "refreshed-synthetic-token", refresh_token: "rotated-synthetic-refresh",
      expires_in: 3600, user: { email: "staff@example.test" },
    }) }));
    expect(await getAccessToken()).toBe("refreshed-synthetic-token");
    expect(getSession()?.profile?.role).toBe("admin");
    window.localStorage.clear();
  });
  it("sends the reset destination as a Supabase redirect query parameter", async () => {
    vi.stubEnv("NEXT_PUBLIC_SUPABASE_URL", "http://supabase.test");
    vi.stubEnv("NEXT_PUBLIC_SUPABASE_ANON_KEY", "anon-test");
    const fetchMock = vi.fn().mockResolvedValue({ ok: true });
    vi.stubGlobal("fetch", fetchMock);

    await requestPasswordReset("staff@example.test");

    const [endpoint, options] = fetchMock.mock.calls[0];
    expect(endpoint).toBeInstanceOf(URL);
    expect(endpoint.searchParams.get("redirect_to")).toBe(
      `${window.location.origin}/reset-password`,
    );
    expect(JSON.parse(options.body)).toEqual({ email: "staff@example.test" });
  });
});
