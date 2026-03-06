import type { Metadata } from "next";
import { ChromeButton } from "@/components/ui/ChromeButton";
import { ChromeCard } from "@/components/ui/ChromeCard";
import { SectionTitle } from "@/components/ui/SectionTitle";
import { Divider } from "@/components/ui/Divider";
import type { ContentSection, LeadershipMember, ContactInfo } from "@/types/api";

export const metadata: Metadata = {
  title: "Psi Chi Omega — Alpha Chapter",
  description: "Psi Chi Omega Alpha Chapter — Asian-interest fraternity. Join us.",
  openGraph: {
    title: "Psi Chi Omega — Alpha Chapter",
    description: "Psi Chi Omega Alpha Chapter — Asian-interest fraternity. Join us.",
    type: "website",
  },
};

async function fetchContent<T>(path: string): Promise<T | null> {
  try {
    const apiBase = process.env.NEXT_PUBLIC_API_BASE;
    if (!apiBase) return null;
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 5000);
    try {
      const res = await fetch(`${apiBase}${path}`, {
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

function getInitials(name: string): string {
  return name
    .split(" ")
    .map((word) => word[0])
    .filter(Boolean)
    .slice(0, 2)
    .join("")
    .toUpperCase();
}

export default async function HomePage() {
  const [history, philanthropy, leadership, contacts] = await Promise.all([
    fetchContent<ContentSection>("/v1/content/history"),
    fetchContent<ContentSection>("/v1/content/philanthropy"),
    fetchContent<LeadershipMember[]>("/v1/content/leadership"),
    fetchContent<ContactInfo>("/v1/content/contacts"),
  ]);

  return (
    <main>
      {/* Hero Section */}
      <section
        className="relative flex flex-col items-center justify-center min-h-[calc(100vh-4rem)]"
        style={{
          background: "radial-gradient(ellipse at center, #1a1a1a 0%, #000000 70%)",
        }}
      >
        <h1 className="font-heading text-5xl sm:text-7xl lg:text-8xl font-light tracking-[0.2em] uppercase text-white">
          PSI CHI OMEGA
        </h1>
        <p className="font-heading text-lg sm:text-xl tracking-[0.4em] uppercase text-white/50 mt-4">
          Alpha Chapter
        </p>
        <p className="text-xs tracking-[0.3em] uppercase text-white/30 mt-6">
          Integrity&nbsp;&nbsp;&nbsp;Perseverance&nbsp;&nbsp;&nbsp;Eternal Brotherhood
        </p>
        <div className="mt-10 flex gap-4 flex-wrap justify-center">
          <ChromeButton href="/join" variant="primary">Join Now</ChromeButton>
          <ChromeButton href="/rush" variant="secondary">Rush Info</ChromeButton>
        </div>

        {/* Scroll chevron */}
        <div
          className="absolute bottom-8 left-1/2 -translate-x-1/2"
          style={{ animation: "bounce-gentle 2s ease-in-out infinite" }}
          aria-hidden="true"
        >
          <svg
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            className="text-white/30"
          >
            <path d="M6 9l6 6 6-6" />
          </svg>
        </div>
      </section>

      {/* History Section */}
      <Divider />
      <section id="history" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
        <SectionTitle>History</SectionTitle>
        {history ? (
          <p className="mt-8 text-white/70 font-body leading-relaxed max-w-3xl">
            {history.body}
          </p>
        ) : (
          <p className="mt-8 text-white/40">Coming soon.</p>
        )}
      </section>

      {/* Philanthropy Section */}
      <Divider />
      <section id="philanthropy" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
        <SectionTitle>Philanthropy</SectionTitle>
        {philanthropy ? (
          <p className="mt-8 text-white/70 font-body leading-relaxed max-w-3xl">
            {philanthropy.body}
          </p>
        ) : (
          <p className="mt-8 text-white/40">Coming soon.</p>
        )}
      </section>

      {/* Leadership Section */}
      <Divider />
      <section id="leadership" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
        <SectionTitle>Leadership</SectionTitle>
        {leadership && leadership.length > 0 ? (
          <div className="mt-10 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {leadership.map((member) => (
              <ChromeCard key={member.id}>
                <div className="flex flex-col items-center gap-3 text-center p-4">
                  {member.photo_url ? (
                    <img
                      src={member.photo_url}
                      alt={member.name}
                      className="w-16 h-16 rounded-full object-cover"
                    />
                  ) : (
                    <div className="w-16 h-16 rounded-full bg-card-elevated border border-white/10 flex items-center justify-center font-heading text-xl text-white/60">
                      {getInitials(member.name)}
                    </div>
                  )}
                  <p className="text-white font-medium">{member.name}</p>
                  <p className="text-white/50 text-sm mt-0.5">{member.role}</p>
                </div>
              </ChromeCard>
            ))}
          </div>
        ) : (
          <p className="mt-8 text-white/40">Leadership bios coming soon.</p>
        )}
      </section>

      {/* Contact Section */}
      <Divider />
      <section id="contact" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
        <SectionTitle>Contact</SectionTitle>
        {contacts ? (
          <div className="mt-8 space-y-3 text-white/70">
            {contacts.email && (
              <p>
                Email:{" "}
                <a
                  href={`mailto:${contacts.email}`}
                  className="text-green hover:text-green/80 transition-colors"
                >
                  {contacts.email}
                </a>
              </p>
            )}
            {contacts.phone && <p>Phone: {contacts.phone}</p>}
            {contacts.address && <p>Address: {contacts.address}</p>}
          </div>
        ) : (
          <p className="mt-8 text-white/40">Contact info coming soon.</p>
        )}
      </section>
    </main>
  );
}
