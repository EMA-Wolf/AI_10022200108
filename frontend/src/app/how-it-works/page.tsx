import { GraduationCap, Search, Cpu, BookOpen, ArrowRight } from "lucide-react";
import Link from "next/link";

const STEPS = [
  {
    icon: Search,
    title: "Query Processing",
    desc: "Your question is parsed and embedded into a dense vector representation using the all-MiniLM-L6-v2 sentence transformer model.",
    color: "text-violet-400",
    bg: "bg-violet-500/10",
  },
  {
    icon: BookOpen,
    title: "Hybrid Retrieval",
    desc: "FAISS similarity search is combined with keyword boosting across the Ghana 2025 Budget and 2024 Election datasets to surface the most relevant passages.",
    color: "text-blue-400",
    bg: "bg-blue-500/10",
  },
  {
    icon: Cpu,
    title: "LLM Generation",
    desc: "The top retrieved context is injected into a structured prompt sent to Llama 3.1 8B (via Groq), which generates a grounded, citation-aware answer.",
    color: "text-emerald-400",
    bg: "bg-emerald-500/10",
  },
];

export default function HowItWorksPage() {
  return (
    <div className="min-h-screen pt-14">
      <div className="max-w-[680px] mx-auto px-4 py-16 space-y-12">
        {/* Header */}
        <div className="space-y-4">
          <div className="inline-flex items-center gap-2 text-[10px] font-semibold tracking-[0.2em] text-white/30 border border-white/[0.08] rounded-full px-4 py-1.5 uppercase">
            <GraduationCap className="w-3.5 h-3.5" />
            RAG Pipeline
          </div>
          <h1 className="text-3xl font-bold text-white tracking-tight">
            How AcaIntel AI Works
          </h1>
          <p className="text-[14px] text-white/45 leading-relaxed max-w-md">
            AcaIntel uses a Retrieval-Augmented Generation (RAG) pipeline to
            answer questions with evidence directly drawn from verified Ghanaian
            government datasets.
          </p>
        </div>

        {/* Steps */}
        <div className="space-y-3">
          {STEPS.map(({ icon: Icon, title, desc, color, bg }, i) => (
            <div
              key={title}
              className="flex gap-4 p-5 rounded-2xl border border-white/[0.07] bg-white/[0.025]"
            >
              <div className="flex flex-col items-center gap-2 shrink-0">
                <div className={`w-9 h-9 rounded-xl flex items-center justify-center ${bg}`}>
                  <Icon className={`w-4.5 h-4.5 ${color}`} />
                </div>
                {i < STEPS.length - 1 && (
                  <div className="w-px flex-1 bg-white/[0.06] min-h-[24px]" />
                )}
              </div>
              <div className="pt-1 space-y-1.5">
                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-semibold text-white/25 tracking-widest uppercase">
                    Step {i + 1}
                  </span>
                </div>
                <h3 className="text-[15px] font-semibold text-white/85">{title}</h3>
                <p className="text-[13px] text-white/45 leading-relaxed">{desc}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Datasets */}
        <div className="rounded-2xl border border-white/[0.07] bg-white/[0.025] p-5 space-y-3">
          <h3 className="text-[12px] font-bold tracking-[0.18em] text-white/30 uppercase">
            Data Sources
          </h3>
          <div className="grid grid-cols-2 gap-2.5">
            {[
              { label: "Ghana 2025 Budget Statement", tag: "PDF · ~300 pages" },
              { label: "2024 Ghana Election Results", tag: "CSV · All constituencies" },
            ].map(({ label, tag }) => (
              <div
                key={label}
                className="p-3.5 rounded-xl bg-white/[0.03] border border-white/[0.05] space-y-1"
              >
                <p className="text-[13px] text-white/70 font-medium">{label}</p>
                <p className="text-[11px] text-white/30">{tag}</p>
              </div>
            ))}
          </div>
        </div>

        {/* CTA */}
        <div className="flex justify-center">
          <Link
            href="/chat"
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-sm font-medium text-white transition-colors shadow-lg shadow-indigo-600/25"
          >
            Try it now
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </div>
    </div>
  );
}
