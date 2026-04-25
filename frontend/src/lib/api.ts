const BACKEND_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000";

export interface RetrievedChunk {
  id?: string | number;
  text: string;
  source: string;
  score?: number;
  page?: number | string;
  type?: string;
  region?: string;
  constituency?: string;
  [key: string]: unknown;
}

export interface ChatResponse {
  query: string;
  answer: string;
  retrieved_chunks: RetrievedChunk[];
  final_prompt: string;
}

export async function sendChatMessage(query: string): Promise<ChatResponse> {
  const res = await fetch(`${BACKEND_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`API error ${res.status}: ${text}`);
  }

  return res.json() as Promise<ChatResponse>;
}
