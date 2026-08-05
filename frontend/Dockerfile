# --- CampusConnect frontend, containerized ---
# Multi-stage build: install deps, build the standalone server, then ship
# ONLY the standalone output in the final image -- not the full node_modules
# tree or the source .tsx files.

FROM node:20-slim AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm install

FROM node:20-slim AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
# Baked in at build time -- the browser needs this to know where the API is.
ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
RUN npm run build

FROM node:20-slim AS runner
WORKDIR /app
ENV NODE_ENV=production
# The node:20-slim base image can lag behind Debian's own security patches
# (Trivy caught libgnutls30 CRITICAL CVE-2026-33845/42010 here) -- pulling
# the latest patched packages at build time, not just at image-publish time.
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*
# The runtime here only ever runs `node server.js` -- it never runs `npm`.
# But every node:*-slim image ships npm's own CLI pre-installed, and ITS
# bundled dependencies (not ours -- Trivy's file path made that clear:
# usr/local/lib/node_modules/npm/...) had a CRITICAL CVE in a vulnerable
# `tar` version. Removing the package manager we never use both fixes the
# CVE and shrinks the production image's attack surface.
RUN rm -rf /usr/local/lib/node_modules/npm /usr/local/bin/npm /usr/local/bin/npx
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000
CMD ["node", "server.js"]
