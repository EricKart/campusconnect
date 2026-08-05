"use client";

import { useState } from "react";
import Link from "next/link";
import { useAuth, ApiError } from "@/lib/auth-context";

export default function RegisterPage() {
  const { register } = useAuth();
  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    department: "",
    year: 4,
    skills: "",
    bio: "",
  });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  function update<K extends keyof typeof form>(key: K, value: (typeof form)[K]) {
    setForm((f) => ({ ...f, [key]: value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await register(form);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="max-w-sm mx-auto mt-10 bg-white border border-slate-200 rounded-xl p-7">
      <h1 className="text-xl font-bold text-slate-900 text-center mb-5">Join CampusConnect</h1>
      {error && <div className="bg-red-50 border border-red-200 text-red-800 text-sm rounded-lg p-3 mb-4">{error}</div>}
      <form onSubmit={handleSubmit} className="flex flex-col gap-3">
        <input placeholder="Full name" required value={form.name} onChange={(e) => update("name", e.target.value)} className="border border-slate-300 rounded-lg px-3 py-2 text-sm" />
        <input type="email" placeholder="Email" required value={form.email} onChange={(e) => update("email", e.target.value)} className="border border-slate-300 rounded-lg px-3 py-2 text-sm" />
        <input type="password" placeholder="Password (min 6 characters)" required minLength={6} value={form.password} onChange={(e) => update("password", e.target.value)} className="border border-slate-300 rounded-lg px-3 py-2 text-sm" />
        <input placeholder="Department, e.g. Computer Science" required value={form.department} onChange={(e) => update("department", e.target.value)} className="border border-slate-300 rounded-lg px-3 py-2 text-sm" />
        <select value={form.year} onChange={(e) => update("year", Number(e.target.value))} className="border border-slate-300 rounded-lg px-3 py-2 text-sm">
          <option value={1}>1st Year</option>
          <option value={2}>2nd Year</option>
          <option value={3}>3rd Year</option>
          <option value={4}>4th Year</option>
        </select>
        <input placeholder="Skills (comma-separated)" value={form.skills} onChange={(e) => update("skills", e.target.value)} className="border border-slate-300 rounded-lg px-3 py-2 text-sm" />
        <textarea placeholder="Short bio" value={form.bio} onChange={(e) => update("bio", e.target.value)} className="border border-slate-300 rounded-lg px-3 py-2 text-sm min-h-16" />
        <button type="submit" disabled={submitting} className="bg-slate-900 text-white font-semibold rounded-lg py-2 text-sm hover:bg-slate-700 disabled:opacity-60">
          {submitting ? "Creating account..." : "Create Account"}
        </button>
      </form>
      <p className="text-xs text-slate-500 text-center mt-4">
        Already have an account? <Link href="/login" className="text-blue-700 font-semibold">Log in</Link>
      </p>
    </div>
  );
}
