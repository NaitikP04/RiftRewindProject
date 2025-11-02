"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { Button } from "@/components/ui/button"
import { exportToImage } from "@/lib/html2canvas-export"
import type { PlayerData } from "@/lib/types"

/**
 * Share actions: download image and copy link
 */

interface ShareActionsProps {
  playerData: PlayerData
}

export function ShareActions({ playerData }: ShareActionsProps) {
  const [isDownloading, setIsDownloading] = useState(false)
  const [copied, setCopied] = useState(false)
  const [showConfetti, setShowConfetti] = useState(false)

  const handleDownload = async () => {
    setIsDownloading(true)
    try {
      await exportToImage("share-preview", `${playerData.username}-riftreview.png`)
      setShowConfetti(true)
      setTimeout(() => setShowConfetti(false), 2000)
    } catch (error) {
      console.error("Download failed:", error)
    } finally {
      setIsDownloading(false)
    }
  }

  const handleCopyLink = () => {
    const mockUrl = `https://riftreview.gg/share/${playerData.username.toLowerCase()}`
    navigator.clipboard.writeText(mockUrl)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="relative">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="flex flex-col gap-4 sm:flex-row"
      >
        <Button
          onClick={handleDownload}
          disabled={isDownloading}
          className="flex-1 bg-accent py-6 text-lg font-bold text-black hover:bg-accent/90"
        >
          {isDownloading ? "Downloading..." : "Download Image"}
        </Button>

        <Button
          onClick={handleCopyLink}
          variant="outline"
          className="flex-1 border-accent bg-transparent py-6 text-lg font-bold text-accent hover:bg-accent/10"
        >
          {copied ? "Link Copied!" : "Copy Share Link"}
        </Button>
      </motion.div>

      {showConfetti && (
        <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
          {[...Array(30)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute h-2 w-2 rounded-full bg-accent"
              initial={{
                x: 0,
                y: 0,
                opacity: 1,
              }}
              animate={{
                x: (Math.random() - 0.5) * 400,
                y: (Math.random() - 0.5) * 400,
                opacity: 0,
              }}
              transition={{
                duration: 1.5,
                ease: "easeOut",
              }}
            />
          ))}
        </div>
      )}
    </div>
  )
}
