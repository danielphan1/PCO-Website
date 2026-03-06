import type { Metadata } from "next";
import { SectionTitle } from "@/components/ui/SectionTitle";
import type { ContentSection } from "@/types/api";

export const metadata: Metadata = {
  title: "Philanthropy | Psi Chi Omega",
  description: "Philanthropic initiatives of Psi Chi Omega Alpha Chapter.",
};

async function getPhilanthropy(): Promise<ContentSection | null> {
  try {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE}/v1/content/philanthropy`, {
      next: { revalidate: 3600 },
    });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

export default async function PhilanthropyPage() {
  const content = await getPhilanthropy();
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
      <SectionTitle>{content?.title ?? "Philanthropy"}</SectionTitle>
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
