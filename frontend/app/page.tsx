"use client";

import { useEffect, useState } from "react";
import RequireAuth from "@/components/RequireAuth";
import { api } from "@/lib/api";
import { Post } from "@/lib/types";

function FeedContent() {
  const [posts, setPosts] = useState<Post[]>([]);
  const [body, setBody] = useState("");
  const [tags, setTags] = useState("");
  const [commentDrafts, setCommentDrafts] = useState<Record<number, string>>({});

  async function load() {
    setPosts(await api.get<Post[]>("/posts"));
  }

  useEffect(() => {
    load();
  }, []);

  async function submitPost(e: React.FormEvent) {
    e.preventDefault();
    if (!body.trim()) return;
    await api.post("/posts", { body, tags });
    setBody("");
    setTags("");
    load();
  }

  async function toggleLike(postId: number) {
    await api.post(`/posts/${postId}/like`);
    load();
  }

  async function submitComment(postId: number) {
    const draft = commentDrafts[postId];
    if (!draft?.trim()) return;
    await api.post(`/posts/${postId}/comments`, { body: draft });
    setCommentDrafts((d) => ({ ...d, [postId]: "" }));
    load();
  }

  return (
    <div>
      <h1 className="text-xl font-bold text-slate-900 mb-4">Feed</h1>

      <form onSubmit={submitPost} className="bg-white border border-slate-200 rounded-xl p-4 mb-5 flex flex-col gap-2">
        <textarea
          placeholder="Share an update with campus..."
          value={body}
          onChange={(e) => setBody(e.target.value)}
          required
          className="border border-slate-300 rounded-lg px-3 py-2 text-sm min-h-16"
        />
        <input
          placeholder="Tags (comma-separated, optional)"
          value={tags}
          onChange={(e) => setTags(e.target.value)}
          className="border border-slate-300 rounded-lg px-3 py-2 text-sm"
        />
        <button type="submit" className="self-start bg-slate-900 text-white font-semibold rounded-lg px-4 py-2 text-sm hover:bg-slate-700">
          Post
        </button>
      </form>

      {posts.length === 0 && <p className="text-sm text-slate-500">No posts yet -- be the first to share something.</p>}

      {posts.map((post) => (
        <div key={post.id} className="bg-white border border-slate-200 rounded-xl p-4 mb-4">
          <div className="text-xs text-slate-500 mb-1">
            {post.author.name} &middot; {post.author.department} &middot; {new Date(post.created_at).toLocaleString()}
          </div>
          <div className="text-sm whitespace-pre-wrap">{post.body}</div>
          {post.tags && (
            <div className="mt-2 flex gap-1 flex-wrap">
              {post.tags.split(",").filter(Boolean).map((t) => (
                <span key={t} className="bg-slate-100 text-slate-600 text-xs rounded-full px-2 py-0.5">{t.trim()}</span>
              ))}
            </div>
          )}
          <div className="flex items-center gap-4 mt-3">
            <button
              onClick={() => toggleLike(post.id)}
              className={`text-xs font-semibold ${post.liked_by_me ? "text-emerald-700" : "text-blue-700"}`}
            >
              {post.liked_by_me ? "♥ Liked" : "♡ Like"} ({post.like_count})
            </button>
            <span className="text-xs text-slate-500">
              {post.comment_count} comment{post.comment_count !== 1 ? "s" : ""}
            </span>
          </div>

          {post.comments.length > 0 && (
            <div className="mt-3 pt-2 border-t border-slate-100 flex flex-col gap-1">
              {post.comments.map((c) => (
                <div key={c.id} className="text-sm">
                  <b className="text-slate-900">{c.author.name}:</b> {c.body}
                </div>
              ))}
            </div>
          )}

          <div className="mt-3 flex gap-2">
            <input
              placeholder="Write a comment..."
              value={commentDrafts[post.id] || ""}
              onChange={(e) => setCommentDrafts((d) => ({ ...d, [post.id]: e.target.value }))}
              className="flex-1 border border-slate-300 rounded-lg px-3 py-1.5 text-sm"
            />
            <button
              onClick={() => submitComment(post.id)}
              className="bg-slate-100 text-slate-700 font-semibold rounded-lg px-3 py-1.5 text-xs hover:bg-slate-200"
            >
              Reply
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}

export default function FeedPage() {
  return (
    <RequireAuth>
      <FeedContent />
    </RequireAuth>
  );
}
