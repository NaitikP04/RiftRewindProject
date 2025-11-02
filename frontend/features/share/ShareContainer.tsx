"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { motion } from "framer-motion"
import { usePlayerData } from "@/context/PlayerDataProvider"
import { SharePreview } from "./SharePreview"
import { ShareActions } from "./ShareActions"
import { Button } from "@/components/ui/button"

/**
 * Share page container
 * Displays shareable preview and export actions
 */

export function ShareContainer() {
  const { playerData } = usePlayerData()
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
    <div className="min-h-screen px-4 py-8">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="mb-8 text-center">
        <Button onClick={() => router.push("/dashboard")} variant="ghost" className="mb-4 text-[var(--muted-gray)]">
          ← Back to Dashboard
        </Button>

        <h1 className="text-4xl font-bold text-white">Share Your Results</h1>
        <p className="mt-2 text-[var(--muted-gray)]">Download your stats card or share with friends</p>
      </motion.div>

      {/* Preview */}
      <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.1 }}>
        <SharePreview playerData={playerData} />
      </motion.div>

      {/* Actions */}
      <div className="mx-auto mt-8 max-w-2xl">
        <ShareActions playerData={playerData} />
      </div>

      {/* Tips */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
        className="mx-auto mt-8 max-w-2xl text-center text-sm text-[var(--muted-gray)]"
      >
        <p>Share your progress with your team or on social media</p>
      </motion.div>
    </div>
  )
}
