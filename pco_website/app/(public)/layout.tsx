import { SiteLayout } from "@/components/layout/SiteLayout";

export default function PublicLayout({ children }: { children: React.ReactNode }) {
  return <SiteLayout>{children}</SiteLayout>;
}
