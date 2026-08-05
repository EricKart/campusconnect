"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import RequireAuth from "@/components/RequireAuth";
import { api } from "@/lib/api";
import { Thread } from "@/lib/types";

function ForumDetailContent() {
  const params = useParams<{ slug: string }>();
  const [threads, setThreads] = useState<Thread[]>([]);
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");

  async function load() {
    setThreads(await api.get<Thread[]>(`/forums/${params.slug}`));
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [params.slug]);

  async function submitThread(e: React.FormEvent) {
    e.preventDefault();
    if (!title.trim() || !body.trim()) return;
    await api.post(`/forums/${params.slug}`, { title, body });
    setTitle("");
    setBody("");
    load();
  }

  return (
    <div>
      <p className="mb-3">
        <Link href="/forums" className="text-xs text-blue-700 font-semibold">&larr; All forums</Link>
      </p>
      <h1 className="text-xl font-bold text-slate-900 mb-4">{params.slug.replace(/-/g, " ")}</h1>

      <form onSubmit={submitThread} className="bg-white border border-slate-200 rounded-xl p-4 mb-5 flex flex-col gap-2">
        <input placeholder="Thread title" value={title} onChange={(e) => setTitle(e.target.value)} required className="border border-slate-300 rounded-lg px-3 py-2 text-sm" />
        <textarea placeholder="What do you want to ask or discuss?" value={body} onChange={(e) => setBody(e.target.value)} required className="border border-slate-300 rounded-lg px-3 py-2 text-sm min-h-16" />
        <button type="submit" className="self-start bg-slate-900 text-white font-semibold rounded-lg px-4 py-2 text-sm hover:bg-slate-700">
          Start Thread
        </button>
      </form>

      {threads.length === 0 && <p className="text-sm text-slate-500">No threads yet -- start the first discussion.</p>}

      <div className="flex flex-col gap-3">
        {threads.map((t) => (
          <Link key={t.id} href={`/forums/thread/${t.id}`} className="bg-white border border-slate-200 rounded-xl p-4 block hover:border-slate-400">
            <h2 className="text-sm font-bold text-slate-900">{t.title}</h2>
            <p className="text-xs text-slate-500 mt-1">
              {t.author.name} &middot; {new Date(t.created_at).toLocaleDateString()} &middot; {t.reply_count} repl{t.reply_count === 1 ? "y" : "ies"}
            </p>
          </Link>
        ))}
      </div>
    </div>
  );
}

export default function ForumDetailPage() {
  return (
    <RequireAuth>
      <ForumDetailContent />
    </RequireAuth>
  );
}
