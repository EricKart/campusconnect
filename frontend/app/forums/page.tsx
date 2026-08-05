"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import RequireAuth from "@/components/RequireAuth";
import { api } from "@/lib/api";
import { Forum } from "@/lib/types";

function ForumsContent() {
  const [forums, setForums] = useState<Forum[]>([]);

  useEffect(() => {
    api.get<Forum[]>("/forums").then(setForums);
  }, []);

  return (
    <div>
      <h1 className="text-xl font-bold text-slate-900 mb-4">Forums</h1>
      <div className="flex flex-col gap-3">
        {forums.map((f) => (
          <Link key={f.id} href={`/forums/${f.slug}`} className="bg-white border border-slate-200 rounded-xl p-4 block hover:border-slate-400">
            <h2 className="text-sm font-bold text-slate-900">{f.name}</h2>
            <p className="text-xs text-slate-500 mt-1">{f.description}</p>
            <p className="text-xs text-slate-400 mt-1">{f.thread_count} thread{f.thread_count !== 1 ? "s" : ""}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}

export default function ForumsPage() {
  return (
    <RequireAuth>
      <ForumsContent />
    </RequireAuth>
  );
}
