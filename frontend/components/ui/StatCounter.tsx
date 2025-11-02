"use client"

import { useEffect, useState } from "react"
import { useMotionValue, useTransform, animate } from "framer-motion"

/**
 * Animated stat counter with smooth count-up animation
 */

interface StatCounterProps {
  value: string
  duration?: number
}

export function StatCounter({ value, duration = 1 }: StatCounterProps) {
  const [displayValue, setDisplayValue] = useState(value)
  const motionValue = useMotionValue(0)
  const rounded = useTransform(motionValue, (latest) => {
    const numMatch = value.match(/[\d.]+/)
    if (!numMatch) {
      return value
    }
    const decimals = numMatch[0].includes(".") ? 1 : 0
    return latest.toFixed(decimals)
  })

  useEffect(() => {
    // Check if value contains a number
    const numMatch = value.match(/[\d.]+/)
    if (!numMatch) {
      setDisplayValue(value)
      return
    }

    const targetNum = Number.parseFloat(numMatch[0])
    const prefix = value.substring(0, numMatch.index)
    const suffix = value.substring((numMatch.index || 0) + numMatch[0].length)

    const unsubscribe = rounded.on("change", (latest) => {
      setDisplayValue(`${prefix}${latest}${suffix}`)
    })

    const controls = animate(motionValue, targetNum, {
      duration,
      ease: [0.22, 0.9, 0.38, 1],
    })

    return () => {
      unsubscribe()
      controls.stop()
    }
  }, [value, duration])

  return <span>{displayValue}</span>
}
