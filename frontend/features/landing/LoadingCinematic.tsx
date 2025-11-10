"use client"

import { motion, AnimatePresence } from "framer-motion"
import { useEffect, useState } from "react"

/**
 * Cinematic loading animation with logo pulse and particle effects
 * Shows real-time progress messages during analysis
 */

const PROGRESS_STEPS = [
  { progress: 5, message: "Connecting to Riot API...", delay: 5000 },
  { progress: 10, message: "Loading summoner profile...", delay: 6000 },
  { progress: 15, message: "Validating account...", delay: 5000 },
  { progress: 20, message: "Fetching match history...", delay: 7000 },
  { progress: 25, message: "Downloading match details...", delay: 8000 },
  { progress: 30, message: "Processing game data...", delay: 8000 },
  { progress: 35, message: "Analyzing first batch of matches...", delay: 9000 },
  { progress: 40, message: "Calculating performance metrics...", delay: 10000 },
  { progress: 45, message: "Examining champion statistics...", delay: 10000 },
  { progress: 50, message: "Identifying playstyle patterns...", delay: 12000 },
  { progress: 55, message: "Selecting key matches for deep dive...", delay: 12000 },
  { progress: 60, message: "Analyzing game timelines...", delay: 15000 },
  { progress: 65, message: "Processing combat data...", delay: 15000 },
  { progress: 70, message: "Evaluating decision-making patterns...", delay: 18000 },
  { progress: 75, message: "Preparing AI analysis...", delay: 20000 },
  { progress: 80, message: "Generating insights with Claude AI...", delay: 25000 },
  { progress: 85, message: "Finalizing personality analysis...", delay: 20000 },
  { progress: 90, message: "Compiling recommendations...", delay: 15000 },
  { progress: 95, message: "Almost there...", delay: 10000 },
  { progress: 98, message: "Finishing up...", delay: 5000 },
]

export function LoadingCinematic() {
  const [progress, setProgress] = useState(0)
  const [message, setMessage] = useState("Initializing analysis...")
  const [stepIndex, setStepIndex] = useState(0)

  useEffect(() => {
    const currentStep = PROGRESS_STEPS[stepIndex]
    if (!currentStep) return

    const timer = setTimeout(() => {
      setProgress(currentStep.progress)
      setMessage(currentStep.message)
      setStepIndex(prev => prev + 1)
    }, currentStep.delay)

    return () => clearTimeout(timer)
  }, [stepIndex])
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 flex items-center justify-center bg-background"
    >
      {/* Particle background */}
      <div className="absolute inset-0 overflow-hidden">
        {[...Array(20)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute h-1 w-1 rounded-full bg-accent"
            initial={{
              x: typeof window !== "undefined" ? Math.random() * window.innerWidth : 0,
              y: typeof window !== "undefined" ? Math.random() * window.innerHeight : 0,
              opacity: 0,
            }}
            animate={{
              y: typeof window !== "undefined" ? [null, Math.random() * window.innerHeight] : 0,
              opacity: [0, 0.6, 0],
            }}
            transition={{
              duration: 2 + Math.random() * 2,
              repeat: Number.POSITIVE_INFINITY,
              ease: "linear",
            }}
          />
        ))}
      </div>

      {/* Logo pulse */}
      <div className="relative z-10 text-center space-y-8 px-4">
        <motion.div
          animate={{
            scale: [1, 1.1, 1],
            opacity: [0.8, 1, 0.8],
          }}
          transition={{
            duration: 1.5,
            repeat: Number.POSITIVE_INFINITY,
            ease: "easeInOut",
          }}
        >
          <div className="text-6xl font-bold text-accent">
            RIFT<span className="text-white">REWIND</span>
          </div>
        </motion.div>

        {/* Progress bar with percentage */}
        <div className="max-w-md mx-auto space-y-4">
          <div className="flex items-center justify-between">
            <motion.p
              key={message}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="text-sm font-medium text-foreground"
            >
              {message}
            </motion.p>
            <motion.span
              key={progress}
              initial={{ scale: 1.2, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="text-sm font-mono font-bold text-accent"
            >
              {progress}%
            </motion.span>
          </div>

          {/* Progress bar */}
          <div className="relative h-2 bg-muted rounded-full overflow-hidden">
            <motion.div
              className="absolute top-0 left-0 h-full bg-accent"
              initial={{ width: "0%" }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.5, ease: "easeOut" }}
            />
            
            {/* Shimmer effect */}
            <motion.div
              className="absolute top-0 left-0 h-full w-20 bg-linear-to-r from-transparent via-white/30 to-transparent"
              animate={{
                x: [-100, 500],
              }}
              transition={{
                duration: 1.5,
                repeat: Infinity,
                ease: "linear",
              }}
            />
          </div>
        </div>

        {/* Additional info */}
        <AnimatePresence mode="wait">
          <motion.p
            key={stepIndex}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="text-xs text-muted-foreground"
          >
            {progress < 50 && "Fetching data from Riot Games API..."}
            {progress >= 50 && progress < 85 && "Analyzing your gameplay patterns..."}
            {progress >= 85 && "Generating AI-powered insights..."}
          </motion.p>
        </AnimatePresence>
      </div>
    </motion.div>
  )
}
