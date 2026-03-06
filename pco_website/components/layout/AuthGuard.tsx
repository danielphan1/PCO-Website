"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";

interface AuthGuardProps {
  children: React.ReactNode;
  requiredRole: "member" | "admin";
}

export function AuthGuard({ children, requiredRole }: AuthGuardProps) {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (loading) return;

    if (!user) {
      router.replace("/login");
      return;
    }

    // Non-admin user attempting to access admin routes → redirect to dashboard
    if (requiredRole === "admin" && user.role !== "admin") {
      router.replace("/dashboard");
    }
  }, [user, loading, requiredRole, router]);

  // While loading, render nothing — prevents flash of protected content
  if (loading) return null;

  // Not authenticated — render nothing while redirect fires
  if (!user) return null;

  // Admin route, non-admin user — render nothing while redirect fires
  if (requiredRole === "admin" && user.role !== "admin") return null;

  return <>{children}</>;
}
