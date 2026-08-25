import { afterEach, describe, expect, it, vi } from "vitest";

import { requestPasswordReset } from "@/lib/auth";

afterEach(() => {
  vi.unstubAllEnvs();
  vi.restoreAllMocks();
});

describe("password recovery", () => {
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
