import { cn } from "@/lib/utils";

interface ChromeCardProps {
  children: React.ReactNode;
  className?: string;
}

export function ChromeCard({ children, className }: ChromeCardProps) {
  return (
    <div
      className={cn(
        // Outer wrapper — gradient background clips to form the metallic border
        "relative rounded-xl p-px",
        "bg-gradient-to-br from-chrome-light via-transparent to-transparent",
        // Hover glow — green box shadow appears only on hover, not at rest
        "transition-shadow duration-300",
        "hover:shadow-[0_0_24px_rgba(34,139,34,0.35)]",
        className
      )}
    >
      {/* Inner div provides the actual card background */}
      <div className="relative rounded-[calc(0.75rem-1px)] bg-card p-6">
        {children}
      </div>
    </div>
  );
}
