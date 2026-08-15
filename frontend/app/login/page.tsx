"use client";

import { ShieldCheck } from "lucide-react";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { getCurrentUser } from "@/lib/api/users";
import { signInMock, signOutMock } from "@/lib/auth";
import type { MockRole } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("bd.demo@example.test");
  const [password, setPassword] = useState("demo-password");
  const [role, setRole] = useState<MockRole>("business_development");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);

    if (!email.trim() || !password.trim()) {
      setError("Email and password are required.");
      return;
    }

    try {
      setIsSubmitting(true);
      signInMock(email, role);
      await getCurrentUser();
      router.replace("/dashboard");
    } catch {
      signOutMock();
      setError("Backend login check failed. Make sure FastAPI is running on port 8000.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="grid min-h-screen bg-background lg:grid-cols-[1fr_1.05fr]">
      <section className="flex items-center px-6 py-10 sm:px-10 lg:px-16">
        <div className="w-full max-w-md">
          <div className="mb-8 flex items-center gap-3">
            <div className="flex size-11 items-center justify-center rounded-md bg-primary text-primary-foreground">
              <ShieldCheck className="size-6" aria-hidden="true" />
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">XY CYBER</p>
              <h1 className="text-2xl font-semibold tracking-normal">Growth Intelligence</h1>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5 rounded-md border bg-card p-6 shadow-sm">
            <div>
              <h2 className="text-xl font-semibold tracking-normal">Sign in</h2>
              <p className="mt-1 text-sm text-muted-foreground">
                Use a demo account until Supabase Auth is connected.
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                autoComplete="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                autoComplete="current-password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="role">Demo role</Label>
              <select
                id="role"
                className="h-10 w-full rounded-md border bg-background px-3 text-sm"
                value={role}
                onChange={(event) => setRole(event.target.value as MockRole)}
              >
                <option value="admin">Admin</option>
                <option value="business_development">Business Development</option>
                <option value="technical_analyst">Technical Analyst</option>
                <option value="management">Management</option>
              </select>
            </div>

            {error ? (
              <p className="rounded-md border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
                {error}
              </p>
            ) : null}

            <Button type="submit" className="w-full" disabled={isSubmitting}>
              {isSubmitting ? "Signing in..." : "Sign in"}
            </Button>
          </form>
        </div>
      </section>

      <section className="hidden bg-secondary px-10 py-12 text-secondary-foreground lg:flex lg:items-end">
        <div className="max-w-xl">
          <p className="text-sm font-medium uppercase tracking-wider text-accent">
            Week 1 vertical slice
          </p>
          <p className="mt-4 text-4xl font-semibold tracking-normal">
            Login, company creation, contacts, and refresh persistence come first.
          </p>
          <p className="mt-5 text-base leading-7 text-secondary-foreground/75">
            This shell is ready for protected internal workflows while Supabase schema and auth
            integration are being finished.
          </p>
        </div>
      </section>
    </main>
  );
}
