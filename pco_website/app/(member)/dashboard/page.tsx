"use client";

import { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { apiFetch } from "@/lib/api";
import { toast } from "sonner";
import { SectionTitle } from "@/components/ui/SectionTitle";
import { Divider } from "@/components/ui/Divider";
import { ChromeButton } from "@/components/ui/ChromeButton";
import type { Event, LeadershipContact } from "@/types/api";

function SkeletonRow() {
  return (
    <div className="flex items-center justify-between py-4 border-b border-chrome/10">
      <div className="flex flex-col gap-2">
        <div className="h-4 w-48 bg-white/10 rounded animate-pulse" />
        <div className="h-3 w-24 bg-white/5 rounded animate-pulse" />
      </div>
      <div className="h-8 w-16 bg-white/10 rounded animate-pulse" />
    </div>
  );
}

export default function DashboardPage() {
  const { user } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();

  const [events, setEvents] = useState<Event[]>([]);
  const [eventsLoading, setEventsLoading] = useState(true);
  const [eventsError, setEventsError] = useState(false);

  const [leaders, setLeaders] = useState<LeadershipContact[]>([]);
  const [leadersLoading, setLeadersLoading] = useState(true);
  const [leadersError, setLeadersError] = useState(false);

  // Preserve access_denied logic from Phase 3 stub
  useEffect(() => {
    if (searchParams.get("access_denied") === "1") {
      toast.error("Access denied. Admin privileges required.");
      router.replace("/dashboard");
    }
  }, [searchParams, router]);

  // Fetch events
  useEffect(() => {
    apiFetch<Event[]>("/v1/events/")
      .then(setEvents)
      .catch(() => {
        setEventsError(true);
        toast.error("Failed to load events. Try refreshing.");
      })
      .finally(() => setEventsLoading(false));
  }, []);

  // Fetch leadership contacts
  useEffect(() => {
    apiFetch<LeadershipContact[]>("/v1/content/leadership")
      .then(setLeaders)
      .catch(() => {
        setLeadersError(true);
        toast.error("Failed to load leadership contacts. Try refreshing.");
      })
      .finally(() => setLeadersLoading(false));
  }, []);

  return (
    <main className="max-w-2xl mx-auto px-4 py-12">
      {/* Profile snippet */}
      <div className="pb-8">
        <SectionTitle as="h1">{user?.full_name?.toUpperCase()}</SectionTitle>
        <p className="font-body text-white/40 text-xs tracking-[0.2em] uppercase mt-2">
          {user?.role}
        </p>
      </div>

      {/* Events section */}
      <Divider className="mb-6" />
      <SectionTitle as="h2" className="text-xl mb-4">Events</SectionTitle>

      {eventsLoading ? (
        <>
          <SkeletonRow />
          <SkeletonRow />
          <SkeletonRow />
        </>
      ) : eventsError ? (
        <p className="font-body text-white/40 text-sm py-4">
          Could not load events. Please refresh the page.
        </p>
      ) : events.length === 0 ? (
        <p className="font-body text-white/40 text-sm py-4">
          No upcoming events posted yet.
        </p>
      ) : (
        events.map((event) => (
          <div
            key={event.id}
            className="flex items-center justify-between py-4 border-b border-chrome/10 last:border-b-0"
          >
            <div>
              <p className="font-body text-white text-sm">{event.title}</p>
              <p className="font-body text-white/40 text-xs tracking-wider mt-0.5">
                {new Date(event.date).toLocaleDateString("en-US", {
                  month: "long",
                  day: "numeric",
                  year: "numeric",
                })}
              </p>
            </div>
            <ChromeButton
              variant="secondary"
              href={event.signed_url}
              target="_blank"
              rel="noopener noreferrer"
            >
              View
            </ChromeButton>
          </div>
        ))
      )}

      {/* Leadership section */}
      <Divider className="mt-10 mb-6" />
      <SectionTitle as="h2" className="text-xl mb-4">T6 Leadership</SectionTitle>

      {leadersLoading ? (
        <>
          <SkeletonRow />
          <SkeletonRow />
          <SkeletonRow />
        </>
      ) : leadersError ? (
        <p className="font-body text-white/40 text-sm py-4">
          Could not load leadership contacts. Please refresh the page.
        </p>
      ) : leaders.length === 0 ? (
        <p className="font-body text-white/40 text-sm py-4">
          No leadership contacts posted yet.
        </p>
      ) : (
        leaders.map((leader) => (
          <div
            key={leader.id}
            className="flex items-center justify-between py-4 border-b border-chrome/10 last:border-b-0"
          >
            <div>
              <p className="font-body text-white text-sm">{leader.name}</p>
              <p className="font-body text-white/40 text-xs tracking-wider uppercase mt-0.5">
                {leader.role}
              </p>
            </div>
            <a
              href={`mailto:${leader.email}`}
              className="font-body text-green underline text-sm hover:text-green/80 transition-colors"
            >
              {leader.email}
            </a>
          </div>
        ))
      )}
    </main>
  );
}
