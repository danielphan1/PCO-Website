import { cn } from "@/lib/utils";

interface DividerProps {
  className?: string;
  showDot?: boolean;
}

export function Divider({ className, showDot = true }: DividerProps) {
  return (
    <div className={cn("relative flex items-center", className)}>
      {/* Chrome gradient line: bright center fades to transparent at both edges */}
      <div
        className="flex-1 h-px"
        style={{
          background:
            "linear-gradient(to right, transparent, #c0c0c0 30%, #e8e8e8 50%, #c0c0c0 70%, transparent)",
        }}
      />
      {showDot && (
        // Green dot accent — centered on the line
        <span className="absolute left-1/2 -translate-x-1/2 w-1.5 h-1.5 rounded-full bg-green" />
      )}
    </div>
  );
}
