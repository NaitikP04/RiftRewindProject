"use client"

import { useEffect, useState } from "react"
import { Progress } from "./progress"
import { Card } from "./card"
import { motion, AnimatePresence } from "framer-motion"

interface ProgressUpdate {
  step: string
  progress: number
  message: string
  timestamp: string
}

interface AnalysisProgressProps {
  analysisId: string
  apiUrl?: string
  onComplete?: () => void
  onError?: (error: string) => void
}

const STEP_LABELS: Record<string, string> = {
  profile: "📋 Loading Profile",
  matches: "📥 Fetching Match History",
  details: "📊 Analyzing Match Details",
  statistics: "🔢 Calculating Statistics",
  deep_dive: "🔍 Selecting Key Matches",
  timeline: "🔎 Analyzing Timelines",
  ai_analysis: "🤖 Generating AI Insights",
  complete: "✅ Analysis Complete",
  error: "❌ Error"
}

// Fake progress simulation for smooth UX
const FAKE_PROGRESS_STEPS = [
  { progress: 5, message: "Connecting to Riot API...", delay: 5000 },
  { progress: 10, message: "Loading profile data...", delay: 6000 },
  { progress: 15, message: "Validating summoner...", delay: 5000 },
  { progress: 20, message: "Fetching match history...", delay: 7000 },
  { progress: 30, message: "Downloading match details...", delay: 8000 },
  { progress: 40, message: "Processing game data...", delay: 10000 },
  { progress: 50, message: "Analyzing performance metrics...", delay: 12000 },
  { progress: 60, message: "Calculating champion stats...", delay: 15000 },
  { progress: 70, message: "Identifying playstyle patterns...", delay: 18000 },
  { progress: 75, message: "Selecting key matches...", delay: 20000 },
  { progress: 80, message: "Analyzing game timelines...", delay: 25000 },
  { progress: 85, message: "Preparing AI analysis...", delay: 20000 },
  { progress: 88, message: "Generating insights with Claude AI...", delay: 30000 },
  { progress: 92, message: "Finalizing personality analysis...", delay: 20000 },
  { progress: 95, message: "Compiling recommendations...", delay: 15000 },
  { progress: 98, message: "Almost there...", delay: 10000 },
]

