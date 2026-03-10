import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  transpilePackages: ["sonner"],
  output: "standalone",
};

export default nextConfig;
