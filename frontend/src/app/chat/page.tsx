"use client";

import { useState, useEffect, useRef, useCallback, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import {
  GraduationCap,
  Sparkles,
  BookOpen,
  ChevronDown,
  Code2,
  Send,
  Activity,
  Database,
  TrendingUp,
  AlertCircle,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { sendChatMessage, type RetrievedChunk } from "@/lib/api";
import ReactMarkdown from "react-markdown";

/* ─────────────── Types ─────────────── */

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: RetrievedChunk[];
  finalPrompt?: string;
  isLoading?: boolean;
  isError?: boolean;
}

const TOPIC_CHIPS = [
  "2025 Budget Theme",
  "Inflation targets",
  "Election results",
  "GDP growth",
];

/* ─────────────── Sub-components ─────────────── */

function SourceChip({ chunk, index }: { chunk: RetrievedChunk; index: number }) {
  const display =
    chunk.id !== undefined
      ? String(chunk.id)
      : chunk.page !== undefined
      ? `p.${chunk.page}`
      : String(index + 1);

  return (
    <span
      title={`${chunk.source}${chunk.score !== undefined ? ` · score ${(chunk.score * 100).toFixed(0)}%` : ""}`}
      className="inline-flex items-center justify-center min-w-[32px] h-7 px-2.5 rounded-md bg-indigo-500/[0.12] border border-indigo-500/20 text-[11px] text-indigo-300/80 font-mono hover:bg-indigo-500/20 transition-colors cursor-default"
    >
      {display}
    </span>
  );
}

function CollapsibleRow({
  icon,
  label,
  children,
}: {
  icon: React.ReactNode;
  label: string;
  children: React.ReactNode;
}) {
  const [open, setOpen] = useState(false);
  return (
    <div>
      <button
        onClick={() => setOpen((v) => !v)}
        className="w-full flex items-center justify-between py-2.5 border-t border-white/[0.05] text-left hover:bg-white/[0.02] -mx-5 px-5 transition-colors"
      >
        <div className="flex items-center gap-2 text-[11px] text-white/35 tracking-wider">
          {icon}
          <span>{label}</span>
        </div>
        <ChevronDown
          className={cn(
            "w-3.5 h-3.5 text-white/25 transition-transform duration-200",
            open && "rotate-180"
          )}
        />
      </button>
      {open && <div className="pb-3">{children}</div>}
    </div>
  );
}

function AIMessage({ message }: { message: Message }) {
  return (
    <div className="w-full">
      <div className="rounded-2xl border border-white/[0.08] bg-[#0d0f14] overflow-hidden shadow-xl shadow-black/30">
        {/* Header */}
        <div className="flex items-center gap-2 px-5 pt-4 pb-3.5">
          <div className="w-6 h-6 rounded-md bg-indigo-500/15 flex items-center justify-center">
            <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
          </div>
          <span className="text-[11px] font-bold tracking-[0.18em] text-indigo-400">
            ACAINTEL AI
          </span>
        </div>

        <div className="px-5 pb-5">
          {/* Loading dots */}
          {message.isLoading && (
            <div className="flex items-center gap-2 py-2">
              <div className="flex gap-1">
                {[0, 150, 300].map((delay) => (
                  <div
                    key={delay}
                    className="w-1.5 h-1.5 rounded-full bg-indigo-400/50 animate-bounce"
                    style={{ animationDelay: `${delay}ms` }}
                  />
                ))}
              </div>
              <span className="text-[13px] text-white/30">
                Searching through documents...
              </span>
            </div>
          )}

          {/* Error */}
          {message.isError && (
            <div className="flex items-start gap-2.5 py-2 text-red-400/80">
              <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
              <p className="text-sm leading-relaxed">{message.content}</p>
            </div>
          )}

          {/* Answer */}
          {!message.isLoading && !message.isError && (
            <>
              <div className="prose-sm text-[14px] text-white/75 leading-[1.75]
                [&_p]:mb-3 [&_p:last-child]:mb-0
                [&_strong]:font-semibold [&_strong]:text-white/90
                [&_ul]:my-2 [&_ul]:space-y-1 [&_ul]:list-disc [&_ul]:list-inside
                [&_ol]:my-2 [&_ol]:space-y-1 [&_ol]:list-decimal [&_ol]:list-inside
                [&_li]:text-white/65
                [&_h1]:text-white [&_h1]:font-semibold [&_h1]:text-base [&_h1]:mb-2
                [&_h2]:text-white [&_h2]:font-semibold [&_h2]:text-[13px] [&_h2]:mb-2
                [&_code]:text-indigo-300 [&_code]:bg-indigo-500/10 [&_code]:px-1 [&_code]:rounded
                [&_blockquote]:border-l-2 [&_blockquote]:border-indigo-500/40 [&_blockquote]:pl-3 [&_blockquote]:text-white/50">
                <ReactMarkdown>{message.content}</ReactMarkdown>
              </div>

              {/* Verified sources */}
              {message.sources && message.sources.length > 0 && (
                <div className="mt-4 pt-4 border-t border-white/[0.05] space-y-2.5">
                  <div className="flex items-center gap-2 text-[10px] font-semibold tracking-[0.15em] text-white/28 uppercase">
                    <BookOpen className="w-3.5 h-3.5" />
                    Verified Sources
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {message.sources.map((chunk, i) => (
                      <SourceChip key={i} chunk={chunk} index={i} />
                    ))}
                  </div>
                </div>
              )}

              {/* Collapsibles */}
              <div className="mt-1">
                {message.sources && message.sources.length > 0 && (
                  <CollapsibleRow
                    icon={<BookOpen className="w-3.5 h-3.5" />}
                    label="SHOW RETRIEVED CONTEXT"
                  >
                    <div className="space-y-2 max-h-72 overflow-y-auto pr-1 mt-2">
                      {message.sources.map((chunk, i) => (
                        <div
                          key={i}
                          className="p-3.5 rounded-xl bg-white/[0.03] border border-white/[0.05]"
                        >
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-[10px] font-semibold text-white/30 uppercase tracking-wider">
                              {chunk.source}
                              {chunk.page && ` · Page ${chunk.page}`}
                              {chunk.region && ` · ${chunk.region}`}
                            </span>
                            {chunk.score !== undefined && (
                              <span className="text-[10px] text-indigo-400/50 font-mono">
                                {(chunk.score * 100).toFixed(1)}% match
                              </span>
                            )}
                          </div>
                          <p className="text-[12px] text-white/45 leading-relaxed line-clamp-5">
                            {chunk.text}
                          </p>
                        </div>
                      ))}
                    </div>
                  </CollapsibleRow>
                )}

                {message.finalPrompt && (
                  <CollapsibleRow
                    icon={<Code2 className="w-3.5 h-3.5" />}
                    label="/ SHOW TECHNICAL DETAILS"
                  >
                    <div className="mt-2 p-3.5 rounded-xl bg-white/[0.03] border border-white/[0.05] max-h-52 overflow-y-auto">
                      <pre className="text-[11px] text-white/35 whitespace-pre-wrap font-mono leading-relaxed">
                        {message.finalPrompt}
                      </pre>
                    </div>
                  </CollapsibleRow>
                )}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

function UserMessage({ content }: { content: string }) {
  return (
    <div className="w-full">
      <div className="rounded-2xl border border-white/[0.07] bg-white/[0.03] px-5 py-4">
        <div className="text-[10px] font-semibold tracking-[0.18em] text-white/25 mb-2.5 uppercase">
          Academic User
        </div>
        <p className="text-[14px] text-white/75 leading-relaxed">{content}</p>
      </div>
    </div>
  );
}

/* ─────────────── Main chat logic ─────────────── */

function ChatContent() {
  const searchParams = useSearchParams();
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isBusy, setIsBusy] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const initializedRef = useRef(false);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  const sendMessage = useCallback(
    async (query: string) => {
      const trimmed = query.trim();
      if (!trimmed || isBusy) return;

      const userId = crypto.randomUUID();
      const loadingId = crypto.randomUUID();

      setMessages((prev) => [
        ...prev,
        { id: userId, role: "user", content: trimmed },
        { id: loadingId, role: "assistant", content: "", isLoading: true },
      ]);
      setIsBusy(true);
      setInputValue("");

      // Reset textarea height
      if (textareaRef.current) {
        textareaRef.current.style.height = "auto";
      }

      try {
        const res = await sendChatMessage(trimmed);
        setMessages((prev) =>
          prev.map((m) =>
            m.id === loadingId
              ? {
                  ...m,
                  content: res.answer,
                  sources: res.retrieved_chunks,
                  finalPrompt: res.final_prompt,
                  isLoading: false,
                }
              : m
          )
        );
      } catch {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === loadingId
              ? {
                  ...m,
                  content:
                    "Unable to reach the backend. Please make sure the server is running on port 8000 and try again.",
                  isLoading: false,
                  isError: true,
                }
              : m
          )
        );
      } finally {
        setIsBusy(false);
      }
    },
    [isBusy]
  );

  // Initial query from URL param
  useEffect(() => {
    if (initializedRef.current) return;
    const q = searchParams.get("q");
    if (q) {
      initializedRef.current = true;
      sendMessage(q);
      window.history.replaceState(null, "", "/chat");
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Scroll on new messages
  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // Auto-resize textarea
  const handleTextareaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputValue(e.target.value);
    const ta = e.target;
    ta.style.height = "auto";
    ta.style.height = Math.min(ta.scrollHeight, 200) + "px";
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage(inputValue);
    }
  };

  return (
    <div className="h-screen pt-14 flex flex-col">
      {/* Messages area */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-[680px] mx-auto px-4 py-10 space-y-5">

          {/* Welcome header */}
          <div className="flex flex-col items-center text-center gap-4 pb-6">
            <div className="w-[52px] h-[52px] rounded-2xl bg-indigo-500/[0.12] border border-indigo-500/20 flex items-center justify-center shadow-lg shadow-indigo-500/10">
              <GraduationCap className="w-6 h-6 text-indigo-400" />
            </div>
            <div className="space-y-2">
              <h2 className="text-[18px] font-semibold text-white/90 tracking-tight">
                Academic Assistant Active
              </h2>
              <p className="text-[13px] text-white/38 max-w-[340px] mx-auto leading-relaxed">
                Ask specific questions about the 2025 Budget Statement or
                election datasets. I will provide sourced evidence for every
                claim.
              </p>
            </div>
            <div className="flex flex-wrap gap-2 justify-center pt-1">
              {TOPIC_CHIPS.map((chip) => (
                <button
                  key={chip}
                  onClick={() => sendMessage(chip)}
                  disabled={isBusy}
                  className="px-3.5 py-1.5 rounded-full border border-white/[0.07] bg-white/[0.03] hover:bg-white/[0.06] hover:border-white/[0.13] text-[12px] text-white/42 hover:text-white/75 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
                >
                  {chip}
                </button>
              ))}
            </div>
          </div>

          {/* Conversation */}
          {messages.map((msg) =>
            msg.role === "user" ? (
              <UserMessage key={msg.id} content={msg.content} />
            ) : (
              <AIMessage key={msg.id} message={msg} />
            )
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input area */}
      <div className="shrink-0 border-t border-white/[0.06] bg-[#09090b] px-4 pt-4 pb-3">
        <div className="max-w-[680px] mx-auto space-y-2.5">
          {/* Textarea container */}
          <div className="rounded-2xl border border-white/[0.08] bg-white/[0.025] focus-within:border-white/[0.14] focus-within:bg-white/[0.04] transition-all overflow-hidden">
            <textarea
              ref={textareaRef}
              value={inputValue}
              onChange={handleTextareaChange}
              onKeyDown={handleKeyDown}
              placeholder="Ask about Ghana's economy, budget, or election results..."
              disabled={isBusy}
              rows={3}
              className="w-full px-5 pt-4 pb-2 bg-transparent text-[14px] text-white/78 placeholder:text-white/20 outline-none resize-none disabled:opacity-40 disabled:cursor-not-allowed leading-relaxed"
            />
            <div className="flex items-center justify-between px-5 pb-3.5">
              <span className="text-[11px] text-white/18">
                Shift + Enter for new line
              </span>
              <button
                onClick={() => sendMessage(inputValue)}
                disabled={!inputValue.trim() || isBusy}
                className="flex items-center gap-2 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:bg-white/[0.08] disabled:text-white/30 disabled:cursor-not-allowed text-[13px] font-medium text-white transition-all shadow-lg shadow-indigo-600/20 disabled:shadow-none"
              >
                Send Query
                <Send className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          {/* Status bar */}
          <div className="flex items-center justify-center gap-6 pb-1">
            <button className="flex items-center gap-1.5 text-[10px] text-white/20 hover:text-white/45 tracking-[0.15em] uppercase transition-colors">
              <TrendingUp className="w-3 h-3" />
              How RAG Works
            </button>
            <div className="flex items-center gap-1.5 text-[10px] tracking-[0.15em] uppercase">
              <Activity className="w-3 h-3 text-emerald-500/60" />
              <span className="text-emerald-500/50">API Status:</span>
              <span className="text-emerald-500/80">Online</span>
            </div>
            <div className="flex items-center gap-1.5 text-[10px] text-white/20 tracking-[0.15em] uppercase">
              <Database className="w-3 h-3" />
              Datasets: GH-2025-Budget
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function ChatPage() {
  return (
    <Suspense fallback={
      <div className="h-screen pt-14 flex items-center justify-center">
        <div className="flex gap-1">
          {[0, 150, 300].map((d) => (
            <div
              key={d}
              className="w-2 h-2 rounded-full bg-indigo-400/40 animate-bounce"
              style={{ animationDelay: `${d}ms` }}
            />
          ))}
        </div>
      </div>
    }>
      <ChatContent />
    </Suspense>
  );
}
