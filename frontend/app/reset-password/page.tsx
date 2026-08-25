"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { getCurrentUser } from "@/lib/api/users";
import { acceptRedirectSession, setProfile, updatePassword } from "@/lib/auth";

export default function ResetPasswordPage() {
  const router = useRouter();
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  useEffect(() => { acceptRedirectSession(); }, []);
  async function submit(event: FormEvent) {
    event.preventDefault();
    if (password.length < 10) return setError("Use at least 10 characters.");
    if (password !== confirmPassword) return setError("Passwords do not match.");
    try {
      await updatePassword(password);
      const profile = await getCurrentUser();
      setProfile({
        id: profile.id,
        email: profile.email,
        fullName: profile.full_name,
        role: profile.role
      });
      router.replace("/dashboard");
    }
    catch (caughtError) { setError(caughtError instanceof Error ? caughtError.message : "Password update failed."); }
  }
  return <main className="flex min-h-screen items-center justify-center bg-background p-6">
    <form onSubmit={submit} className="w-full max-w-md space-y-4 rounded-md border bg-card p-6 shadow-sm">
      <div><h1 className="text-2xl font-semibold">Choose a password</h1><p className="mt-1 text-sm text-muted-foreground">Use this page after accepting an invitation or password-reset link.</p></div>
      <div className="space-y-2"><Label htmlFor="password">New password</Label><Input id="password" type="password" required value={password} onChange={(event) => setPassword(event.target.value)} /></div>
      <div className="space-y-2"><Label htmlFor="confirm-password">Confirm password</Label><Input id="confirm-password" type="password" required value={confirmPassword} onChange={(event) => setConfirmPassword(event.target.value)} /></div>
      {error ? <p role="alert" className="text-sm text-destructive">{error}</p> : null}
      <Button type="submit" className="w-full">Save password</Button>
    </form>
  </main>;
}
