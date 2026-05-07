import Link from "next/link";
import Image from "next/image";
import { notFound } from "next/navigation";
import { getGame, getManifest, milestoneColor, milestoneGlow, MILESTONE_ORDER } from "@/lib/games";
import type { Milestone, FitnessScores } from "@/lib/types";

function MilestonePill({ milestone, active }: { milestone: Milestone; active?: boolean }) {
  const color = milestoneColor(milestone);
  const glow = milestoneGlow(milestone);
  return (
    <span
      className={`px-2 py-0.5 border text-[10px] font-bold uppercase tracking-wider ${color} ${glow} ${active ? "bg-primary/10" : ""}`}
      style={{ fontFamily: "var(--font-display)" }}
    >
      {milestone}
    </span>
  );
}

function FitnessHex({ scores }: { scores: FitnessScores }) {
  const axes = [
    { key: "fun", label: "FUN" },
    { key: "novelty", label: "NOV" },
    { key: "balance", label: "BAL" },
    { key: "difficulty", label: "DIFF" },
    { key: "exploit_free", label: "SAFE" },
    { key: "ux_clarity", label: "UX" },
  ];
  const cx = 50, cy = 50, r = 40;
  const n = axes.length;

  function axisPoint(i: number, scale: number) {
    const angle = (Math.PI * 2 * i) / n - Math.PI / 2;
    return {
      x: cx + r * scale * Math.cos(angle),
      y: cy + r * scale * Math.sin(angle),
    };
  }

  const dataPoints = axes.map((a, i) => {
    const val = (scores as unknown as Record<string, number>)[a.key] ?? 0;
    return axisPoint(i, val);
  });

  const dataPath = dataPoints.map((p, i) => `${i === 0 ? "M" : "L"} ${p.x} ${p.y}`).join(" ") + " Z";

  const gridScales = [0.25, 0.5, 0.75, 1.0];
  const labelPoints = axes.map((a, i) => {
    const p = axisPoint(i, 1.25);
    return { ...p, label: a.label };
  });

  return (
    <div className="relative w-32 h-32 flex items-center justify-center">
      <svg viewBox="0 0 100 100" className="w-full h-full" style={{ filter: "drop-shadow(0 0 10px rgba(0,240,255,0.5))" }}>
        {gridScales.map((s) => {
          const pts = axes.map((_, i) => axisPoint(i, s));
          return (
            <polygon
              key={s}
              points={pts.map((p) => `${p.x},${p.y}`).join(" ")}
              fill="none"
              stroke="#444444"
              strokeWidth="0.5"
            />
          );
        })}
        {axes.map((_, i) => {
          const outer = axisPoint(i, 1.0);
          return <line key={i} x1={cx} y1={cy} x2={outer.x} y2={outer.y} stroke="#444444" strokeWidth="0.5" />;
        })}
        <polygon
          points={dataPoints.map((p) => `${p.x},${p.y}`).join(" ")}
          fill="rgba(0,240,255,0.15)"
          stroke="#00F0FF"
          strokeWidth="1.5"
        />
        {labelPoints.map((lp) => (
          <text
            key={lp.label}
            x={lp.x}
            y={lp.y}
            textAnchor="middle"
            dominantBaseline="middle"
            fontSize="5"
            fill="#00F0FF"
            fontFamily="monospace"
          >
            {lp.label}
          </text>
        ))}
      </svg>
    </div>
  );
}

export async function generateStaticParams() {
  const manifest = getManifest();
  return manifest.games.map((g) => ({ slug: g.slug }));
}

