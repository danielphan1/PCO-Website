import { cn } from "@/lib/utils";

interface SectionTitleProps {
  children: React.ReactNode;
  className?: string;
  as?: "h1" | "h2" | "h3" | "h4";
}

export function SectionTitle({
  children,
  className,
  as: Tag = "h2",
}: SectionTitleProps) {
  return (
    <Tag
      className={cn(
        "font-heading text-white",
        // Cormorant Garamond looks best at larger sizes with lighter weight
        "text-3xl font-light tracking-wide",
        className
      )}
    >
      {children}
    </Tag>
  );
}
