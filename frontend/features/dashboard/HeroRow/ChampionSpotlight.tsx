"use client"

import { motion } from "framer-motion"
import type { Champion } from "@/lib/types"

/**
 * Champion spotlight with circular progress ring and glow effect
 */

interface ChampionSpotlightProps {
  champion: Champion
  index: number
}

export function ChampionSpotlight({ champion, index }: ChampionSpotlightProps) {
  const circumference = 2 * Math.PI * 70
  const offset = circumference - (champion.winRate / 100) * circumference

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1, duration: 0.5 }}
      whileHover={{ scale: 1.05 }}
      className="glass-card relative flex flex-col items-center rounded-xl p-6 transition-all duration-300"
    >
      {/* Circular progress ring */}
      <div className="relative">
        <svg className="h-40 w-40 -rotate-90 transform">
          {/* Background circle */}
          <circle cx="80" cy="80" r="70" stroke="rgba(255,255,255,0.1)" strokeWidth="8" fill="none" />
          <motion.circle
            cx="80"
            cy="80"
            r="70"
            stroke="var(--accent-primary)"
            strokeWidth="8"
            fill="none"
            strokeLinecap="round"
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: offset }}
            transition={{ duration: 1.5, ease: [0.22, 0.9, 0.38, 1] }}
            style={{
              strokeDasharray: circumference,
            }}
          />
        </svg>

        {/* Champion image placeholder */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="flex h-28 w-28 items-center justify-center rounded-full bg-gradient-to-br from-accent to-accent-secondary text-3xl font-bold text-white shadow-lg">
            {champion.name.charAt(0)}
          </div>
        </div>

        <motion.div
          animate={{
            opacity: [0.3, 0.6, 0.3],
            scale: [1, 1.1, 1],
          }}
          transition={{
            duration: 2,
            repeat: Number.POSITIVE_INFINITY,
            ease: "easeInOut",
          }}
          className="absolute inset-0 -z-10 rounded-full bg-accent blur-xl"
        />
      </div>

      {/* Champion info */}
      <div className="mt-4 text-center">
        <h3 className="text-xl font-bold text-white">{champion.name}</h3>
        <p className="mt-1 text-sm text-muted-foreground">{champion.games} games</p>
        <div className="mt-2 text-3xl font-bold text-accent">{champion.winRate}%</div>
        <p className="text-xs text-muted-foreground">Win Rate</p>
      </div>
    </motion.div>
  )
}
