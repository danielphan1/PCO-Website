"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { useAuth } from "@/contexts/AuthContext";
import { apiFetch } from "@/lib/api";
import { ChromeCard } from "@/components/ui/ChromeCard";
import { ChromeButton } from "@/components/ui/ChromeButton";
import { SectionTitle } from "@/components/ui/SectionTitle";
import { Divider } from "@/components/ui/Divider";
import type { AuthTokens, User } from "@/types/api";

export function LoginForm() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { user, login } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (user) router.replace("/dashboard");
  }, [user, router]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      const data = await apiFetch<AuthTokens & { user: User }>("/v1/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      login(
        { access_token: data.access_token, refresh_token: data.refresh_token },
        data.user
      );
      router.push("/dashboard");
    } catch {
      toast.error("Invalid email or password.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="w-full max-w-sm mx-auto">
      <ChromeCard>
        <form onSubmit={handleSubmit}>
          <div className="px-8 py-10 flex flex-col gap-5">
            <SectionTitle>PSI CHI OMEGA</SectionTitle>
            <Divider />
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Email"
              required
              className="w-full bg-white/5 border border-white/20 rounded px-4 py-2.5 text-white text-sm placeholder:text-white/40 focus:outline-none focus:border-white/50 transition-colors"
            />
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Password"
              required
              className="w-full bg-white/5 border border-white/20 rounded px-4 py-2.5 text-white text-sm placeholder:text-white/40 focus:outline-none focus:border-white/50 transition-colors"
            />
            <ChromeButton variant="primary" type="submit" disabled={isSubmitting}>
              {isSubmitting ? "Signing in\u2026" : "Sign In"}
            </ChromeButton>
            <p className="text-xs text-white/40 text-center mt-2">
              Accounts are created by admins. Contact your chapter officer to get access.
            </p>
          </div>
        </form>
      </ChromeCard>
    </div>
  );
}
