// DEV ONLY — renders all design system components for visual inspection
// This page is NOT linked from anywhere; navigate to /dev-preview manually
// Remove or gate behind NODE_ENV check before production if desired

import { ChromeCard } from "@/components/ui/ChromeCard";
import { ChromeButton } from "@/components/ui/ChromeButton";
import { SectionTitle } from "@/components/ui/SectionTitle";
import { Divider } from "@/components/ui/Divider";

export default function DevPreviewPage() {
  return (
    <div className="min-h-screen bg-black p-8 space-y-16">
      <header className="text-center">
        <h1 className="font-heading text-chrome text-2xl tracking-[0.3em] uppercase mb-2">
          Design System Preview
        </h1>
        <p className="text-white/40 text-sm tracking-wider">Phase 1 — Visual QA</p>
      </header>

      {/* Typography */}
      <section className="space-y-4">
        <p className="text-chrome/60 text-xs tracking-widest uppercase mb-4">Typography</p>
        <SectionTitle as="h1">Heading H1 — Cormorant Garamond</SectionTitle>
        <SectionTitle as="h2">Heading H2 — Section Title</SectionTitle>
        <SectionTitle as="h3" className="text-xl">Heading H3 — Subheading</SectionTitle>
        <p className="text-white/70 font-body text-base leading-relaxed max-w-prose">
          Body text in EB Garamond. The quick brown fox jumps over the lazy dog. This elegant
          serif typeface pairs editorial restraint with high readability at body sizes.
        </p>
      </section>

      <Divider />

      {/* ChromeButton */}
      <section className="space-y-4">
        <p className="text-chrome/60 text-xs tracking-widest uppercase mb-4">ChromeButton — Hover to test sheen</p>
        <div className="flex flex-wrap gap-4">
          <ChromeButton variant="primary">Primary Button</ChromeButton>
          <ChromeButton variant="secondary">Secondary Button</ChromeButton>
          <ChromeButton variant="primary" disabled>Disabled Primary</ChromeButton>
        </div>
      </section>

      <Divider />

      {/* ChromeCard */}
      <section className="space-y-4">
        <p className="text-chrome/60 text-xs tracking-widest uppercase mb-4">ChromeCard — Hover to test glow</p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl">
          <ChromeCard>
            <SectionTitle as="h3" className="text-xl mb-2">Card Title</SectionTitle>
            <p className="text-white/60 text-sm">Card body text. Hover this card to see the subtle green glow appear.</p>
          </ChromeCard>
          <ChromeCard>
            <SectionTitle as="h3" className="text-xl mb-2">Second Card</SectionTitle>
            <p className="text-white/60 text-sm">Another card demonstrating the metallic gradient border.</p>
          </ChromeCard>
          <ChromeCard>
            <SectionTitle as="h3" className="text-xl mb-2">Third Card</SectionTitle>
            <p className="text-white/60 text-sm">The border gradient runs from silver/white at top-left to transparent at bottom-right.</p>
          </ChromeCard>
        </div>
      </section>

      <Divider showDot={true} />

      {/* Divider variants */}
      <section className="space-y-6 max-w-2xl">
        <p className="text-chrome/60 text-xs tracking-widest uppercase">Divider — with and without dot</p>
        <Divider showDot={true} />
        <Divider showDot={false} />
      </section>

      {/* Toast trigger note */}
      <section className="space-y-4">
        <p className="text-chrome/60 text-xs tracking-widest uppercase">Toast (Sonner)</p>
        <p className="text-white/50 text-sm">
          To test toasts, open browser console and run:
        </p>
        <code className="block bg-card-elevated text-chrome text-sm p-4 rounded border border-white/10">
          {`// In browser console:\nimport('sonner').then(m => { m.toast.success("Success!"); m.toast.error("Error!"); })`}
        </code>
      </section>
    </div>
  );
}
