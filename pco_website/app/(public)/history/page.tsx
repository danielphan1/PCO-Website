import type { Metadata } from "next";
import { SectionTitle } from "@/components/ui/SectionTitle";
import type { ContentSection } from "@/types/api";

export const metadata: Metadata = {
  title: "History | Psi Chi Omega",
  description: "The history of Psi Chi Omega Alpha Chapter.",
};

async function getHistory(): Promise<ContentSection | null> {
  try {
    const res = await fetch(`${process.env.BACKEND_URL}/v1/content/history`, {
      next: { revalidate: 3600 },
    });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

export default async function HistoryPage() {
  const content = await getHistory();
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
      <SectionTitle>{content?.title ?? "History"}</SectionTitle>
      {content ? (
        <div className="mt-8 text-white/70 font-body leading-relaxed space-y-4">
          <p>{content.body}</p>
        </div>
      ) : (
        <p className="mt-8 text-white/40">Coming soon.</p>
      )}
    </div>
  );
}
