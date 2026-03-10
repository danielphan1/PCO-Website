"use client";

import { AuthGuard } from "@/components/layout/AuthGuard";
import { SiteLayout } from "@/components/layout/SiteLayout";

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <SiteLayout>
      <AuthGuard requiredRole="admin">{children}</AuthGuard>
    </SiteLayout>
  );
}
