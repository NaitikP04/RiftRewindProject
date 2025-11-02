"use client"

import { createContext, useContext, useState, useEffect, type ReactNode } from "react"
import type { PlayerData } from "@/lib/types"
import { getPersonaTheme, type PersonaTheme } from "@/lib/personalization"
import { getThemeNameFromPersonality, applyTheme } from "@/lib/theme-utils"

/**
 * Context provider for global player data state
 * Manages current player profile across the application
 */

interface PlayerDataContextType {
  playerData: PlayerData | null
  setPlayerData: (data: PlayerData | null) => void
  isLoading: boolean
  setIsLoading: (loading: boolean) => void
  personaTheme: PersonaTheme | null
}

const PlayerDataContext = createContext<PlayerDataContextType | undefined>(undefined)

export function PlayerDataProvider({ children }: { children: ReactNode }) {
  const [playerData, setPlayerData] = useState<PlayerData | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const personaTheme = playerData ? getPersonaTheme(playerData.personality, playerData.mainRole) : null

  useEffect(() => {
    if (playerData?.personality) {
      const themeName = getThemeNameFromPersonality(playerData.personality)
      applyTheme(themeName)
    }
  }, [playerData?.personality])

  return (
    <PlayerDataContext.Provider value={{ playerData, setPlayerData, isLoading, setIsLoading, personaTheme }}>
      {children}
    </PlayerDataContext.Provider>
  )
}

export function usePlayerData() {
  const context = useContext(PlayerDataContext)
  if (context === undefined) {
    throw new Error("usePlayerData must be used within a PlayerDataProvider")
  }
  return context
}
