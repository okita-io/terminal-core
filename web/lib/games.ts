import fs from "fs";
import path from "path";
import type { GamesManifest, GameEntry, Milestone } from "./types";

const MANIFEST_PATH = path.join(process.cwd(), "public", "games", "index.json");

export function getManifest(): GamesManifest {
  try {
    const raw = fs.readFileSync(MANIFEST_PATH, "utf-8");
    return JSON.parse(raw) as GamesManifest;
  } catch {
    return { games: [], updated_at: new Date().toISOString() };
  }
}

export function getGame(slug: string): GameEntry | null {
  const manifest = getManifest();
  return manifest.games.find((g) => g.slug === slug) ?? null;
}

export function getGameUrl(slug: string, milestone: Milestone): string {
  return `/games/${slug}/${milestone}/index.html`;
}

export const MILESTONE_ORDER: Milestone[] = ["concept", "alpha", "beta", "preview", "release"];

export function milestoneLabel(m: Milestone): string {
  return m.toUpperCase();
}

export function milestoneColor(m: Milestone): string {
  const map: Record<Milestone, string> = {
    concept: "text-text-dim border-text-dim",
    alpha: "text-secondary border-secondary",
    beta: "text-primary border-primary",
    preview: "text-[#FFB800] border-[#FFB800]",
    release: "text-[#00FF88] border-[#00FF88]",
  };
  return map[m] ?? "text-text-dim border-text-dim";
}

export function milestoneGlow(m: Milestone): string {
  const map: Record<Milestone, string> = {
    concept: "",
    alpha: "shadow-glow-magenta",
    beta: "shadow-glow-cyan",
    preview: "[box-shadow:0_0_10px_rgba(255,184,0,0.4)]",
    release: "[box-shadow:0_0_10px_rgba(0,255,136,0.4)]",
  };
  return map[m] ?? "";
}

export function fitnessBar(score: number): string {
  // Returns filled segments count out of 5
  return Math.round(score * 5).toString();
}