export default async function GameDetailPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const game = getGame(slug);
  if (!game) notFound();

  const latestMilestone = game.milestone;
  const playUrl = `/games/${slug}/${latestMilestone}/index.html`;
  const composite = game.fitness?.composite ?? 0;

  return (
    <div className="crt-on min-h-screen flex flex-col">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-bg-dark/95 backdrop-blur-sm border-b border-[#444444]/50">
        <div className="flex items-center justify-between p-3">
          <Link
            href="/"
            className="flex items-center gap-2 text-primary hover:text-white transition-colors"
          >
            <span className="text-xl">←</span>
            <span className="text-sm font-bold tracking-tighter" style={{ fontFamily: "var(--font-display)" }}>
              RETURN_TO_ROOT
            </span>
          </Link>
          <div className="flex items-center gap-2">
            <div className="h-2 w-2 bg-primary rounded-full animate-pulse" />
            <h1 className="text-sm text-white tracking-tight uppercase" style={{ fontFamily: "var(--font-display)" }}>
              DIAGNOSTIC_VIEW // {game.title.toUpperCase().replace(/\s+/g, "_")}
            </h1>
          </div>
          <div className="w-8" />
        </div>
        <div className="w-full bg-surface-dark border-b border-[#444444]/30 overflow-hidden whitespace-nowrap py-0.5">
          <p className="text-xs text-primary/70 animate-pulse" style={{ fontFamily: "var(--font-micro)" }}>
            {">>"} SYSTEM CHECK: OPTIMAL {">>"} FITNESS: {(composite * 100).toFixed(0)}% {">>"} MILESTONE: {latestMilestone.toUpperCase()} {">>"} GENRE: {game.genre?.toUpperCase().replace(/_/g, "_")} {">>"}
          </p>
        </div>
      </header>

      <main className="flex-grow flex flex-col relative w-full max-w-2xl mx-auto border-x border-[#444444]/20 bg-bg-dark">
        {/* Hero */}
        <section className="relative h-[40vh] w-full bg-surface-dark overflow-hidden group">
          {game.screenshot ? (
            <Image
              src={game.screenshot}
              alt={game.title}
              fill
              className="object-cover opacity-80 group-hover:scale-105 transition-transform duration-700"
              sizes="672px"
            />
          ) : (
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-[#444444] text-xs" style={{ fontFamily: "var(--font-display)" }}>
                NO_VISUAL_FEED
              </span>
            </div>
          )}
          <div className="absolute inset-0 scanlines opacity-40 pointer-events-none" />
          <div className="absolute inset-0 bg-gradient-to-t from-bg-dark via-transparent to-transparent" />

          {/* Fitness hex */}
          {game.fitness && (
            <div className="absolute bottom-4 right-4 z-10 hidden sm:block">
              <FitnessHex scores={game.fitness} />
            </div>
          )}

          {/* Mobile stats */}
          <div className="absolute bottom-4 right-4 z-10 sm:hidden flex flex-col items-end gap-1 bg-black/80 p-2 border border-[#444444] backdrop-blur-sm">
            <div className="flex items-center gap-2">
              <span className="text-xs text-[#444444]" style={{ fontFamily: "var(--font-micro)" }}>FITNESS:</span>
              <span className="text-sm text-primary font-bold" style={{ fontFamily: "var(--font-display)" }}>
                {(composite * 100).toFixed(0)}%
              </span>
            </div>
          </div>

          {/* Title overlay */}
          <div className="absolute bottom-4 left-4 z-10">
            <div className="inline-flex items-center gap-2 mb-1">
              <MilestonePill milestone={latestMilestone} />
              <span className="text-xs text-white/80" style={{ fontFamily: "var(--font-micro)" }}>
                gen.{game.fitness ? (composite * 100).toFixed(0) : "00"}
              </span>
            </div>
            <h2 className="text-3xl md:text-4xl font-bold text-white tracking-tighter drop-shadow-lg glitch-hover cursor-default" style={{ fontFamily: "var(--font-display)" }}>
              {game.title.toUpperCase().replace(/\s+/g, "_")}
            </h2>
          </div>
        </section>

        {/* Execute button */}
        <section className="p-4 border-b border-[#444444]/30 bg-bg-dark z-20">
          <Link
            href={`/games/${slug}/play`}
            className="group relative w-full overflow-hidden border border-primary bg-transparent hover:bg-primary/10 transition-all duration-100 py-4 px-6 flex items-center justify-between block"
          >
            <div className="absolute inset-0 bg-primary/5 opacity-0 group-hover:opacity-100 transition-opacity" />
            <div className="flex items-center gap-3 relative z-10">
              <span className="text-primary text-3xl animate-pulse">▶</span>
              <div className="flex flex-col items-start">
                <span className="font-bold text-xl text-white tracking-tight group-hover:translate-x-1 transition-transform" style={{ fontFamily: "var(--font-display)" }}>
                  &gt; EXECUTE_GAME.EXE
                </span>
                <span className="text-xs text-primary/70" style={{ fontFamily: "var(--font-micro)" }}>
                  MILESTONE: {latestMilestone.toUpperCase()} // PATH: {playUrl}
                </span>
              </div>
            </div>
            <span className="relative z-10 text-2xl text-primary group-hover:text-white transition-colors" style={{ fontFamily: "var(--font-display)" }}>
              [ENTER]
            </span>
            {/* Corner accents */}
            <div className="absolute top-0 left-0 w-2 h-2 border-t border-l border-primary" />
            <div className="absolute bottom-0 right-0 w-2 h-2 border-b border-r border-primary" />
          </Link>
        </section>

        {/* Milestone history */}
        {game.milestones.length > 1 && (
          <section className="px-4 py-3 border-b border-[#444444]/30 flex gap-2 items-center">
            <span className="text-[10px] text-[#444444] mr-1" style={{ fontFamily: "var(--font-micro)" }}>VERSIONS:</span>
            {game.milestones.map((m) => (
              <Link key={m} href={`/games/${slug}/play?v=${m}`}>
                <MilestonePill milestone={m} active={m === latestMilestone} />
              </Link>
            ))}
          </section>
        )}

        {/* Tabs */}
        <section className="flex border-b border-[#444444]/30 sticky top-[98px] bg-bg-dark z-30">
          <div className="flex-1 py-3 px-2 border-r border-[#444444]/30 text-center font-bold bg-primary text-black text-xs md:text-sm" style={{ fontFamily: "var(--font-display)" }}>
            [01]_DIAGNOSTICS
          </div>
          <div className="flex-1 py-3 px-2 border-r border-[#444444]/30 text-center font-bold text-[#444444] hover:text-white hover:bg-surface-dark transition-colors text-xs md:text-sm" style={{ fontFamily: "var(--font-display)" }}>
            [02]_FITNESS
          </div>
          <div className="flex-1 py-3 px-2 text-center font-bold text-[#444444] hover:text-white hover:bg-surface-dark transition-colors text-xs md:text-sm" style={{ fontFamily: "var(--font-display)" }}>
            [03]_EVOLUTION
          </div>
        </section>

        {/* Diagnostics content */}
        <section className="p-4 md:p-6 space-y-8 pb-20">
          {/* Description */}
          <div className="border-l-2 border-primary pl-4 py-1">
            <h3 className="text-xs text-primary mb-2 opacity-70" style={{ fontFamily: "var(--font-display)" }}>
              &gt;&gt; FILE_DESCRIPTION
            </h3>
            <p className="text-sm md:text-base text-gray-300 leading-relaxed typing-cursor" style={{ fontFamily: "var(--font-body)" }}>
              {game.description || "No description recorded."}
            </p>
          </div>

          {/* Specs grid */}
          <div>
            <h3 className="text-xs text-primary mb-3 opacity-70" style={{ fontFamily: "var(--font-display)" }}>
              &gt;&gt; SYSTEM_DIAGNOSTICS
            </h3>
            <div className="grid grid-cols-2 gap-px bg-[#444444]/30 border border-[#444444]/30">
              {[
                ["GENRE", game.genre?.toUpperCase().replace(/_/g, " ") ?? "—"],
                ["MILESTONE", latestMilestone.toUpperCase()],
                ["FITNESS", `${(composite * 100).toFixed(1)}%`],
                ["GAME_ID", game.game_id.slice(0, 8).toUpperCase()],
                ["CREATED", new Date(game.created_at).toLocaleDateString()],
                ["UPDATED", new Date(game.updated_at).toLocaleDateString()],
              ].map(([label, value]) => (
                <div key={label} className="bg-surface-dark p-3 flex flex-col gap-1">
                  <span className="text-[10px] text-[#444444] uppercase" style={{ fontFamily: "var(--font-micro)" }}>
                    {label}
                  </span>
                  <span className="text-sm text-white" style={{ fontFamily: "var(--font-display)" }}>
                    {value}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Tags */}
          {game.tags && game.tags.length > 0 && (
            <div>
              <h3 className="text-xs text-primary mb-3 opacity-70" style={{ fontFamily: "var(--font-display)" }}>
                &gt;&gt; TAGS
              </h3>
              <div className="flex flex-wrap gap-2">
                {game.tags.map((tag) => (
                  <span
                    key={tag}
                    className="border border-[#444444] px-2 py-1 text-xs text-gray-400 hover:border-primary hover:text-primary transition-colors cursor-pointer"
                    style={{ fontFamily: "var(--font-code)" }}
                  >
                    #{tag.toUpperCase()}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Fitness scores */}
          {game.fitness && (
            <div>
              <h3 className="text-xs text-primary mb-3 opacity-70" style={{ fontFamily: "var(--font-display)" }}>
                &gt;&gt; FITNESS_BREAKDOWN
              </h3>
              <div className="space-y-2">
                {[
                  ["FUN", game.fitness.fun, "w-[30%]"],
                  ["NOVELTY", game.fitness.novelty, "w-[20%]"],
                  ["BALANCE", game.fitness.balance, "w-[15%]"],
                  ["DIFFICULTY", game.fitness.difficulty, "w-[15%]"],
                  ["EXPLOIT_FREE", game.fitness.exploit_free, "w-[10%]"],
                  ["PERFORMANCE", game.fitness.performance, "w-[5%]"],
                  ["UX_CLARITY", game.fitness.ux_clarity, "w-[5%]"],
                ].map(([label, score]) => (
                  <div key={label as string} className="flex items-center gap-3">
                    <span className="text-[10px] text-[#444444] w-24 shrink-0" style={{ fontFamily: "var(--font-micro)" }}>
                      {label as string}
                    </span>
                    <div className="flex-1 bg-[#444444]/20 h-1.5">
                      <div
                        className="h-full bg-primary transition-all"
                        style={{ width: `${((score as number) ?? 0) * 100}%` }}
                      />
                    </div>
                    <span className="text-[10px] text-primary w-8 text-right" style={{ fontFamily: "var(--font-code)" }}>
                      {(((score as number) ?? 0) * 100).toFixed(0)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
