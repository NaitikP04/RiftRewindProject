/**
 * API client for Rift Rewind backend
 * Handles communication with FastAPI endpoints
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface ProfileResponse {
  success: boolean
  profile?: {
    puuid: string
    display_name: string
    profile_icon_url: string
    summoner_level: number
    rank: {
      tier: string
      division: string
      lp: number
      wins: number
      losses: number
      win_rate: number
      display: string
    }
    main_role: string
  }
  error?: string
}

export interface AnalysisResponse {
  success: boolean
  data?: {
    displayName: string
    profilePicture: string
    mainRole: string
    topChampions: Array<{
      name: string
      games: number
      winRate: number
    }>
    highlights: Array<{
      stat: string
      value: string
    }>
    aiInsight: string
    personality: string
    rank: string
    matchesAnalyzed: number
  }
  error?: string
}

/**
 * Parse Riot ID into game name and tag line
 */
function parseRiotId(riotId: string): { gameName: string; tagLine: string } {
  const parts = riotId.split('#')
  if (parts.length !== 2) {
    throw new Error('Invalid Riot ID format. Use: GameName#TAG')
  }
  return {
    gameName: parts[0].trim(),
    tagLine: parts[1].trim()
  }
}

/**
 * Fetch player profile (fast, <5 seconds)
 * Gets summoner info, rank, and main role
 */
export async function fetchProfile(riotId: string): Promise<ProfileResponse> {
  try {
    const { gameName, tagLine } = parseRiotId(riotId)
    
    console.log(`[API] Fetching profile for ${gameName}#${tagLine}`)
    
    const response = await fetch(
      `${API_BASE_URL}/api/profile/${encodeURIComponent(gameName)}/${encodeURIComponent(tagLine)}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    )
    
    if (!response.ok) {
      const error = await response.json()
      return {
        success: false,
        error: error.detail || 'Failed to fetch profile'
      }
    }
    
    const data = await response.json()
    console.log('[API] Profile fetched successfully')
    return data
    
  } catch (error) {
    console.error('[API] Profile fetch error:', error)
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Network error'
    }
  }
}

/**
 * Generate AI analysis (slow, 3-6 minutes)
 * Gets top champions, highlights, AI insights, and personality
 */
export async function fetchAnalysis(
  riotId: string,
  numMatches: number = 100
): Promise<AnalysisResponse> {
  try {
    const { gameName, tagLine } = parseRiotId(riotId)
    
    console.log(`[API] Generating analysis for ${gameName}#${tagLine} (${numMatches} matches)`)
    
    const response = await fetch(
      `${API_BASE_URL}/api/analysis/${encodeURIComponent(gameName)}/${encodeURIComponent(tagLine)}?num_matches=${numMatches}`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    )
    
    if (!response.ok) {
      const error = await response.json()
      return {
        success: false,
        error: error.detail || 'Failed to generate analysis'
      }
    }
    
    const data = await response.json()
    console.log('[API] Analysis generated successfully')
    return data
    
  } catch (error) {
    console.error('[API] Analysis error:', error)
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Network error'
    }
  }
}

/**
 * Check backend health
 */
export async function checkHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/health`)
    return response.ok
  } catch {
    return false
  }
}
