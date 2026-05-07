import Link from "next/link";
import { notFound } from "next/navigation";
import { getGame } from "@/lib/games";
import type { Milestone } from "@/lib/types";

export default async function PlayPage({
  params,
  searchParams,
}: {
  params: Promise<{ slug: string }>;
  searchParams: Promise<{ v?: string }>;
}) {
  const { slug } = await params;
  const { v } = await searchParams;
  const game = getGame(slug);
  if (!game) notFound();

  const milestone: Milestone = (v as Milestone) ?? game.milestone;
  const gameUrl = `/games/${slug}/${milestone}/index.html`;

  return (
    <div className="w-screen h-screen bg-black flex flex-col">
      {/* Minimal toolbar */}
      <div className="flex items-center justify-between px-3 py-1.5 bg-bg-dark border-b border-[#444444] shrink-0">
        <Link
          href={`/games/${slug}`}
          className="flex items-center gap-2 text-primary hover:text-white transition-colors text-sm"
          style={{ fontFamily: "var(--font-display)" }}
        >
          <span>←</span>
          <span>RETURN</span>
        </Link>
        <span className="text-xs text-[#444444] uppercase tracking-widest" style={{ fontFamily: "var(--font-display)" }}>
          {game.title.replace(/\s+/g, "_").toUpperCase()} // {milestone.toUpperCase()}
        </span>
        <div className="h-2 w-2 bg-primary rounded-full animate-pulse" />
      </div>

      {/* Game iframe — fills remaining space */}
      <iframe
        src={gameUrl}
        className="flex-1 w-full border-0"
        title={game.title}
        allow="fullscreen"
        sandbox="allow-scripts allow-same-origin"
      />
    </div>
  );
}
