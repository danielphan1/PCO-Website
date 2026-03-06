"use client";

import { AuthGuard } from "@/components/layout/AuthGuard";

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <AuthGuard requiredRole="admin">{children}</AuthGuard>;
}
