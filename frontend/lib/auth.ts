const sessionKey = "xy-growth-intelligence:mock-session";

export type MockSession = {
  email: string;
  role: "business_development";
};

export function getMockSession(): MockSession | null {
  if (typeof window === "undefined") {
    return null;
  }

  const rawValue = window.localStorage.getItem(sessionKey);

  if (!rawValue) {
    return null;
  }

  try {
    return JSON.parse(rawValue) as MockSession;
  } catch {
    window.localStorage.removeItem(sessionKey);
    return null;
  }
}

export function signInMock(email: string): MockSession {
  const session: MockSession = {
    email,
    role: "business_development"
  };

  window.localStorage.setItem(sessionKey, JSON.stringify(session));
  return session;
}

export function signOutMock() {
  window.localStorage.removeItem(sessionKey);
}
