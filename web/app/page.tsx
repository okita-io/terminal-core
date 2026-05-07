import Link from "next/link";
import Image from "next/image";
import { getManifest, milestoneColor, milestoneGlow } from "@/lib/games";
import type { GameEntry, Milestone } from "@/lib/types";

function FitnessBar({ score }: { score: number }) {
  const filled = Math.round(score * 5);
  return (
    <div className="flex gap-0.5 h-2">
      {[0, 1, 2, 3, 4].map((i) => (
        <div
          key={i}
          className={`flex-1 transition-colors ${
            i < filled ? "bg-primary shadow-glow-cyan" : "bg-[#444444]/20"
          }`}
        />
      ))}
    </div>
  );
}

function MilestonePill({ milestone }: { milestone: Milestone }) {
  const color = milestoneColor(milestone);
  const glow = milestoneGlow(milestone);
  return (
    <span
      className={`px-1.5 py-0.5 border font-display text-[10px] font-bold uppercase tracking-wider ${color} ${glow}`}
      style={{ fontFamily: "var(--font-display)" }}
    >
      {milestone}
    </span>
  );
}

function GameCard({ game }: { game: GameEntry }) {
  const composite = game.fitness?.composite ?? 0;

  return (
    <Link href={`/games/${game.slug}`}>
      <article className="group relative w-full border border-[#444444] bg-surface-dark hover:border-primary transition-colors duration-300 cursor-pointer">
        {/* Thumbnail */}
        <div className="relative w-full aspect-video border-b border-[#444444] overflow-hidden bg-black">
          {game.screenshot ? (
            <Image
              src={game.screenshot}
              alt={game.title}
              fill
              className="object-cover opacity-80 group-hover:opacity-100 transition-opacity duration-300"
              sizes="(max-width: 768px) 100vw, 448px"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center">
              <span className="font-display text-[#444444] text-xs animate-pulse" style={{ fontFamily: "var(--font-display)" }}>
                NO_VISUAL_FEED
              </span>
            </div>
          )}
          <div className="absolute inset-0 scanlines opacity-50" />
          <div className="absolute top-2 right-2 flex gap-1">
            {game.milestones.map((m) => (
              <MilestonePill key={m} milestone={m} />
            ))}
          </div>
        </div>

        {/* Content */}
        <div className="p-3 space-y-3">
          <div className="flex justify-between items-baseline">
            <h2 className="font-bold text-lg text-white uppercase tracking-tight truncate pr-2 glitch-hover" style={{ fontFamily: "var(--font-display)" }}>
              {game.title.toUpperCase().replace(/\s+/g, "_")}
            </h2>
            <span className="text-xs text-[#444444] whitespace-nowrap" style={{ fontFamily: "var(--font-code)" }}>
              {game.genre?.replace(/_/g, " ")}
            </span>
          </div>

          {/* Fitness Bar */}
          <div className="space-y-1">
            <div className="flex justify-between text-[10px] uppercase text-[#444444]" style={{ fontFamily: "var(--font-micro)" }}>
              <span>FITNESS_COMPOSITE</span>
              <span className="text-primary">{(composite * 100).toFixed(0)}%</span>
            </div>
            <FitnessBar score={composite} />
          </div>

          {/* Stats grid */}
          <div className="grid grid-cols-4 gap-y-2 gap-x-1 pt-2 border-t border-dashed border-[#444444]/30">
            {[
              ["FUN", game.fitness?.fun],
              ["NOV", game.fitness?.novelty],
              ["BAL", game.fitness?.balance],
              ["UX", game.fitness?.ux_clarity],
            ].map(([label, val]) => (
              <div key={label as string} className="flex items-center gap-1 text-[#444444] hover:text-white transition-colors">
                <span className="text-xs" style={{ fontFamily: "var(--font-micro)" }}>{label as string}</span>
                <span className="text-xs text-primary" style={{ fontFamily: "var(--font-micro)" }}>
                  {(((val as number) ?? 0) * 10).toFixed(1)}
                </span>
              </div>
            ))}
          </div>
        </div>
      </article>
    </Link>
  );
}

