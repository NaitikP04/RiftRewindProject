"use client"

import { motion } from "framer-motion"
import type { Highlight } from "@/lib/types"
import { StatCounter } from "@/components/ui/StatCounter"

/**
 * Stat highlights cards with animated counters
 */

interface StatHighlightsProps {
  highlights: Highlight[]
}

export function StatHighlights({ highlights }: StatHighlightsProps) {
  return (
    <div className="grid gap-4 md:grid-cols-3">
      {highlights.map((highlight, index) => (
        <motion.div
          key={highlight.stat}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 + index * 0.1, duration: 0.5 }}
          whileHover={{ scale: 1.02, y: -4 }}
          className="glass-card rounded-xl p-6 transition-all duration-200"
        >
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">{highlight.stat}</p>
              <div className="mt-2 text-4xl font-bold text-white">
                <StatCounter value={highlight.value} duration={1.2} />
              </div>
            </div>

            <motion.div
              initial={{ scale: 0, rotate: 0 }}
              animate={{ scale: 1, rotate: 180 }}
              transition={{ delay: 0.5 + index * 0.1, duration: 0.6 }}
              className="h-8 w-8 rounded-full bg-gradient-to-br from-accent to-accent-secondary opacity-20"
            />
          </div>

          <motion.div
            initial={{ width: 0 }}
            animate={{ width: "100%" }}
            transition={{ delay: 0.6 + index * 0.1, duration: 0.8 }}
            className="mt-4 h-1 rounded-full bg-gradient-to-r from-accent to-transparent"
          />
        </motion.div>
      ))}
    </div>
  )
}
