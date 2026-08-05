import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Produces a minimal, self-contained server bundle (server.js + only the
  // node_modules it actually needs) -- a much smaller Docker image than
  // shipping the whole node_modules tree, and the standard real-world choice.
  output: "standalone",
};

export default nextConfig;