export default function HomePage() {
  const manifest = getManifest();
  const games = manifest.games;

  return (
    <>
      {/* Header */}
      <header className="sticky top-0 z-50 bg-bg-dark/95 backdrop-blur-sm border-b border-[#444444]">
        <div className="flex items-center justify-between px-4 h-14">
          <h1 className="font-bold text-lg tracking-tight text-primary glitch-hover cursor-default select-none" style={{ fontFamily: "var(--font-display)" }}>
            TERMINAL_CORE{" "}
            <span className="text-xs text-[#444444]">v1.0</span>
          </h1>
          <div className="flex items-center gap-2">
            <div className="h-2 w-2 bg-primary rounded-full animate-pulse" />
            <span className="text-xs text-[#444444]" style={{ fontFamily: "var(--font-micro)" }}>
              {games.length}_PACKETS
            </span>
          </div>
        </div>
        {/* Marquee ticker */}
        <div className="w-full border-b border-[#444444] bg-surface-dark h-6 overflow-hidden flex items-center relative">
          <div
            className="whitespace-nowrap text-xs text-primary uppercase tracking-widest absolute"
            style={{ fontFamily: "var(--font-micro)", animation: "marquee 20s linear infinite" }}
          >
            {games.length > 0
              ? games.map((g) => `>> ${g.title.toUpperCase().replace(/\s+/g, "_")} [${g.milestone.toUpperCase()}] `).join("// ")
              : ">> TERMINAL_CORE SYSTEM OPTIMAL // AWAITING_PACKETS // AI_ENGINE: ACTIVE // VIBE_CHECK: PASSED //"}
          </div>
        </div>
      </header>

      {/* Main */}
      <main className="flex-1 w-full max-w-md mx-auto relative pb-20">
        {/* Filter bar */}
        <div className="sticky top-20 z-40 bg-bg-dark/80 backdrop-blur border-b border-[#444444] py-3 px-4 overflow-x-auto no-scrollbar flex gap-3 mb-4">
          <button className="shrink-0 px-3 py-1 bg-primary text-black font-bold border border-primary hover:shadow-glow-cyan uppercase text-sm" style={{ fontFamily: "var(--font-display)" }}>
            [ALL]
          </button>
          {["ALPHA", "BETA", "PREVIEW", "RELEASE"].map((m) => (
            <button
              key={m}
              className="shrink-0 px-3 py-1 bg-transparent text-[#444444] font-bold border border-[#444444] hover:border-primary hover:text-primary transition-colors uppercase text-sm"
              style={{ fontFamily: "var(--font-display)" }}
            >
              [{m}]
            </button>
          ))}
        </div>

        {/* Game list */}
        <div className="px-4 space-y-6">
          {games.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-20 gap-4">
              <div className="border border-[#444444]/30 p-8 text-center space-y-3">
                <p className="text-primary text-lg animate-pulse" style={{ fontFamily: "var(--font-display)" }}>
                  AWAITING_PACKETS_
                </p>
                <p className="text-xs text-[#444444]" style={{ fontFamily: "var(--font-micro)" }}>
                  NO GAMES GENERATED YET
                </p>
                <p className="text-xs text-[#444444]/60 mt-2" style={{ fontFamily: "var(--font-code)" }}>
                  $ python -m harness.main new
                </p>
              </div>
            </div>
          ) : (
            games.map((game) => <GameCard key={game.slug} game={game} />)
          )}
        </div>
      </main>

      {/* Bottom Nav */}
      <nav className="fixed bottom-0 w-full z-40 bg-bg-dark border-t border-[#444444]">
        <div className="flex gap-2 bg-surface-dark px-4 pb-3 pt-2 max-w-md mx-auto">
          <a className="flex flex-1 flex-col items-center justify-end gap-1 text-primary" href="/">
            <span className="text-xl">⌂</span>
          </a>
          <a className="flex flex-1 flex-col items-center justify-end gap-1 text-[#444444] hover:text-white transition-colors" href="#">
            <span className="text-xl">◈</span>
          </a>
          <a className="flex flex-1 flex-col items-center justify-end gap-1 text-[#444444] hover:text-white transition-colors" href="#">
            <span className="text-xl">⌘</span>
          </a>
        </div>
      </nav>
    </>
  );
}
