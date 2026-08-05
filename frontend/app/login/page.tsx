"use client";

import { useState } from "react";
import Link from "next/link";
import { useAuth, ApiError } from "@/lib/auth-context";

export default function LoginPage() {
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await login(email, password);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="max-w-sm mx-auto mt-16 bg-white border border-slate-200 rounded-xl p-7">
      <h1 className="text-xl font-bold text-slate-900 text-center mb-5">Welcome Back</h1>
      {error && <div className="bg-red-50 border border-red-200 text-red-800 text-sm rounded-lg p-3 mb-4">{error}</div>}
      <form onSubmit={handleSubmit} className="flex flex-col gap-3">
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className="border border-slate-300 rounded-lg px-3 py-2 text-sm"
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          className="border border-slate-300 rounded-lg px-3 py-2 text-sm"
        />
        <button
          type="submit"
          disabled={submitting}
          className="bg-slate-900 text-white font-semibold rounded-lg py-2 text-sm hover:bg-slate-700 disabled:opacity-60"
        >
          {submitting ? "Logging in..." : "Log In"}
        </button>
      </form>
      <p className="text-xs text-slate-500 text-center mt-4">
        New here? <Link href="/register" className="text-blue-700 font-semibold">Create an account</Link>
      </p>
    </div>
  );
}
