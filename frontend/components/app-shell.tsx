"use client";

import {
  BarChart3,
  Building2,
  LayoutDashboard,
  LogOut,
  Menu,
  Radar,
  ShieldCheck,
  Target,
  UsersRound,
  X
} from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { ReactNode, useState } from "react";

import { Button } from "@/components/ui/button";
import { getMockSession, signOutMock } from "@/lib/auth";
import type { MockRole } from "@/lib/auth";
import { cn } from "@/lib/utils";

type NavigationItem = {
  href: string;
  label: string;
  icon: typeof LayoutDashboard;
  roles?: MockRole[];
};

const navigation: NavigationItem[] = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/companies", label: "Companies", icon: Building2 },
  { href: "/contacts", label: "Contacts", icon: UsersRound },
  { href: "/opportunities", label: "Opportunities", icon: Target },
  {
    href: "/security-scans",
    label: "Security Scans",
    icon: Radar,
    roles: ["technical_analyst"]
  },
  { href: "/reports", label: "Reports", icon: BarChart3 }
];

const roleLabels = {
  business_development: "Business Development",
  technical_analyst: "Technical Analyst",
  management: "Management"
};

export function AppShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [mobileOpen, setMobileOpen] = useState(false);
  const session = getMockSession();
  const visibleNavigation = navigation.filter(
    (item) => !item.roles || (session && item.roles.includes(session.role))
  );

  function handleSignOut() {
    signOutMock();
    router.replace("/login");
  }

  return (
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-40 border-b bg-card/95 backdrop-blur">
        <div className="flex h-16 items-center justify-between px-4 sm:px-6 lg:px-8">
          <Link href="/dashboard" className="flex items-center gap-3">
            <div className="flex size-10 items-center justify-center rounded-md bg-primary text-primary-foreground">
              <ShieldCheck className="size-5" aria-hidden="true" />
            </div>
            <div className="min-w-0">
              <p className="truncate text-sm font-medium text-muted-foreground">XY CYBER</p>
              <p className="truncate text-base font-semibold tracking-normal">Growth Intelligence</p>
            </div>
          </Link>

          <div className="hidden items-center gap-3 md:flex">
            <span className="rounded-md bg-muted px-3 py-2 text-sm text-muted-foreground">
              {session ? roleLabels[session.role] : "Signed in"}
            </span>
            <Button type="button" variant="outline" onClick={handleSignOut}>
              <LogOut className="mr-2 size-4" aria-hidden="true" />
              Sign out
            </Button>
          </div>

          <Button
            type="button"
            variant="outline"
            size="icon"
            className="md:hidden"
            aria-label="Toggle navigation"
            onClick={() => setMobileOpen((value) => !value)}
          >
            {mobileOpen ? <X className="size-5" /> : <Menu className="size-5" />}
          </Button>
        </div>
      </header>

      <div className="lg:grid lg:grid-cols-[260px_1fr]">
        <aside
          className={cn(
            "border-b bg-card px-4 py-4 lg:sticky lg:top-16 lg:block lg:h-[calc(100vh-4rem)] lg:border-b-0 lg:border-r lg:px-5",
            mobileOpen ? "block" : "hidden"
          )}
        >
          <nav className="space-y-1" aria-label="Main navigation">
            {visibleNavigation.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;

              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setMobileOpen(false)}
                  className={cn(
                    "flex min-h-11 items-center gap-3 rounded-md px-3 py-2 text-sm font-medium",
                    isActive
                      ? "bg-primary text-primary-foreground"
                      : "text-muted-foreground hover:bg-muted hover:text-foreground"
                  )}
                >
                  <Icon className="size-4" aria-hidden="true" />
                  {item.label}
                </Link>
              );
            })}
          </nav>

          <div className="mt-4 border-t pt-4 md:hidden">
            <Button type="button" variant="outline" className="w-full" onClick={handleSignOut}>
              <LogOut className="mr-2 size-4" aria-hidden="true" />
              Sign out
            </Button>
          </div>
        </aside>

        <main className="min-w-0 px-4 py-6 sm:px-6 lg:px-8">{children}</main>
      </div>
    </div>
  );
}
