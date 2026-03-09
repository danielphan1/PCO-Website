"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { FullPageSpinner } from "@/components/ui/FullPageSpinner";

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
      router.replace("/dashboard?access_denied=1");
    }
  }, [user, loading, requiredRole, router]);

  // While loading, show spinner — prevents flash of protected content
  if (loading) return <FullPageSpinner />;

  // Not authenticated — render nothing while redirect fires
  if (!user) return null;

  // Admin route, non-admin user — render nothing while redirect fires
  if (requiredRole === "admin" && user.role !== "admin") return null;

  return <>{children}</>;
}