export function AnalysisProgress({ 
  analysisId, 
  apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  onComplete,
  onError 
}: AnalysisProgressProps) {
  const [progress, setProgress] = useState(0)
  const [currentStep, setCurrentStep] = useState<string>("profile")
  const [message, setMessage] = useState<string>("Starting analysis...")
  const [isComplete, setIsComplete] = useState(false)
  const [hasError, setHasError] = useState(false)
  const [useRealProgress, setUseRealProgress] = useState(false)
  const [fakeStepIndex, setFakeStepIndex] = useState(0)

  // Fake progress animation for smooth UX
  useEffect(() => {
    if (useRealProgress || isComplete || hasError) return

    const currentFakeStep = FAKE_PROGRESS_STEPS[fakeStepIndex]
    if (!currentFakeStep) {
      // Reached end of fake steps, hold at 98%
      return
    }

    const timer = setTimeout(() => {
      setProgress(currentFakeStep.progress)
      setMessage(currentFakeStep.message)
      setFakeStepIndex(prev => prev + 1)
    }, currentFakeStep.delay)

    return () => clearTimeout(timer)
  }, [fakeStepIndex, useRealProgress, isComplete, hasError])

  // Real SSE progress tracking
  useEffect(() => {
    let eventSource: EventSource | null = null
    let reconnectTimeout: NodeJS.Timeout | null = null

    const connect = () => {
      console.log(`[AnalysisProgress] Connecting to SSE: ${apiUrl}/api/analysis/${analysisId}/progress`)
      
      eventSource = new EventSource(`${apiUrl}/api/analysis/${analysisId}/progress`)

      eventSource.onmessage = (event) => {
        try {
          const data: ProgressUpdate = JSON.parse(event.data)
          console.log("[AnalysisProgress] Real update:", data)
          
          // Switch to real progress when we get backend updates
          setUseRealProgress(true)
          setProgress(data.progress)
          setCurrentStep(data.step)
          setMessage(data.message)

          if (data.step === "complete") {
            setIsComplete(true)
            eventSource?.close()
            setTimeout(() => {
              onComplete?.()
            }, 1000)
          } else if (data.step === "error") {
            setHasError(true)
            eventSource?.close()
            onError?.(data.message)
          }
        } catch (err) {
          console.error("[AnalysisProgress] Failed to parse update:", err)
        }
      }

      eventSource.onerror = (error) => {
        console.error("[AnalysisProgress] SSE error:", error)
        eventSource?.close()
        
        // Keep showing fake progress on connection issues
        if (!isComplete && !hasError && !useRealProgress) {
          console.log("[AnalysisProgress] Connection lost, continuing with fake progress")
          reconnectTimeout = setTimeout(connect, 3000)
        }
      }
    }

    // Delay SSE connection slightly to let fake progress start
    const initialDelay = setTimeout(connect, 1000)

    return () => {
      console.log("[AnalysisProgress] Cleaning up SSE connection")
      clearTimeout(initialDelay)
      eventSource?.close()
      if (reconnectTimeout) clearTimeout(reconnectTimeout)
    }
  }, [analysisId, apiUrl, onComplete, onError, isComplete, hasError, useRealProgress])

  return (
    <Card className="p-6 space-y-4 relative overflow-hidden">
      {/* Animated background gradient */}
      <motion.div
        className="absolute inset-0 opacity-10"
        animate={{
          background: [
            "linear-gradient(45deg, #3b82f6 0%, #8b5cf6 100%)",
            "linear-gradient(90deg, #8b5cf6 0%, #ec4899 100%)",
            "linear-gradient(135deg, #ec4899 0%, #f59e0b 100%)",
            "linear-gradient(180deg, #f59e0b 0%, #3b82f6 100%)",
            "linear-gradient(45deg, #3b82f6 0%, #8b5cf6 100%)",
          ],
        }}
        transition={{
          duration: 8,
          repeat: Infinity,
          ease: "linear",
        }}
      />

      <div className="space-y-3 relative z-10">
        <div className="flex items-center justify-between gap-4">
          <motion.h3 
            className="text-lg font-semibold flex items-center gap-2 text-foreground"
            key={currentStep}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3 }}
          >
            {STEP_LABELS[currentStep] || currentStep}
          </motion.h3>
          <motion.span 
            className="text-base font-mono font-bold text-accent shrink-0"
            key={progress}
            initial={{ scale: 1.2, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.2 }}
          >
            {progress}%
          </motion.span>
        </div>
        
        <div className="relative">
          <Progress value={progress} className="h-2" />
          
          {/* Shimmer effect */}
          <motion.div
            className="absolute top-0 left-0 h-full w-20 bg-linear-to-r from-transparent via-white/30 to-transparent"
            animate={{
              x: [-100, 400],
            }}
            transition={{
              duration: 1.5,
              repeat: Infinity,
              ease: "linear",
            }}
          />
        </div>
        
        <AnimatePresence mode="wait">
          <motion.div
            key={message}
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            className="flex items-center gap-2"
          >
            {/* Pulsing dot indicator */}
            {!isComplete && !hasError && (
              <motion.div
                className="w-2 h-2 rounded-full bg-accent shrink-0"
                animate={{
                  scale: [1, 1.5, 1],
                  opacity: [1, 0.5, 1],
                }}
                transition={{
                  duration: 1.5,
                  repeat: Infinity,
                  ease: "easeInOut",
                }}
              />
            )}
            <p className="text-sm text-foreground font-medium">
              {message}
            </p>
          </motion.div>
        </AnimatePresence>

        {/* Particle effects */}
        {!isComplete && !hasError && (
          <div className="absolute top-0 left-0 w-full h-full pointer-events-none">
            {[...Array(5)].map((_, i) => (
              <motion.div
                key={i}
                className="absolute w-1 h-1 bg-accent rounded-full"
                initial={{
                  x: Math.random() * 100 + "%",
                  y: "100%",
                  opacity: 0,
                }}
                animate={{
                  y: "-10%",
                  opacity: [0, 1, 0],
                }}
                transition={{
                  duration: 3 + Math.random() * 2,
                  repeat: Infinity,
                  delay: Math.random() * 2,
                  ease: "easeOut",
                }}
              />
            ))}
          </div>
        )}
      </div>

      {hasError && (
        <motion.div 
          className="p-4 bg-destructive/10 border border-destructive rounded-md"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
        >
          <p className="text-sm text-destructive font-medium">
            Analysis failed: {message}
          </p>
        </motion.div>
      )}

      {isComplete && (
        <motion.div 
          className="p-4 bg-green-500/10 border border-green-500 rounded-md"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
        >
          <p className="text-sm text-green-600 dark:text-green-400 font-medium flex items-center gap-2">
            <motion.span
              animate={{ rotate: [0, 360] }}
              transition={{ duration: 0.5 }}
            >
              🎉
            </motion.span>
            Analysis complete! Redirecting to dashboard...
          </p>
        </motion.div>
      )}
    </Card>
  )
}
