"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import RequireAuth from "@/components/RequireAuth";
import { api } from "@/lib/api";
import { ThreadDetail } from "@/lib/types";

function ThreadDetailContent() {
  const params = useParams<{ id: string }>();
  const [thread, setThread] = useState<ThreadDetail | null>(null);
  const [reply, setReply] = useState("");

  async function load() {
    setThread(await api.get<ThreadDetail>(`/forums/thread/${params.id}`));
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [params.id]);

  async function submitReply(e: React.FormEvent) {
    e.preventDefault();
    if (!reply.trim()) return;
    await api.post(`/forums/thread/${params.id}/replies`, { body: reply });
    setReply("");
    load();
  }

  if (!thread) return null;

  return (
    <div>
      <div className="bg-white border border-slate-200 rounded-xl p-4 mb-5">
        <h1 className="text-lg font-bold text-slate-900">{thread.title}</h1>
        <p className="text-xs text-slate-500 mt-1">
          {thread.author.name} &middot; {thread.author.department} &middot; {new Date(thread.created_at).toLocaleString()}
        </p>
        <p className="text-sm mt-2 whitespace-pre-wrap">{thread.body}</p>
      </div>

      <h2 className="text-sm font-bold text-slate-900 mb-2">
        {thread.replies.length} Repl{thread.replies.length === 1 ? "y" : "ies"}
      </h2>
      {thread.replies.map((r) => (
        <div key={r.id} className="bg-white border border-slate-200 rounded-xl p-4 mb-3">
          <p className="text-xs text-slate-500">{r.author.name} &middot; {new Date(r.created_at).toLocaleString()}</p>
          <p className="text-sm mt-1 whitespace-pre-wrap">{r.body}</p>
        </div>
      ))}

      <form onSubmit={submitReply} className="bg-white border border-slate-200 rounded-xl p-4 mt-4 flex flex-col gap-2">
        <textarea placeholder="Write a reply..." value={reply} onChange={(e) => setReply(e.target.value)} required className="border border-slate-300 rounded-lg px-3 py-2 text-sm min-h-16" />
        <button type="submit" className="self-start bg-slate-900 text-white font-semibold rounded-lg px-4 py-2 text-sm hover:bg-slate-700">
          Reply
        </button>
      </form>
    </div>
  );
}

export default function ThreadPage() {
  return (
    <RequireAuth>
      <ThreadDetailContent />
    </RequireAuth>
  );
}
