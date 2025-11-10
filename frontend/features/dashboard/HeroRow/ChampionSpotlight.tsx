"use client"

import { motion } from "framer-motion"
import type { Champion } from "@/lib/types"

/**
 * Champion spotlight with circular progress ring, champion icon, and glow effect
 */

interface ChampionSpotlightProps {
  champion: Champion
  index: number
}

export function ChampionSpotlight({ champion, index }: ChampionSpotlightProps) {
  const circumference = 2 * Math.PI * 70
  const offset = circumference - (champion.winRate / 100) * circumference
  
  // Clean champion name for DDragon API (remove spaces and special characters)
  const cleanChampionName = champion.name.replace(/[^a-zA-Z]/g, '')

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1, duration: 0.5 }}
      whileHover={{ scale: 1.05, y: -5 }}
      className="glass-card group relative flex flex-col items-center rounded-xl p-6 transition-all duration-300 hover:shadow-2xl hover:shadow-accent/20"
    >
      {/* Circular progress ring */}
      <div className="relative">
        <svg className="h-40 w-40 -rotate-90 transform">
          {/* Background circle */}
          <circle cx="80" cy="80" r="70" stroke="rgba(255,255,255,0.1)" strokeWidth="8" fill="none" />
          {/* Progress circle */}
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
              filter: "drop-shadow(0 0 8px var(--accent-primary))",
            }}
          />
        </svg>

        {/* Champion image from DDragon */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="relative h-28 w-28 overflow-hidden rounded-full border-4 border-accent/50 shadow-2xl ring-2 ring-accent/30 transition-all group-hover:border-accent group-hover:ring-accent/50">
            <img
              src={`https://ddragon.leagueoflegends.com/cdn/14.23.1/img/champion/${cleanChampionName}.png`}
              alt={champion.name}
              className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-110"
              onError={(e) => {
                // Fallback to first letter if image fails to load
                const img = e.currentTarget
                img.style.display = 'none'
                const fallback = img.nextElementSibling as HTMLElement
                if (fallback) fallback.style.display = 'flex'
              }}
            />
            {/* Fallback for image load failures */}
            <div className="absolute inset-0 hidden items-center justify-center bg-linear-to-br from-accent to-accent-secondary text-3xl font-bold text-white">
              {champion.name.charAt(0)}
            </div>
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
        <h3 className="text-xl font-bold text-white transition-colors group-hover:text-accent">{champion.name}</h3>
        <p className="mt-1 text-sm text-muted-foreground">{champion.games} games played</p>
        <div className="mt-3 flex items-baseline justify-center gap-1">
          <span className="text-4xl font-bold text-accent">{champion.winRate}</span>
          <span className="text-lg font-semibold text-accent/70">%</span>
        </div>
        <p className="mt-1 text-xs font-medium uppercase tracking-wide text-muted-foreground">Win Rate</p>
      </div>
    </motion.div>
  )
}
