"use client";

import {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";
import type { User, AuthTokens } from "@/types/api";
import { setTokens, clearTokens, getAccessToken } from "@/lib/auth";
import { apiFetch } from "@/lib/api";

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  login: (tokens: AuthTokens, user: User) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = getAccessToken();
    if (!token) {
      setLoading(false);
      return;
    }
    apiFetch<User>("/v1/users/me")
      .then((data) => setUser(data))
      .catch(() => {
        // 401 with exhausted refresh, or network error — clear stale tokens
        clearTokens();
        document.cookie = "auth-hint=; path=/; max-age=0; samesite=lax";
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, []);

  const login = (tokens: AuthTokens, user: User) => {
    setTokens(tokens);
    // Set auth-hint cookie so proxy.ts can detect auth state server-side.
    // Session cookie (no max-age) — expires when browser session ends.
    // SameSite=Lax prevents CSRF for navigation requests.
    document.cookie = "auth-hint=1; path=/; samesite=lax";
    setUser(user);
  };

  const logout = () => {
    clearTokens();
    // Clear auth-hint cookie by setting max-age=0
    document.cookie = "auth-hint=; path=/; max-age=0; samesite=lax";
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
