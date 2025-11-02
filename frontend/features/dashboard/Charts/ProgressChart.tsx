"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts"
import { GlassCard } from "@/components/ui/GlassCard"

/**
 * Animated line chart for tracking progress over time
 * Now includes stat toggles for better data visualization
 */

interface ProgressChartProps {
  title: string
  data: Array<{ season: string; [key: string]: string | number }>
  dataKeys: Array<{ key: string; label: string; color: string }>
}

export function ProgressChart({ title, data, dataKeys }: ProgressChartProps) {
  const [visibleStats, setVisibleStats] = useState<Set<string>>(new Set(dataKeys.map((dk) => dk.key)))

  const toggleStat = (key: string) => {
    setVisibleStats((prev) => {
      const newSet = new Set(prev)
      if (newSet.has(key)) {
        newSet.delete(key)
      } else {
        newSet.add(key)
      }
      return newSet
    })
  }

  const activeDataKeys = dataKeys.filter((dk) => visibleStats.has(dk.key))

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
      <GlassCard>
        <div className="mb-4 flex flex-wrap items-center justify-between gap-4">
          <h3 className="text-xl font-bold text-white">{title}</h3>

          <div className="flex flex-wrap gap-2">
            {dataKeys.map((dk) => (
              <button
                key={dk.key}
                onClick={() => toggleStat(dk.key)}
                className={`rounded-full px-3 py-1 text-xs font-medium transition-all ${
                  visibleStats.has(dk.key)
                    ? "bg-white/10 text-white ring-1 ring-white/20"
                    : "bg-white/5 text-muted-foreground"
                }`}
                style={{
                  borderColor: visibleStats.has(dk.key) ? dk.color : "transparent",
                  borderWidth: visibleStats.has(dk.key) ? "2px" : "0",
                }}
              >
                {dk.label}
              </button>
            ))}
          </div>
        </div>

        {activeDataKeys.length === 0 ? (
          <div className="flex h-[300px] items-center justify-center text-muted-foreground">
            Select at least one stat to display
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              <defs>
                {activeDataKeys.map((dk) => (
                  <linearGradient key={dk.key} id={`gradient-${dk.key}`} x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={dk.color} stopOpacity={0.8} />
                    <stop offset="95%" stopColor={dk.color} stopOpacity={0.1} />
                  </linearGradient>
                ))}
              </defs>

              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />

              <XAxis dataKey="season" stroke="var(--muted-gray)" style={{ fontSize: "12px" }} />

              <YAxis stroke="var(--muted-gray)" style={{ fontSize: "12px" }} />

              <Tooltip
                contentStyle={{
                  backgroundColor: "var(--bg-800)",
                  border: "1px solid rgba(255,255,255,0.1)",
                  borderRadius: "8px",
                  color: "white",
                }}
                labelStyle={{ color: "var(--muted-gray)", marginBottom: "8px" }}
                formatter={(value: number, name: string) => {
                  const dataKey = activeDataKeys.find((dk) => dk.key === name)
                  return [
                    `${value}${name.toLowerCase().includes("rate") ? "%" : ""}`,
                    dataKey?.label || name.toUpperCase(),
                  ]
                }}
              />

              <Legend wrapperStyle={{ color: "var(--muted-gray)", fontSize: "12px" }} iconType="line" iconSize={16} />

              {activeDataKeys.map((dk) => (
                <Line
                  key={dk.key}
                  type="monotone"
                  dataKey={dk.key}
                  name={dk.label}
                  stroke={dk.color}
                  strokeWidth={3}
                  dot={{ fill: dk.color, r: 5 }}
                  activeDot={{ r: 7, fill: dk.color }}
                  animationDuration={1500}
                  animationEasing="ease-in-out"
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        )}
      </GlassCard>
    </motion.div>
  )
}
