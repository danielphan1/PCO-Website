// Shared TypeScript types for API responses and auth

export interface User {
  id: string;
  name: string;
  email: string;
  role: "member" | "admin";
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
}

export interface ApiError extends Error {
  status: number;
}
