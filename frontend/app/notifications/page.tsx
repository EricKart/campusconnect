"use client";

import { useEffect, useState } from "react";
import RequireAuth from "@/components/RequireAuth";
import { api } from "@/lib/api";
import { Notification } from "@/lib/types";

function NotificationsContent() {
  const [notes, setNotes] = useState<Notification[]>([]);

  useEffect(() => {
    api.get<Notification[]>("/notifications").then(setNotes);
  }, []);

  return (
    <div>
      <h1 className="text-xl font-bold text-slate-900 mb-1">Notifications</h1>
      <p className="text-xs text-slate-500 mb-4">
        Every row here was written by the <code>worker</code> process, not the page that triggered it.
      </p>

      {notes.length === 0 && (
        <p className="text-sm text-slate-500">
          No notifications yet. Comment, like, or send a team request on another account to generate one.
        </p>
      )}

      <div className="bg-white border border-slate-200 rounded-xl divide-y divide-slate-100">
        {notes.map((n) => (
          <div key={n.id} className={`flex items-center gap-3 px-4 py-3 ${!n.is_read ? "bg-blue-50/50" : ""}`}>
            <span className="text-[10px] font-extrabold uppercase text-teal-700 w-24 shrink-0">
              {n.type.replace(/_/g, " ")}
            </span>
            <span className="text-sm flex-1">{n.payload}</span>
            <span className="text-xs text-slate-400 whitespace-nowrap">{new Date(n.created_at).toLocaleString()}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function NotificationsPage() {
  return (
    <RequireAuth>
      <NotificationsContent />
    </RequireAuth>
  );
}
