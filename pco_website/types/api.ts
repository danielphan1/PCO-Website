// Shared TypeScript types for API responses and auth

export interface User {
  id: string;
  full_name: string;
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

// Phase 2 — Public site type contracts

export interface LeadershipMember {
  id: string;
  name: string;
  role: string;
  photo_url?: string; // optional — backend may not return this
}

export interface RushEvent {
  id: string;
  name: string;
  date: string;
  time: string;
  location: string;
  description?: string;
}

export interface RushContent {
  status: "published" | "coming_soon";
  title?: string;
  intro?: string;
  events?: RushEvent[];
}

export interface ContentSection {
  title: string;
  body: string;
}

export interface ContactInfo {
  email?: string;
  phone?: string;
  address?: string;
}

// Phase 4 — Member Dashboard type contracts

export interface Event {
  id: string;
  title: string;
  date: string;           // ISO date string — format with Date constructor
  signed_url: string;     // Supabase signed URL for PDF access
}

// LeadershipContact is separate from LeadershipMember (public type has no email field)
export interface LeadershipContact {
  id: string;
  name: string;
  role: string;
  email: string;          // Required for mailto links
}
