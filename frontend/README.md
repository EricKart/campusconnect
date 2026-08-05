# CampusConnect Frontend

Next.js (App Router, TypeScript, Tailwind). Talks directly to the FastAPI backend from the browser
using `fetch(..., { credentials: "include" })` so the httpOnly JWT cookie set at login is sent
automatically -- see `lib/api.ts` and `lib/auth-context.tsx`.

## Local development (outside Docker)

```bash
npm install
cp .env.local.example .env.local
npm run dev
```

Requires the backend running separately (see `../backend/README.md` or the root `README.md`).

## Structure

```
app/            -- one folder per route (App Router)
components/     -- Navbar, RequireAuth (client-side route guard)
lib/api.ts       -- fetch wrapper, always sends credentials
lib/auth-context.tsx  -- current-user React context (login/register/logout)
lib/types.ts      -- TypeScript types matching the backend's Pydantic schemas
```
