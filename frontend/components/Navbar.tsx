"use client";

import Link from "next/link";
import { useAuth } from "@/lib/auth-context";

export default function Navbar() {
  const { user, logout } = useAuth();

  if (!user) return null;

  return (
    <header className="flex items-center gap-7 bg-slate-900 text-white px-6 py-3">
      <Link href="/" className="font-extrabold text-lg">
        CampusConnect
      </Link>
      <nav className="flex gap-5 flex-1 text-sm font-semibold">
        <Link href="/" className="text-slate-200 hover:text-white">
          Feed
        </Link>
        <Link href="/forums" className="text-slate-200 hover:text-white">
          Forums
        </Link>
        <Link href="/projects" className="text-slate-200 hover:text-white">
          Projects
        </Link>
        <Link href="/notifications" className="text-slate-200 hover:text-white">
          Notifications
        </Link>
      </nav>
      <div className="flex items-center gap-4 text-xs text-slate-300">
        <span>
          {user.name} &middot; {user.department}
        </span>
        <button onClick={() => logout()} className="text-white font-semibold hover:underline">
          Log out
        </button>
      </div>
    </header>
  );
}
