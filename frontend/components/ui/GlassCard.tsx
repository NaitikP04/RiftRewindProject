import { cn } from "@/lib/utils"
import type { ReactNode } from "react"

/**
 * Glass morphism card component with optional glow effects
 */

interface GlassCardProps {
  children: ReactNode
  className?: string
  glow?: "accent" | "none"
}

export function GlassCard({ children, className, glow = "none" }: GlassCardProps) {
  return (
    <div className={cn("glass-card rounded-xl p-6", glow === "accent" && "glow-accent", className)}>{children}</div>
  )
}
