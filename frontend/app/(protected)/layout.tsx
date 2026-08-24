"use client";

import { useRouter } from "next/navigation";
import { ReactNode, useEffect, useState } from "react";

import { AppShell } from "@/components/app-shell";
import { getAccessToken } from "@/lib/auth";

export default function ProtectedLayout({ children }: { children: ReactNode }) {
  const router = useRouter();
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    void getAccessToken().then((token) => {
      if (!token) router.replace("/login");
      else setIsChecking(false);
    });
  }, [router]);

  if (isChecking) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-background px-4">
        <div className="rounded-md border bg-card px-5 py-4 text-sm text-muted-foreground shadow-sm">
          Checking session...
        </div>
      </main>
    );
  }

  return <AppShell>{children}</AppShell>;
}
