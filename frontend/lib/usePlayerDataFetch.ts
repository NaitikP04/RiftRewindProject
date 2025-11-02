import type { DemoKey, PlayerData, MockDataSet } from "./types"
import mockData from "@/data/mock-player-data.json"

/**
 * Hook for fetching player data
 * Currently uses mock data, structured for easy API swap
 */

function normalizeInput(input: string): string {
  return input
    .toLowerCase()
    .trim()
    .replace(/\s+/g, "") // Remove all whitespace
    .replace(/#/g, "") // Remove # symbols
}

function matchDemoProfile(input: string, data: MockDataSet): PlayerData | null {
  const normalized = normalizeInput(input)

  console.log("[v0] Demo matching - normalized input:", normalized)

  // Direct demo key match (demo1, demo2, demo3)
  if (normalized === "demo1" || normalized === "demo2" || normalized === "demo3") {
    console.log("[v0] Matched demo key:", normalized)
    return data[normalized as DemoKey]
  }

  // Match against username+tag combinations
  for (const [key, profile] of Object.entries(data)) {
    const profileMatch = normalizeInput(`${profile.username}${profile.tag}`)
    const displayMatch = normalizeInput(profile.displayName)

    console.log("[v0] Checking profile:", key, "against:", profileMatch, displayMatch)

    if (normalized === profileMatch || normalized === displayMatch) {
      console.log("[v0] Matched profile:", key)
      return profile
    }

    // Fuzzy match on username prefix (at least 3 chars)
    if (normalized.length >= 3 && profileMatch.startsWith(normalized)) {
      console.log("[v0] Fuzzy matched profile:", key)
      return profile
    }
  }

  console.log("[v0] No match found for input:", input)
  return null
}

export async function fetchPlayerData(input: string): Promise<PlayerData | null> {
  // Simulate network delay
  await new Promise((resolve) => setTimeout(resolve, 2200))

  const data = mockData as MockDataSet

  return matchDemoProfile(input, data)
}
