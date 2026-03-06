// Next.js 16 proxy — replaces deprecated middleware.ts
// Source: https://nextjs.org/docs/app/api-reference/file-conventions/proxy
//
// Security model: auth-hint is an OPTIMISTIC hint only.
// Real authorization lives in FastAPI. This prevents flash of protected content.
//
// The exported function MUST be named `proxy` (not `middleware`).

import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function proxy(request: NextRequest) {
  const authHint = request.cookies.get("auth-hint")?.value;
  const { pathname } = request.nextUrl;

  const isProtected =
    pathname.startsWith("/dashboard") || pathname.startsWith("/admin");
  const isAuthPage = pathname === "/login";

  // Unauthenticated user visiting protected route → redirect to login
  if (isProtected && !authHint) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  // Already-authenticated user visiting login → redirect to dashboard
  if (isAuthPage && authHint) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return NextResponse.next();
}

export const config = {
  // Match all routes except Next.js internals and static assets
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
};
