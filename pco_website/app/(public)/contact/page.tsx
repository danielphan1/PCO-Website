import type { Metadata } from "next";
import { SectionTitle } from "@/components/ui/SectionTitle";
import { ChromeCard } from "@/components/ui/ChromeCard";
import type { ContactInfo, LeadershipMember } from "@/types/api";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Contact | Psi Chi Omega",
  description: "Get in touch with Psi Chi Omega Alpha Chapter.",
};

async function getContacts(): Promise<ContactInfo | null> {
  try {
    const res = await fetch(`${process.env.BACKEND_URL}/v1/content/contacts`, {
      next: { revalidate: 3600 },
    });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

async function getLeadership(): Promise<LeadershipMember[] | null> {
  try {
    const res = await fetch(`${process.env.BACKEND_URL}/v1/content/leadership`, {
      next: { revalidate: 3600 },
    });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

export default async function ContactPage() {
  const [contacts, leadership] = await Promise.all([getContacts(), getLeadership()]);

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-24 space-y-16">

      {/* General contact info section */}
      <section>
        <SectionTitle>Contact</SectionTitle>
        {contacts ? (
          <div className="mt-8 space-y-3 text-white/70 font-body">
            {contacts.email && (
              <p>
                Email:{" "}
                <a
                  href={`mailto:${contacts.email}`}
                  className="text-green hover:text-green/80 transition-colors underline underline-offset-2"
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

      {/* Leadership contacts section */}
      <section>
        <SectionTitle>Leadership</SectionTitle>
        {leadership && leadership.length > 0 ? (
          <div className="mt-8 space-y-4">
            {leadership.map((member) => (
              <ChromeCard key={member.id}>
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 p-4">
                  <div>
                    <p className="text-white font-medium">{member.name}</p>
                    <p className="text-white/50 text-sm">{member.role}</p>
                  </div>
                  {(member as LeadershipMember & { email?: string }).email && (
                    <a
                      href={`mailto:${(member as LeadershipMember & { email?: string }).email}`}
                      className="text-green hover:text-green/80 transition-colors text-sm underline underline-offset-2"
                    >
                      {(member as LeadershipMember & { email?: string }).email}
                    </a>
                  )}
                </div>
              </ChromeCard>
            ))}
          </div>
        ) : (
          <p className="mt-8 text-white/40">Leadership contacts coming soon.</p>
        )}
      </section>

    </div>
  );
}
