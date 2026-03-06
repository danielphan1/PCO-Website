"use client";

import { cn } from "@/lib/utils";

interface ChromeButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary";
  asChild?: boolean;
  href?: string;
}

export function ChromeButton({
  variant = "primary",
  children,
  className,
  href,
  ...props
}: ChromeButtonProps) {
  const base = cn(
    // Layout and typography
    "relative inline-flex items-center justify-center overflow-hidden",
    "px-6 py-2.5 rounded-sm",
    "text-sm font-medium tracking-widest uppercase",
    "transition-colors duration-200",
    // Sheen pseudo-element via nested span (see below)
    "group",
    // Variant styles
    variant === "primary" && [
      "bg-green text-white border border-green",
      "hover:bg-green/90",
    ],
    variant === "secondary" && [
      "bg-transparent text-white border border-chrome",
      "hover:border-chrome-light",
    ],
    className
  );

  const inner = (
    <>
      {/* Sheen: absolute span sweeps diagonally on group-hover */}
      <span
        className={cn(
          "absolute inset-0 -skew-x-[20deg] translate-x-[-100%]",
          "bg-gradient-to-r from-transparent via-white/30 to-transparent",
          "group-hover:animate-[sheen_0.6s_ease-in-out]",
          "pointer-events-none"
        )}
        aria-hidden="true"
      />
      <span className="relative z-10">{children}</span>
    </>
  );

  if (href) {
    return (
      <a href={href} className={base}>
        {inner}
      </a>
    );
  }

  return (
    <button className={base} {...props}>
      {inner}
    </button>
  );
}
