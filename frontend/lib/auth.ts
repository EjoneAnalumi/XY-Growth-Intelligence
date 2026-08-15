const sessionKey = "xy-growth-intelligence:mock-session";

export type MockRole = "admin" | "business_development" | "technical_analyst" | "management";
export type MockToken =
  | "dev-admin"
  | "dev-business-development"
  | "dev-technical-analyst"
  | "dev-management";

export type MockSession = {
  email: string;
  role: MockRole;
  token: MockToken;
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

export function signInMock(email: string, role: MockRole = "business_development"): MockSession {
  const session: MockSession = {
    email,
    role: "business_development",
    token: "dev-business-development"
  };

  if (role === "technical_analyst") {
    session.role = "technical_analyst";
    session.token = "dev-technical-analyst";
  }

  if (role === "admin") {
    session.role = "admin";
    session.token = "dev-admin";
  }

  if (role === "management") {
    session.role = "management";
    session.token = "dev-management";
  }

  window.localStorage.setItem(sessionKey, JSON.stringify(session));
  return session;
}

export function signOutMock() {
  window.localStorage.removeItem(sessionKey);
}
