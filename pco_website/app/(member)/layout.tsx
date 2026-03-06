"use client";

import { AuthGuard } from "@/components/layout/AuthGuard";

export default function MemberLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <AuthGuard requiredRole="member">{children}</AuthGuard>;
}
