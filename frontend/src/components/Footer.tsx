import Link from "next/link";
import { Monitor } from "lucide-react";

export function Footer() {
  return (
    <footer className="border-t border-white/[0.06] py-5 px-6 mt-auto">
      <div className="max-w-4xl mx-auto flex items-center justify-between">
        <p className="text-xs text-white/25">
          © 2026 AcaIntel AI. Built for Academic City University.
        </p>
        <div className="flex items-center gap-5">
          <Link
            href="#"
            className="text-xs text-white/25 hover:text-white/50 transition-colors"
          >
            Privacy Policy
          </Link>
          <Link
            href="#"
            className="text-xs text-white/25 hover:text-white/50 transition-colors"
          >
            Terms of Service
          </Link>
          <Monitor className="w-3.5 h-3.5 text-white/20" />
        </div>
      </div>
    </footer>
  );
}
