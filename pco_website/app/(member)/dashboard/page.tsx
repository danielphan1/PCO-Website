"use client";

import { useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { toast } from "sonner";

export default function DashboardPage() {
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    if (searchParams.get("access_denied") === "1") {
      toast.error("Access denied. Admin privileges required.");
      router.replace("/dashboard");
    }
  }, [searchParams, router]);

  return (
    <div className="min-h-screen bg-black flex items-center justify-center">
      <p className="font-body text-white/40 tracking-widest uppercase text-sm">
        Dashboard — coming in Phase 4
      </p>
    </div>
  );
}
