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

export function AnalysisProgress({ 
  analysisId, 
  apiUrl = "http://localhost:8000",
  onComplete,
  onError 
}: AnalysisProgressProps) {
  const [progress, setProgress] = useState(0)
  const [currentStep, setCurrentStep] = useState<string>("profile")
  const [message, setMessage] = useState<string>("Starting analysis...")
  const [isComplete, setIsComplete] = useState(false)
  const [hasError, setHasError] = useState(false)

  useEffect(() => {
    let eventSource: EventSource | null = null
    let reconnectTimeout: NodeJS.Timeout | null = null

    const connect = () => {
      console.log(`[AnalysisProgress] Connecting to SSE: ${apiUrl}/api/analysis/${analysisId}/progress`)
      
      eventSource = new EventSource(`${apiUrl}/api/analysis/${analysisId}/progress`)

      eventSource.onmessage = (event) => {
        try {
          const data: ProgressUpdate = JSON.parse(event.data)
          console.log("[AnalysisProgress] Update:", data)
          
          setProgress(data.progress)
          setCurrentStep(data.step)
          setMessage(data.message)

          if (data.step === "complete") {
            setIsComplete(true)
            eventSource?.close()
            onComplete?.()
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
        
        // Retry connection after 2 seconds if not complete
        if (!isComplete && !hasError) {
          console.log("[AnalysisProgress] Reconnecting in 2s...")
          reconnectTimeout = setTimeout(connect, 2000)
        }
      }
    }

    connect()

    return () => {
      console.log("[AnalysisProgress] Cleaning up SSE connection")
      eventSource?.close()
      if (reconnectTimeout) clearTimeout(reconnectTimeout)
    }
  }, [analysisId, apiUrl, onComplete, onError, isComplete, hasError])

  return (
    <Card className="p-6 space-y-4">
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold">
            {STEP_LABELS[currentStep] || currentStep}
          </h3>
          <span className="text-sm text-muted-foreground">
            {progress}%
          </span>
        </div>
        
        <Progress value={progress} className="h-2" />
        
        <AnimatePresence mode="wait">
          <motion.p
            key={message}
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            className="text-sm text-muted-foreground"
          >
            {message}
          </motion.p>
        </AnimatePresence>
      </div>

      {hasError && (
        <div className="p-4 bg-destructive/10 border border-destructive rounded-md">
          <p className="text-sm text-destructive font-medium">
            Analysis failed: {message}
          </p>
        </div>
      )}

      {isComplete && (
        <div className="p-4 bg-green-500/10 border border-green-500 rounded-md">
          <p className="text-sm text-green-600 dark:text-green-400 font-medium">
            🎉 Analysis complete! Redirecting to dashboard...
          </p>
        </div>
      )}
    </Card>
  )
}
