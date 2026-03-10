"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ChromeButton } from "@/components/ui/ChromeButton";
import { useAuth } from "@/contexts/AuthContext";

const NAV_LINKS = [
  { label: "RUSH", href: "/rush" },
  { label: "HISTORY", href: "/#history" },
  { label: "PHILANTHROPY", href: "/#philanthropy" },
  { label: "CONTACT", href: "/#contact" },
];

function HamburgerIcon({ open }: { open: boolean }) {
  return (
    <button
      aria-label={open ? "Close menu" : "Open menu"}
      aria-expanded={open}
      className="relative w-8 h-8 flex flex-col justify-center items-center gap-1.5 md:hidden"
    >
      <span
        className={`block w-6 h-px bg-white transition-all duration-300 ${
          open ? "rotate-45 translate-y-2" : ""
        }`}
      />
      <span
        className={`block w-6 h-px bg-white transition-all duration-300 ${
          open ? "opacity-0" : ""
        }`}
      />
      <span
        className={`block w-6 h-px bg-white transition-all duration-300 ${
          open ? "-rotate-45 -translate-y-2" : ""
        }`}
      />
    </button>
  );
}

export function SiteLayout({ children }: { children: React.ReactNode }) {
  const [menuOpen, setMenuOpen] = useState(false);
  const { user, logout } = useAuth();
  const router = useRouter();

  return (
    <div className="min-h-screen flex flex-col bg-black">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b border-white/10 bg-black/95 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <Link
              href="/"
              className="font-heading text-white text-lg tracking-[0.2em] uppercase font-light"
            >
              PSI CHI OMEGA
            </Link>

            {/* Desktop nav — hidden when logged in */}
            {!user && (
              <nav className="hidden md:flex items-center gap-8" aria-label="Main navigation">
                {NAV_LINKS.map((link) => (
                  <Link
                    key={link.href}
                    href={link.href}
                    className="text-xs tracking-[0.15em] uppercase text-white/70 hover:text-white transition-colors duration-200"
                  >
                    {link.label}
                  </Link>
                ))}
              </nav>
            )}

            {/* Desktop CTAs */}
            {user ? (
              <div className="hidden md:flex items-center gap-3">
                <Link
                  href="/dashboard"
                  className="text-xs tracking-[0.15em] uppercase text-white/70 hover:text-white transition-colors duration-200"
                >
                  Dashboard
                </Link>
                <ChromeButton
                  variant="secondary"
                  onClick={() => {
                    logout();
                    router.replace("/");
                  }}
                >
                  Logout
                </ChromeButton>
              </div>
            ) : (
              <div className="hidden md:flex items-center gap-3">
                <ChromeButton href="/join" variant="primary">Join</ChromeButton>
                <ChromeButton href="/login" variant="secondary">Login</ChromeButton>
              </div>
            )}

            {/* Authenticated mobile controls */}
            {user && (
              <div className="flex md:hidden items-center gap-2">
                <ChromeButton
                  variant="secondary"
                  onClick={() => {
                    logout();
                    router.replace("/");
                  }}
                >
                  Logout
                </ChromeButton>
              </div>
            )}

            {/* Hamburger — mobile only, hidden when logged in */}
            {!user && (
              <div
                className="md:hidden"
                onClick={() => setMenuOpen((prev) => !prev)}
              >
                <HamburgerIcon open={menuOpen} />
              </div>
            )}
          </div>
        </div>

        {/* Mobile dropdown — hidden when logged in */}
        {menuOpen && !user && (
          <div className="md:hidden border-t border-white/10 bg-black">
            <nav
              className="flex flex-col px-4 py-4 gap-4"
              aria-label="Mobile navigation"
            >
              {NAV_LINKS.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  onClick={() => setMenuOpen(false)}
                  className="text-sm tracking-[0.15em] uppercase text-white/70 hover:text-white transition-colors duration-200 py-1"
                >
                  {link.label}
                </Link>
              ))}
              <div className="flex flex-col gap-3 pt-2 border-t border-white/10">
                <ChromeButton href="/join" variant="primary" className="w-full justify-center">Join</ChromeButton>
                <ChromeButton href="/login" variant="secondary" className="w-full justify-center">Login</ChromeButton>
              </div>
            </nav>
          </div>
        )}
      </header>

      {/* Main content */}
      <main className="flex-1">{children}</main>

      {/* Footer */}
      <footer className="border-t border-white/10 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p className="font-heading text-white/40 text-sm tracking-widest uppercase">
            Psi Chi Omega &copy; {new Date().getFullYear()}
          </p>
        </div>
      </footer>
    </div>
  );
}
