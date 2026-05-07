export type Milestone = "concept" | "alpha" | "beta" | "preview" | "release";

export interface FitnessScores {
  composite: number;
  fun: number;
  novelty: number;
  balance: number;
  difficulty: number;
  exploit_free: number;
  performance: number;
  ux_clarity: number;
}

export interface GameEntry {
  slug: string;
  title: string;
  description: string;
  genre: string;
  milestone: Milestone;
  milestones: Milestone[];
  fitness: FitnessScores;
  game_id: string;
  session_dir: string;
  screenshot: string | null;
  created_at: string;
  updated_at: string;
  tags?: string[];
}

export interface GamesManifest {
  games: GameEntry[];
  updated_at: string;
}
