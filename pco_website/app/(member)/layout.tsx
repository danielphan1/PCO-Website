"use client";

import { AuthGuard } from "@/components/layout/AuthGuard";
import { SiteLayout } from "@/components/layout/SiteLayout";

export default function MemberLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <SiteLayout>
      <AuthGuard requiredRole="member">{children}</AuthGuard>
    </SiteLayout>
  );
}
