import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL ?? "http://localhost:8000";

async function forward(
  req: NextRequest,
  params: Promise<{ path: string[] }>
): Promise<NextResponse> {
  const { path } = await params;
  const joined = path.join("/");
  const search = req.nextUrl.search;
  const url = `${BACKEND_URL}/${joined}${search}`;

  const headers = new Headers(req.headers);
  headers.delete("host");

  const isBodyless = req.method === "GET" || req.method === "HEAD";

  const upstream = await fetch(url, {
    method: req.method,
    headers,
    body: isBodyless ? undefined : req.body,
    // Required for streaming request bodies in Node.js fetch
    ...(isBodyless ? {} : { duplex: "half" as const }),
  } as RequestInit);

  return new NextResponse(upstream.body, {
    status: upstream.status,
    headers: upstream.headers,
  });
}

type RouteContext = { params: Promise<{ path: string[] }> };

export const GET    = (req: NextRequest, ctx: RouteContext) => forward(req, ctx.params);
export const POST   = (req: NextRequest, ctx: RouteContext) => forward(req, ctx.params);
export const PUT    = (req: NextRequest, ctx: RouteContext) => forward(req, ctx.params);
export const PATCH  = (req: NextRequest, ctx: RouteContext) => forward(req, ctx.params);
export const DELETE = (req: NextRequest, ctx: RouteContext) => forward(req, ctx.params);
