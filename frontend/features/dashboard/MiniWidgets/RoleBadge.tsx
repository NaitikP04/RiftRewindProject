"use client"

import { motion } from "framer-motion"

/**
 * Role badge with icon and label
 */

interface RoleBadgeProps {
  role: string
}

export function RoleBadge({ role }: RoleBadgeProps) {
  const roleColors: Record<string, string> = {
    Top: "var(--accent-red)",
    Jungle: "var(--accent-gold)",
    Mid: "var(--accent-blue)",
    ADC: "#00D9FF",
    Support: "#6B48FF",
  }

  const color = roleColors[role] || "var(--accent-gold)"

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: 0.2 }}
      className="glass-card inline-flex items-center gap-2 rounded-full px-4 py-2"
      style={{ borderColor: color, borderWidth: 2 }}
    >
      <div className="h-3 w-3 rounded-full" style={{ backgroundColor: color, boxShadow: `0 0 10px ${color}` }} />
      <span className="text-sm font-bold text-white">{role}</span>
    </motion.div>
  )
}
