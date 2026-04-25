"use client";

import { useState, useRef } from "react";
import { useRouter } from "next/navigation";
import {
  Search,
  Send,
  ChevronDown,
  Clock,
  TrendingUp,
  MapPin,
  Users,
  FileText,
  Database,
} from "lucide-react";
import { Footer } from "@/components/Footer";
import { cn } from "@/lib/utils";

const SUGGESTIONS = [
  {
    icon: Clock,
    text: "What is the theme of the 2025 budget?",
    color: "text-violet-400",
    bg: "bg-violet-500/10",
  },
  {
    icon: TrendingUp,
    text: "What does the budget say about inflation?",
    color: "text-blue-400",
    bg: "bg-blue-500/10",
  },
  {
    icon: MapPin,
    text: "Who won in Ashanti Region?",
    color: "text-emerald-400",
    bg: "bg-emerald-500/10",
  },
  {
    icon: Users,
    text: "Compare NPP and NDC votes",
    color: "text-amber-400",
    bg: "bg-amber-500/10",
  },
] as const;

const DEMO_SETTINGS = [
  { label: "TOP K RESULTS", key: "topK", default: 5, min: 1, max: 20 },
  { label: "CANDIDATE K", key: "candidateK", default: 25, min: 5, max: 100 },
  { label: "TEMPERATURE", key: "temp", default: 0.2, min: 0, max: 1, step: 0.1 },
] as const;

export default function HomePage() {
  const [query, setQuery] = useState("");
  const [settingsOpen, setSettingsOpen] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();

  const navigate = (q: string) => {
    const trimmed = q.trim();
    if (!trimmed) return;
    router.push(`/chat?q=${encodeURIComponent(trimmed)}`);
  };

  return (
    <div className="min-h-screen pt-14 flex flex-col">
      {/* Hero area */}
      <div className="flex-1 flex flex-col items-center justify-center px-4 py-16">
        <div className="w-full max-w-[680px] mx-auto flex flex-col gap-8">

          {/* Badge */}
          <div className="flex justify-center">
            <span className="inline-flex items-center gap-2 text-[10px] font-semibold tracking-[0.2em] text-white/35 border border-white/[0.09] rounded-full px-4 py-1.5 uppercase">
              Academic City University Research Tool
            </span>
          </div>

          {/* Heading */}
          <div className="text-center space-y-4">
            <h1 className="text-[2.75rem] sm:text-5xl font-bold text-white tracking-tight leading-[1.1]">
              Welcome to{" "}
              <span className="bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent">
                AcaIntel AI
              </span>
            </h1>
            <p className="text-[15px] text-white/45 max-w-md mx-auto leading-relaxed">
              Your high-precision academic partner for Ghanaian dataset
              analysis, specializing in Budget Statements and Election Results.
            </p>
          </div>

          {/* Suggestion cards */}
          <div className="grid grid-cols-2 gap-2.5">
            {SUGGESTIONS.map(({ icon: Icon, text, color, bg }) => (
              <button
                key={text}
                onClick={() => navigate(text)}
                className="flex items-start gap-3 p-4 rounded-xl border border-white/[0.07] bg-white/[0.025] hover:bg-white/[0.05] hover:border-white/[0.12] transition-all text-left group cursor-pointer"
              >
                <div
                  className={cn(
                    "w-8 h-8 rounded-lg flex items-center justify-center shrink-0 mt-0.5",
                    bg
                  )}
                >
                  <Icon className={cn("w-4 h-4", color)} />
                </div>
                <span className="text-[13px] text-white/55 group-hover:text-white/80 transition-colors leading-relaxed">
                  {text}
                </span>
              </button>
            ))}
          </div>

          {/* Technical demo settings */}
          <div className="rounded-xl border border-white/[0.06] overflow-hidden">
            <button
              onClick={() => setSettingsOpen((v) => !v)}
              className="w-full flex items-center justify-between px-5 py-3.5 text-left hover:bg-white/[0.02] transition-colors"
            >
              <div className="flex items-center gap-2 text-[10px] font-semibold tracking-[0.2em] text-white/25 uppercase">
                <Database className="w-3.5 h-3.5" />
                Technical Demo Settings
              </div>
              <ChevronDown
                className={cn(
                  "w-4 h-4 text-white/20 transition-transform duration-200",
                  settingsOpen && "rotate-180"
                )}
              />
            </button>
            {settingsOpen && (
              <div className="px-5 pb-5 pt-1 border-t border-white/[0.06] grid grid-cols-3 gap-4">
                {DEMO_SETTINGS.map((s) => (
                  <div key={s.key} className="space-y-1.5">
                    <label className="text-[10px] tracking-widest text-white/25 uppercase">
                      {s.label}
                    </label>
                    <input
                      type="number"
                      defaultValue={s.default}
                      min={s.min}
                      max={s.max}
                      step={"step" in s ? s.step : 1}
                      className="w-full px-3 py-2 rounded-lg bg-white/[0.04] border border-white/[0.07] text-sm text-white/60 outline-none focus:border-indigo-500/50 focus:bg-white/[0.06] transition-all"
                    />
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Search bar */}
      <div className="px-4 pb-6">
        <div className="max-w-[680px] mx-auto space-y-3">
          <div
            className="flex items-center gap-3 px-4 py-3.5 rounded-2xl border border-white/[0.08] bg-white/[0.03] focus-within:border-white/[0.15] focus-within:bg-white/[0.045] transition-all cursor-text"
            onClick={() => inputRef.current?.focus()}
          >
            <Search className="w-4 h-4 text-white/25 shrink-0" />
            <input
              ref={inputRef}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  navigate(query);
                }
              }}
              placeholder="Ask about Ghana's economy, budget, or election results..."
              className="flex-1 bg-transparent text-[14px] text-white/70 placeholder:text-white/22 outline-none"
            />
            <button
              onClick={() => navigate(query)}
              disabled={!query.trim()}
              className="w-7 h-7 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:bg-white/[0.07] disabled:cursor-not-allowed flex items-center justify-center transition-colors shrink-0"
            >
              <Send className="w-3.5 h-3.5 text-white" />
            </button>
          </div>

          {/* Meta info */}
          <div className="flex items-center justify-center gap-5 text-[10px] text-white/18 tracking-[0.15em] uppercase">
            <span className="flex items-center gap-1.5">
              <FileText className="w-3 h-3" />
              Source: Ghana 2025 Budget
            </span>
            <span className="w-px h-3 bg-white/10" />
            <span className="flex items-center gap-1.5">
              <Clock className="w-3 h-3" />
              Updated: Dec 2024
            </span>
          </div>
        </div>
      </div>

      <Footer />

      {/* Made with tag */}
      <div className="fixed bottom-3.5 left-4 pointer-events-none">
        <span className="text-[11px] text-white/15">Made with ♥</span>
      </div>
    </div>
  );
}
