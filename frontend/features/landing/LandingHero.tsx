"use client"

import { motion } from "framer-motion"

/**
 * Hero section with title, tagline, and visual elements
 */

export function LandingHero() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="text-center"
    >
      <motion.h1
        className="text-balance text-7xl font-bold leading-tight"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1, duration: 0.5 }}
      >
        <span className="text-accent">RIFT</span>
        <span className="text-white">REVIEW</span>
      </motion.h1>

      <motion.p
        className="text-balance mx-auto mt-6 max-w-2xl text-xl text-muted-foreground"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2, duration: 0.5 }}
      >
        Your AI-powered League of Legends coach. Get personalized insights, track your progress, and level up your
        gameplay.
      </motion.p>

      <div className="absolute left-1/2 top-0 -z-10 h-[500px] w-[500px] -translate-x-1/2 rounded-full bg-accent opacity-10 blur-[120px]" />
    </motion.div>
  )
}
