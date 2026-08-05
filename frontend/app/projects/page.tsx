"use client";

import { useEffect, useState } from "react";
import RequireAuth from "@/components/RequireAuth";
import { useAuth } from "@/lib/auth-context";
import { api } from "@/lib/api";
import { Project } from "@/lib/types";

const STATUS_STYLE: Record<string, string> = {
  pending: "bg-amber-50 text-amber-700",
  accepted: "bg-emerald-50 text-emerald-700",
  rejected: "bg-red-50 text-red-700",
};

function ProjectsContent() {
  const { user } = useAuth();
  const [projects, setProjects] = useState<Project[]>([]);
  const [body, setBody] = useState("");
  const [skillsNeeded, setSkillsNeeded] = useState("");
  const [hackathonName, setHackathonName] = useState("");
  const [deadline, setDeadline] = useState("");
  const [joinDrafts, setJoinDrafts] = useState<Record<number, string>>({});

  async function load() {
    setProjects(await api.get<Project[]>("/projects"));
  }

  useEffect(() => {
    load();
  }, []);

  async function submitProject(e: React.FormEvent) {
    e.preventDefault();
    if (!body.trim()) return;
    await api.post("/projects", {
      body,
      skills_needed: skillsNeeded,
      hackathon_name: hackathonName,
      deadline: deadline || null,
    });
    setBody("");
    setSkillsNeeded("");
    setHackathonName("");
    setDeadline("");
    load();
  }

  async function requestToJoin(projectId: number) {
    await api.post(`/projects/${projectId}/join`, { message: joinDrafts[projectId] || "" });
    load();
  }

  async function decide(requestId: number, decision: "accepted" | "rejected") {
    await api.post(`/projects/requests/${requestId}/${decision}`);
    load();
  }

  return (
    <div>
      <h1 className="text-xl font-bold text-slate-900 mb-1">Project Board</h1>
      <p className="text-xs text-slate-500 mb-4">Post a project or hackathon idea, or request to join someone else&apos;s.</p>

      <form onSubmit={submitProject} className="bg-white border border-slate-200 rounded-xl p-4 mb-5 flex flex-col gap-2">
        <textarea placeholder="Describe your project or hackathon idea..." value={body} onChange={(e) => setBody(e.target.value)} required className="border border-slate-300 rounded-lg px-3 py-2 text-sm min-h-16" />
        <input placeholder="Skills needed (comma-separated)" value={skillsNeeded} onChange={(e) => setSkillsNeeded(e.target.value)} className="border border-slate-300 rounded-lg px-3 py-2 text-sm" />
        <input placeholder="Hackathon name (optional)" value={hackathonName} onChange={(e) => setHackathonName(e.target.value)} className="border border-slate-300 rounded-lg px-3 py-2 text-sm" />
        <input type="date" value={deadline} onChange={(e) => setDeadline(e.target.value)} className="border border-slate-300 rounded-lg px-3 py-2 text-sm" />
        <button type="submit" className="self-start bg-slate-900 text-white font-semibold rounded-lg px-4 py-2 text-sm hover:bg-slate-700">
          Post Project
        </button>
      </form>

      {projects.length === 0 && <p className="text-sm text-slate-500">No projects posted yet -- be the first.</p>}

      {projects.map((project) => {
        const isOwner = project.post.author.id === user?.id;
        const skills = project.skills_needed.split(",").filter(Boolean);
        return (
          <div key={project.id} className="bg-white border border-slate-200 rounded-xl p-4 mb-4">
            <div className="text-xs text-slate-500 mb-1">
              {project.post.author.name} &middot; {project.post.author.department} &middot; {new Date(project.post.created_at).toLocaleDateString()}
            </div>
            <p className="text-sm">{project.post.body}</p>
            {project.hackathon_name && <p className="text-xs text-slate-500 mt-1"><b>Hackathon:</b> {project.hackathon_name}</p>}
            {project.deadline && <p className="text-xs text-slate-500"><b>Deadline:</b> {project.deadline}</p>}
            {skills.length > 0 && (
              <div className="mt-2 flex gap-1 flex-wrap">
                {skills.map((s) => <span key={s} className="bg-slate-100 text-slate-600 text-xs rounded-full px-2 py-0.5">{s.trim()}</span>)}
              </div>
            )}

            {isOwner ? (
              <div className="mt-4">
                <h2 className="text-xs font-bold text-slate-700 uppercase tracking-wide mb-2">Join Requests</h2>
                {project.team_requests.length === 0 && <p className="text-xs text-slate-400">No requests yet.</p>}
                {project.team_requests.map((tr) => (
                  <div key={tr.id} className="flex items-center justify-between py-1.5 text-sm">
                    <span>{tr.requester.name}{tr.message && <span className="text-slate-500"> &mdash; &quot;{tr.message}&quot;</span>}</span>
                    {tr.status === "pending" ? (
                      <span className="flex gap-2">
                        <button onClick={() => decide(tr.id, "accepted")} className="text-xs bg-emerald-600 text-white rounded-md px-2 py-1 font-semibold">Accept</button>
                        <button onClick={() => decide(tr.id, "rejected")} className="text-xs bg-red-600 text-white rounded-md px-2 py-1 font-semibold">Reject</button>
                      </span>
                    ) : (
                      <span className={`text-xs font-semibold rounded-full px-2 py-0.5 ${STATUS_STYLE[tr.status]}`}>{tr.status}</span>
                    )}
                  </div>
                ))}
              </div>
            ) : project.my_request_status ? (
              <p className="mt-3 text-sm">
                Your request: <span className={`text-xs font-semibold rounded-full px-2 py-0.5 ${STATUS_STYLE[project.my_request_status]}`}>{project.my_request_status}</span>
              </p>
            ) : (
              <div className="mt-3 flex gap-2">
                <input
                  placeholder="Optional message to the project owner"
                  value={joinDrafts[project.id] || ""}
                  onChange={(e) => setJoinDrafts((d) => ({ ...d, [project.id]: e.target.value }))}
                  className="flex-1 border border-slate-300 rounded-lg px-3 py-1.5 text-sm"
                />
                <button onClick={() => requestToJoin(project.id)} className="bg-slate-100 text-slate-700 font-semibold rounded-lg px-3 py-1.5 text-xs hover:bg-slate-200">
                  Request to Join
                </button>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

export default function ProjectsPage() {
  return (
    <RequireAuth>
      <ProjectsContent />
    </RequireAuth>
  );
}
