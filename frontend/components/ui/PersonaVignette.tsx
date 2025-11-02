"use client"

import { useEffect } from "react"
import { getPersonaTheme } from "@/lib/personalization"

interface PersonaVignetteProps {
  personality: string
  role: string
}

export function PersonaVignette({ personality, role }: PersonaVignetteProps) {
  useEffect(() => {
    const theme = getPersonaTheme(personality, role)

    // Apply CSS variable for dynamic accent color
    document.documentElement.style.setProperty("--persona-accent", theme.accentColor)

    console.log("[v0] Applied persona theme:", theme.accent, "for", personality)
  }, [personality, role])

  const theme = getPersonaTheme(personality, role)

  return (
    <div
      className="pointer-events-none fixed inset-0 z-0"
      style={{
        background: theme.vignetteStyle,
      }}
      aria-hidden="true"
    />
  )
}
