"use client"

import { motion } from "framer-motion"
import { GlassCard } from "@/components/ui/GlassCard"

/**
 * AI-generated insights and recommendations
 */

interface AIInsightsProps {
  insight: string
  personality: string
}

export function AIInsights({ insight, personality }: AIInsightsProps) {
  // Split insight into main text and bullet points if present
  const suggestions = [
    "Focus on objective control during mid-game",
    "Improve vision placement in enemy jungle",
    "Practice wave management for better recalls",
  ]

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.4, duration: 0.5 }}
    >
      <GlassCard glow="accent" className="relative overflow-hidden">
        {/* AI Badge */}
        <div className="mb-4 inline-flex items-center gap-2 rounded-full bg-accent/20 px-3 py-1 text-xs font-semibold text-accent">
          <span className="relative flex h-2 w-2">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-accent opacity-75"></span>
            <span className="relative inline-flex h-2 w-2 rounded-full bg-accent"></span>
          </span>
          AI INSIGHTS
        </div>

        <h3 className="text-2xl font-bold text-white">{personality}</h3>

        <p className="mt-4 text-base leading-relaxed text-muted-foreground">{insight}</p>

        {/* Action suggestions */}
        <div className="mt-6 space-y-3">
          <p className="text-sm font-semibold text-white">Recommended Actions:</p>
          {suggestions.map((suggestion, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.6 + index * 0.1 }}
              className="flex items-start gap-3"
            >
              <div className="mt-1 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-accent" />
              <p className="text-sm text-muted-foreground">{suggestion}</p>
            </motion.div>
          ))}
        </div>

        <div className="absolute -right-20 -top-20 h-40 w-40 rounded-full bg-accent opacity-10 blur-3xl" />
      </GlassCard>
    </motion.div>
  )
}
