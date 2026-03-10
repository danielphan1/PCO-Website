import type { Metadata } from "next";
import type { RushContent } from "@/types/api";
import { SectionTitle } from "@/components/ui/SectionTitle";
import { ChromeButton } from "@/components/ui/ChromeButton";

export const metadata: Metadata = {
  title: "Rush | Psi Chi Omega",
  description: "Learn about rush events and how to join Psi Chi Omega.",
};

async function getRush(): Promise<RushContent | null> {
  try {
    const apiBase = process.env.BACKEND_URL;
    if (!apiBase) return null;
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 5000);
    try {
      const res = await fetch(`${apiBase}/v1/rush`, {
        next: { revalidate: 3600 },
        signal: controller.signal,
      });
      if (!res.ok) return null;
      return res.json();
    } finally {
      clearTimeout(timeout);
    }
  } catch {
    return null;
  }
}

export default async function RushPage() {
  const data = await getRush();

  if (!data || data.status === "coming_soon") {
    return (
      <div className="min-h-[calc(100vh-4rem)] flex flex-col items-center justify-center px-4 text-center">
        <SectionTitle>Rush</SectionTitle>
        <p className="mt-6 text-white/60 font-body text-lg max-w-md">
          Rush season is coming soon. Sign up to stay in the loop.
        </p>
        <div className="mt-8">
          <ChromeButton href="/join" variant="primary">Sign Up</ChromeButton>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div className="text-center">
        <SectionTitle>{data.title ?? "Rush"}</SectionTitle>
        {data.intro && (
          <p className="mt-4 text-white/60 font-body text-lg max-w-xl mx-auto">
            {data.intro}
          </p>
        )}
        <div className="mt-8">
          <ChromeButton href="/join" variant="primary">Sign Up</ChromeButton>
        </div>
      </div>

      {data.events && data.events.length > 0 ? (
        <div className="relative mt-12 space-y-0">
          <div className="absolute left-[7rem] top-0 bottom-0 w-px bg-white/10" />
          {data.events.map((event) => (
            <div key={event.id} className="flex gap-6 pb-12 relative">
              <div className="absolute left-[6.85rem] top-1 w-[6px] h-[6px] rounded-full bg-green" />
              <div className="text-white/50 text-sm font-mono w-28 shrink-0 pt-0.5">
                {event.date}
              </div>
              <div>
                <p className="text-white font-medium">{event.name}</p>
                <p className="text-white/50 text-sm">
                  {event.time} &middot; {event.location}
                </p>
                {event.description && (
                  <p className="text-white/60 text-sm mt-2">{event.description}</p>
                )}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-white/40 mt-8">No events posted yet. Check back soon.</p>
      )}
    </div>
  );
}
