"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { requestPasswordReset } from "@/lib/auth";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  async function submit(event: FormEvent) {
    event.preventDefault();
    try {
      await requestPasswordReset(email.trim());
      setMessage("If that invited account exists, Supabase has sent a reset link.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Reset request failed.");
    }
  }
  return <main className="flex min-h-screen items-center justify-center bg-background p-6">
    <form onSubmit={submit} className="w-full max-w-md space-y-4 rounded-md border bg-card p-6 shadow-sm">
      <div><h1 className="text-2xl font-semibold">Reset password</h1><p className="mt-1 text-sm text-muted-foreground">Enter the email address from your staff invitation.</p></div>
      <div className="space-y-2"><Label htmlFor="email">Email</Label><Input id="email" type="email" required value={email} onChange={(event) => setEmail(event.target.value)} /></div>
      {message ? <p role="status" className="text-sm text-muted-foreground">{message}</p> : null}
      <Button type="submit" className="w-full">Send reset link</Button>
      <Link href="/login" className="block text-center text-sm text-primary underline">Back to sign in</Link>
    </form>
  </main>;
}
