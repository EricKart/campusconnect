export interface User {
  id: number;
  name: string;
  email: string;
  department: string;
  year: number;
  bio: string;
  skills: string;
}

export interface Comment {
  id: number;
  body: string;
  created_at: string;
  author: User;
}

export interface Post {
  id: number;
  body: string;
  tags: string;
  type: string;
  created_at: string;
  author: User;
  like_count: number;
  comment_count: number;
  liked_by_me: boolean;
  comments: Comment[];
}

export interface Forum {
  id: number;
  name: string;
  slug: string;
  description: string;
  thread_count: number;
}

export interface Thread {
  id: number;
  title: string;
  body: string;
  created_at: string;
  author: User;
  reply_count: number;
}

export interface ThreadReply {
  id: number;
  body: string;
  created_at: string;
  author: User;
}

export interface ThreadDetail extends Thread {
  replies: ThreadReply[];
}

export interface TeamRequest {
  id: number;
  status: "pending" | "accepted" | "rejected";
  message: string;
  requester: User;
}

export interface Project {
  id: number;
  post: Post;
  skills_needed: string;
  hackathon_name: string;
  deadline: string | null;
  team_requests: TeamRequest[];
  my_request_status: string | null;
}

export interface Notification {
  id: number;
  type: string;
  payload: string;
  is_read: boolean;
  created_at: string;
}
