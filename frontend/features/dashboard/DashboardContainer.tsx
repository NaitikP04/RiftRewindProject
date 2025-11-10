"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { motion } from "framer-motion"
import { usePlayerData } from "@/context/PlayerDataProvider"
import { ChampionSpotlight } from "./HeroRow/ChampionSpotlight"
import { StatHighlights } from "./HeroRow/StatHighlights"
import { AIInsights } from "./HeroRow/AIInsights"
import { RoleBadge } from "./MiniWidgets/RoleBadge"
import { SeasonTrendContainer } from "./Charts/SeasonTrendContainer"
import { Button } from "@/components/ui/button"
import { PlayerIdentity } from "@/components/ui/PlayerIdentity"
import { PersonaVignette } from "@/components/ui/PersonaVignette"

/**
 * Main dashboard container
 * Displays player stats, champion performance, and AI insights
 */

export function DashboardContainer() {
  const { playerData, personaTheme } = usePlayerData()
  const router = useRouter()

  useEffect(() => {
    if (!playerData) {
      router.push("/")
    }
  }, [playerData, router])

  if (!playerData) {
    return null
  }

  return (
    <>
      <PersonaVignette personality={playerData.personality} role={playerData.mainRole} />

      <div className="relative z-10 min-h-screen px-4 py-8 md:px-8 lg:px-16">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8 flex flex-col items-start justify-between gap-4 md:flex-row md:items-center"
        >
          <div className="flex items-center gap-4">
            <PlayerIdentity
              displayName={playerData.displayName}
              profilePicture={playerData.profilePicture}
              mainRole={playerData.mainRole}
              size="lg"
              showRole={false}
            />
            <div className="mt-2">
              <RoleBadge role={playerData.mainRole} />
            </div>
          </div>

          <Button onClick={() => router.push("/share")} className="bg-accent font-bold text-black hover:bg-accent/90">
            Share Results
          </Button>
        </motion.div>

        {/* Hero Row - Champions */}
        <section className="mb-12">
          <motion.h2 
            initial={{ opacity: 0, x: -20 }} 
            animate={{ opacity: 1, x: 0 }} 
            transition={{ delay: 0.1 }}
            className="mb-6 text-3xl font-bold text-white"
          >
            🏆 Top Champions
          </motion.h2>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {playerData.topChampions.map((champion, index) => (
              <ChampionSpotlight key={champion.name} champion={champion} index={index} />
            ))}
          </div>
        </section>

        {/* Stat Highlights */}
        <section className="mb-12">
          <motion.h2
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="mb-6 text-3xl font-bold text-white"
          >
            ⚡ Performance Highlights
          </motion.h2>
          <StatHighlights highlights={playerData.highlights} />
        </section>

        {/* AI Insights */}
        <section className="mb-12">
          <motion.h2
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
            className="mb-6 text-3xl font-bold text-white"
          >
            🤖 AI Analysis
          </motion.h2>
          <AIInsights insight={playerData.aiInsight} personality={playerData.personality} />
        </section>

        {/* Season Performance Trends - Interactive rank progression chart */}
        <section className="mb-8">
          <motion.h2
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
            className="mb-6 text-3xl font-bold text-white"
          >
            📈 Season Performance Trends
          </motion.h2>
          <SeasonTrendContainer />
        </section>
      </div>
    </>
  )
}
