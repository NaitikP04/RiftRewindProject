import type { PlayerData } from "./types"
import { fetchProfile, fetchAnalysis } from "./api-client"

/**
 * Fetch complete player data from backend API
 * Two-phase approach:
 * 1. Fast profile fetch (<5s) - shows profile immediately
 * 2. Deep analysis (3-6min) - generates full AI insights
 */

export async function fetchPlayerData(riotId: string): Promise<PlayerData | null> {
  try {
    console.log(`[Fetch] Starting data fetch for ${riotId}`)
    
    // Phase 1: Get profile quickly
    const profileResult = await fetchProfile(riotId)
    
    if (!profileResult.success || !profileResult.profile) {
      console.error('[Fetch] Profile fetch failed:', profileResult.error)
      return null
    }
    
    const profile = profileResult.profile
    console.log('[Fetch] Profile received, starting analysis...')
    
    // Phase 2: Generate full analysis
    const analysisResult = await fetchAnalysis(riotId, 100)
    
    if (!analysisResult.success || !analysisResult.data) {
      console.error('[Fetch] Analysis failed:', analysisResult.error)
      return null
    }
    
    const analysis = analysisResult.data
    console.log('[Fetch] Analysis complete!')
    
    // Combine into PlayerData format
    const playerData: PlayerData = {
      username: riotId.split('#')[0],
      tag: riotId.split('#')[1],
      displayName: analysis.displayName,
      profilePicture: analysis.profilePicture,
      mainRole: analysis.mainRole,
      topChampions: analysis.topChampions,
      highlights: analysis.highlights,
      aiInsight: analysis.aiInsight,
      personality: analysis.personality,
      // Progress data (mock for now until we implement growth charts)
      progress: {
        season: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        kda: [2.8, 2.9, 3.0, 3.2, 3.1, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9],
        winRate: [48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59]
      },
      seasonMonths: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
      rankTimeline: [
        analysis.rank, analysis.rank, analysis.rank, analysis.rank,
        analysis.rank, analysis.rank, analysis.rank, analysis.rank,
        analysis.rank, analysis.rank, analysis.rank, analysis.rank
      ],
      rankEvents: {}
    }
    
    return playerData
    
  } catch (error) {
    console.error('[Fetch] Unexpected error:', error)
    return null
  }
}
