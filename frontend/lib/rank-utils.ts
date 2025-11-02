/**
 * Rank mapping and utilities for Season Performance Trends
 */

export const RANK_TO_NUMBER: Record<string, number> = {
  Iron: 1,
  Bronze: 2,
  Silver: 3,
  Gold: 4,
  Platinum: 5,
  Diamond: 6,
  Master: 7,
  Grandmaster: 8,
  Challenger: 9,
}

export const NUMBER_TO_RANK: Record<number, string> = {
  1: "Iron",
  2: "Bronze",
  3: "Silver",
  4: "Gold",
  5: "Platinum",
  6: "Diamond",
  7: "Master",
  8: "Grandmaster",
  9: "Challenger",
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
