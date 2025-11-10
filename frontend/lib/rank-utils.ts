/**
 * Rank mapping and utilities for Season Performance Trends
 */

export const RANK_TO_NUMBER: Record<string, number> = {
  Iron: 1,
  Bronze: 2,
  Silver: 3,
  Gold: 4,
  Platinum: 5,
  Emerald: 6,
  Diamond: 7,
  Master: 8,
  Grandmaster: 9,
  Challenger: 10,
}

export const NUMBER_TO_RANK: Record<number, string> = {
  1: "Iron",
  2: "Bronze",
  3: "Silver",
  4: "Gold",
  5: "Platinum",
  6: "Emerald",
  7: "Diamond",
  8: "Master",
  9: "Grandmaster",
  10: "Challenger",
}

export function rankToNumber(rank: string): number {
  return RANK_TO_NUMBER[rank] || 0
}

export function numberToRank(num: number): string {
  return NUMBER_TO_RANK[num] || "Unranked"
}

export function formatMonth(monthStr: string): string {
  const date = new Date(monthStr + "-01")
  return date.toLocaleDateString("en-US", { month: "short" })
}

type RankTierKey =
  | "iron"
  | "bronze"
  | "silver"
  | "gold"
  | "platinum"
  | "emerald"
  | "diamond"
  | "master"
  | "grandmaster"
  | "challenger"
  | "unranked"

const RANK_STYLE_MAP: Record<RankTierKey, {
  label: string
  primary: string
  secondary: string
  border: string
  inner: string
  glyph: string
  glyphChar: string
}> = {
  iron: {
    label: "Iron",
    primary: "#9f9c95",
    secondary: "#4b4741",
    border: "#d0cbc3",
    inner: "#2d2b29",
    glyph: "#f5f3f1",
    glyphChar: "I",
  },
  bronze: {
    label: "Bronze",
    primary: "#d18c4b",
    secondary: "#7a3f1d",
    border: "#f4b57d",
    inner: "#30190c",
    glyph: "#ffe3c7",
    glyphChar: "B",
  },
  silver: {
    label: "Silver",
    primary: "#e3e9f1",
    secondary: "#8d9dac",
    border: "#f2f6ff",
    inner: "#3f4b57",
    glyph: "#ffffff",
    glyphChar: "S",
  },
  gold: {
    label: "Gold",
    primary: "#f7d66a",
    secondary: "#c28a1a",
    border: "#ffeab0",
    inner: "#4f3105",
    glyph: "#fff4da",
    glyphChar: "G",
  },
  platinum: {
    label: "Platinum",
    primary: "#6be2c4",
    secondary: "#0c7b62",
    border: "#9bf3dc",
    inner: "#053e32",
    glyph: "#e7fffb",
    glyphChar: "P",
  },
  emerald: {
    label: "Emerald",
    primary: "#4de070",
    secondary: "#0c6a3b",
    border: "#8bf3ac",
    inner: "#064124",
    glyph: "#eafff0",
    glyphChar: "E",
  },
  diamond: {
    label: "Diamond",
    primary: "#70c6ff",
    secondary: "#2657ff",
    border: "#a8e1ff",
    inner: "#102c6e",
    glyph: "#f4fbff",
    glyphChar: "D",
  },
  master: {
    label: "Master",
    primary: "#c476ff",
    secondary: "#5b0da6",
    border: "#e7b3ff",
    inner: "#2a074f",
    glyph: "#ffe9ff",
    glyphChar: "M",
  },
  grandmaster: {
    label: "Grandmaster",
    primary: "#ff6e8d",
    secondary: "#b40033",
    border: "#ffc1cf",
    inner: "#4f0015",
    glyph: "#fff5f7",
    glyphChar: "GM",
  },
  challenger: {
    label: "Challenger",
    primary: "#69f3ff",
    secondary: "#1688ff",
    border: "#aef7ff",
    inner: "#0b2c57",
    glyph: "#f2ffff",
    glyphChar: "C",
  },
  unranked: {
    label: "Unranked",
    primary: "#aaa",
    secondary: "#555",
    border: "#d4d4d4",
    inner: "#2c2c2c",
    glyph: "#f5f5f5",
    glyphChar: "?",
  },
}

const rankIconCache: Partial<Record<RankTierKey, string>> = {}

function createIconSvg(tier: RankTierKey): string {
  const style = RANK_STYLE_MAP[tier]
  const gradientId = `grad-${tier}`
  const glyph = style.glyphChar
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <defs>
    <linearGradient id="${gradientId}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="${style.primary}" />
      <stop offset="100%" stop-color="${style.secondary}" />
    </linearGradient>
  </defs>
  <polygon points="32 4 58 18 58 46 32 60 6 46 6 18" fill="url(#${gradientId})" stroke="${style.border}" stroke-width="3" stroke-linejoin="round" />
  <circle cx="32" cy="32" r="14" fill="${style.inner}" opacity="0.9" />
  <text x="32" y="38" font-family="'Segoe UI', 'Montserrat', sans-serif" font-size="18" font-weight="700" text-anchor="middle" fill="${style.glyph}">${glyph}</text>
</svg>`

  return `data:image/svg+xml;utf8,${encodeURIComponent(svg)}`
}

function normalizeRank(rank?: string): RankTierKey {
  if (!rank) {
    return "unranked"
  }

  const lowered = rank.toLowerCase()
  if (lowered.includes("challenger")) return "challenger"
  if (lowered.includes("grandmaster")) return "grandmaster"
  if (lowered.includes("master")) return "master"
  if (lowered.includes("diamond")) return "diamond"
  if (lowered.includes("emerald")) return "emerald"
  if (lowered.includes("platinum")) return "platinum"
  if (lowered.includes("gold")) return "gold"
  if (lowered.includes("silver")) return "silver"
  if (lowered.includes("bronze")) return "bronze"
  if (lowered.includes("iron")) return "iron"
  return "unranked"
}

export function getRankTierLabel(rank?: string): string {
  const tier = normalizeRank(rank)
  return RANK_STYLE_MAP[tier].label
}

export function getRankIconDataUri(rank?: string): string {
  const tier = normalizeRank(rank)
  if (!rankIconCache[tier]) {
    rankIconCache[tier] = createIconSvg(tier)
  }
  return rankIconCache[tier] as string
}
