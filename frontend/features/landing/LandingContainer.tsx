"use client"

import type React from "react"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { motion, AnimatePresence } from "framer-motion"
import { LandingHero } from "./LandingHero"
import { LoadingCinematic } from "./LoadingCinematic"
import { usePlayerData } from "@/context/PlayerDataProvider"
import { fetchPlayerData } from "@/lib/usePlayerDataFetch"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

/**
 * Main landing page container
 * Handles user input, data fetching, and navigation to dashboard
 */

export function LandingContainer() {
  const [input, setInput] = useState("")
  const [error, setError] = useState("")
  const { setPlayerData, isLoading, setIsLoading } = usePlayerData()
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")

    if (!input.trim()) {
      setError("Please enter a username")
      return
    }

    setIsLoading(true)

    try {
      const data = await fetchPlayerData(input.trim())

      if (data) {
        setPlayerData(data)
        router.push("/dashboard")
      } else {
        setError("Player not found. Please check your Riot ID and try again.")
        setIsLoading(false)
      }
    } catch (err) {
      setError("Failed to fetch player data. Please try again.")
      setIsLoading(false)
    }
  }

  return (
    <>
      <AnimatePresence>{isLoading && <LoadingCinematic />}</AnimatePresence>

      <div className="relative flex min-h-screen flex-col items-center justify-center px-4">
        <LandingHero />

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.5 }}
          className="mt-12 w-full max-w-md"
        >
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
