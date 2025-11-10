"use client"

import type React from "react"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { motion, AnimatePresence } from "framer-motion"
import { LandingHero } from "./LandingHero"
import { LoadingCinematic } from "./LoadingCinematic"
import { AnalysisProgress } from "@/components/ui/AnalysisProgress"
import { usePlayerData } from "@/context/PlayerDataProvider"
import { fetchProfile, fetchAnalysis } from "@/lib/api-client"
import type { PlayerData } from "@/lib/types"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

/**
 * Main landing page container
 * Handles user input, data fetching, and navigation to dashboard
 */

export function LandingContainer() {
  const [input, setInput] = useState("")
  const [error, setError] = useState("")
  const [analysisId, setAnalysisId] = useState<string | null>(null)
  const { setPlayerData, isLoading, setIsLoading } = usePlayerData()
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setAnalysisId(null)

    if (!input.trim()) {
      setError("Please enter a username")
      return
    }

    setIsLoading(true)

    try {
      const riotId = input.trim()
      console.log(`[Landing] Starting data fetch for ${riotId}`)
      
      // Phase 1: Get profile quickly
      const profileResult = await fetchProfile(riotId)
      
      if (!profileResult.success || !profileResult.profile) {
        setError(profileResult.error || "Player not found")
        setIsLoading(false)
        return
      }
      
      console.log('[Landing] Profile received, starting analysis...')
      
      // Phase 2: Start analysis and get analysis_id for progress tracking
      const analysisResult = await fetchAnalysis(riotId, 100)
      
      if (!analysisResult.success) {
        setError(analysisResult.error || "Analysis failed")
        setIsLoading(false)
        return
      }
      
      // If we got an analysis_id, show progress bar
      if (analysisResult.analysis_id) {
        console.log('[Landing] Got analysis_id:', analysisResult.analysis_id)
        setAnalysisId(analysisResult.analysis_id)
      }
      
      // If we got data immediately, navigate to dashboard
      if (analysisResult.data) {
        const analysis = analysisResult.data
        console.log('[Landing] Analysis complete!')
        
        const playerData: PlayerData = {
          username: riotId.split('#')[0],
          tag: riotId.split('#')[1],
          displayName: analysis.displayName,
          profilePicture: analysis.profilePicture,
          mainRole: analysis.mainRole,
          rank: analysis.rank,
          topChampions: analysis.topChampions,
          highlights: analysis.highlights,
          aiInsight: analysis.aiInsight,
          recommendedActions: analysis.recommendedActions ?? [],
          personality: analysis.personality,
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
        
        setPlayerData(playerData)
        router.push("/dashboard")
      }
    } catch (err) {
      setError("Failed to fetch player data. Please try again.")
      setIsLoading(false)
    }
  }

  const handleAnalysisComplete = () => {
    console.log('[Landing] Analysis complete, navigating to dashboard')
    // Analysis is complete, we should have the data in context
    router.push("/dashboard")
  }

  const handleAnalysisError = (errorMsg: string) => {
    console.error('[Landing] Analysis error:', errorMsg)
    setError(errorMsg)
    setIsLoading(false)
    setAnalysisId(null)
  }

  return (
    <>
      <AnimatePresence>{isLoading && !analysisId && <LoadingCinematic />}</AnimatePresence>

      <div className="relative flex min-h-screen flex-col items-center justify-center px-4">
        <LandingHero />

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.5 }}
          className="mt-12 w-full max-w-md"
        >
          {analysisId ? (
            // Show progress bar during analysis
            <AnalysisProgress 
              analysisId={analysisId} 
              onComplete={handleAnalysisComplete}
              onError={handleAnalysisError}
            />
          ) : (
            // Show input form
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="glass-card rounded-xl p-6">
                <label htmlFor="username" className="mb-2 block text-sm font-medium text-muted-foreground">
                  Enter Your Riot ID
                </label>
                <Input
                  id="username"
                  type="text"
                  placeholder="Username#TAG"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  className="bg-card text-white placeholder:text-muted-foreground"
                  disabled={isLoading}
                />

                {error && (
                  <motion.p
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-2 text-sm text-destructive"
                  >
                    {error}
                  </motion.p>
                )}
              </div>

              <Button
                type="submit"
                disabled={isLoading}
                className="w-full bg-accent py-6 text-lg font-bold text-black hover:bg-accent/90"
              >
                {isLoading ? "Analyzing..." : "Get My Analysis"}
              </Button>
            </form>
          )}
        </motion.div>

        {/* Bottom decorative elements */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="absolute bottom-8 flex gap-8 text-xs text-muted-foreground"
        >
          <span>Powered by AI</span>
          <span>•</span>
          <span>Real-time Analysis</span>
          <span>•</span>
          <span>Personalized Insights</span>
        </motion.div>
      </div>
    </>
  )
}
