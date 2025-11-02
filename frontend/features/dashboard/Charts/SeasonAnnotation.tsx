"use client"

import { motion, AnimatePresence } from "framer-motion"
import { X } from "lucide-react"
import type { RankEvent } from "@/lib/types"
import { cn } from "@/lib/utils"

interface SeasonAnnotationProps {
  month: string
  rank: string
  event?: RankEvent
  isPinned: boolean
  onClose: () => void
  accentColor: string
}

export function SeasonAnnotation({ month, rank, event, isPinned, onClose, accentColor }: SeasonAnnotationProps) {
  const effectColors = {
    win: "border-green-500/50 bg-green-950/30",
    loss: "border-red-500/50 bg-red-950/30",
    streak: "border-yellow-500/50 bg-yellow-950/30",
  }

  const effectColor = event ? effectColors[event.effect] : "border-border bg-card/80"

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, scale: 0.9, y: -10 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.9, y: -10 }}
        transition={{ duration: 0.2 }}
        className={cn(
          "relative rounded-lg border-2 p-4 backdrop-blur-sm",
          effectColor,
          isPinned && "shadow-lg shadow-accent/20",
        )}
        style={{
          borderColor: isPinned ? accentColor : undefined,
        }}
      >
        {isPinned && (
          <button
            onClick={onClose}
            className="absolute right-2 top-2 rounded-full p-1 hover:bg-background/20"
            aria-label="Close annotation"
          >
            <X className="h-3 w-3" />
          </button>
        )}

        <div className="space-y-2">
          <div className="flex items-center justify-between gap-2">
            <p className="text-xs font-semibold text-muted-foreground">{month}</p>
            <p className="text-sm font-bold" style={{ color: accentColor }}>
              {rank}
            </p>
          </div>

          {event ? (
            <>
              <p className="text-sm leading-relaxed text-foreground">{event.message}</p>
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <span className="font-medium">Champion: {event.champion}</span>
                <span
                  className={cn(
                    "rounded-full px-2 py-0.5 font-bold",
                    event.effect === "win" && "bg-green-500/20 text-green-400",
                    event.effect === "loss" && "bg-red-500/20 text-red-400",
                    event.effect === "streak" && "bg-yellow-500/20 text-yellow-400",
                  )}
                >
                  {event.effect === "win" ? "+" : event.effect === "loss" ? "-" : "~"}
                </span>
              </div>
            </>
          ) : (
            <p className="text-sm text-muted-foreground">No notable events — steady climb</p>
          )}
        </div>
      </motion.div>
    </AnimatePresence>
  )
}
