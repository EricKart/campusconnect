import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "@/lib/auth-context";
import Navbar from "@/components/Navbar";

export const metadata: Metadata = {
  title: "CampusConnect",
  description: "A LinkedIn-for-college platform -- the byteXL DevOps bootcamp capstone app.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="h-full">
      <body className="min-h-full flex flex-col bg-slate-50 text-slate-900 font-sans">
        <AuthProvider>
          <Navbar />
          <main className="flex-1 w-full max-w-3xl mx-auto px-5 py-6">{children}</main>
        </AuthProvider>
      </body>
    </html>
  );
}
