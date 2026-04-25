"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { GraduationCap, MessageSquare, Info } from "lucide-react";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { cn } from "@/lib/utils";

export function Navbar() {
  const pathname = usePathname();

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 h-14 flex items-center justify-between px-6 border-b border-white/[0.07] bg-[#09090b]/95 backdrop-blur-md">
      {/* Logo */}
      <Link href="/" className="flex items-center gap-2.5 group">
        <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center shadow-lg shadow-indigo-600/30">
          <GraduationCap className="w-4 h-4 text-white" />
        </div>
        <span className="font-semibold text-white text-sm tracking-tight">
          AcaIntel AI
        </span>
      </Link>

      {/* Center tabs */}
      <div className="flex items-center gap-0.5 bg-white/[0.04] rounded-lg p-1 border border-white/[0.06]">
        <Link
          href="/chat"
          className={cn(
            "flex items-center gap-1.5 px-3.5 py-1.5 rounded-md text-[13px] font-medium transition-all",
            pathname === "/chat"
              ? "bg-white/10 text-white shadow-sm"
              : "text-white/45 hover:text-white/75 hover:bg-white/[0.04]"
          )}
        >
          <MessageSquare className="w-3.5 h-3.5" />
          Chat
        </Link>
        <Link
          href="/how-it-works"
          className={cn(
            "flex items-center gap-1.5 px-3.5 py-1.5 rounded-md text-[13px] font-medium transition-all",
            pathname === "/how-it-works"
              ? "bg-white/10 text-white shadow-sm"
              : "text-white/45 hover:text-white/75 hover:bg-white/[0.04]"
          )}
        >
          <Info className="w-3.5 h-3.5" />
          How it works
        </Link>
      </div>

      {/* Right side */}
      <div className="flex items-center gap-3">
        <span className="text-[13px] text-white/40 hidden sm:block">
          Academic City Portal
        </span>
        <div className="relative">
          <Avatar className="size-8">
            <AvatarFallback className="bg-gradient-to-br from-indigo-500 to-indigo-700 text-white text-[11px] font-semibold">
              AC
            </AvatarFallback>
          </Avatar>
          <span className="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 bg-emerald-500 rounded-full border-2 border-[#09090b]" />
        </div>
      </div>
    </nav>
  );
}
