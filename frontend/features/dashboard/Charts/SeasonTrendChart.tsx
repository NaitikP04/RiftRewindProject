"use client"

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"
import { motion } from "framer-motion"
import { numberToRank } from "@/lib/rank-utils"
import { useReducedMotion } from "@/hooks/use-reduced-motion"

interface ChartDataPoint {
  month: string
  rank: number
  monthLabel: string
}

interface SeasonTrendChartProps {
  data: ChartDataPoint[]
  accentColor: string
  onPointHover: (index: number | null) => void
  onPointClick: (index: number) => void
  hoveredIndex: number | null
  pinnedIndex: number | null
}

export function SeasonTrendChart({
  data,
  accentColor,
  onPointHover,
  onPointClick,
  hoveredIndex,
  pinnedIndex,
}: SeasonTrendChartProps) {
  const prefersReducedMotion = useReducedMotion()

  const CustomDot = (props: any) => {
    const { cx, cy, index } = props
    const isHovered = hoveredIndex === index
    const isPinned = pinnedIndex === index

    return (
      <motion.circle
        cx={cx}
        cy={cy}
        r={isPinned ? 8 : isHovered ? 6 : 4}
        fill={accentColor}
        stroke="hsl(var(--background))"
        strokeWidth={2}
        className="cursor-pointer"
        initial={prefersReducedMotion ? {} : { scale: 0, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ delay: index * 0.05, duration: 0.3 }}
        onMouseEnter={() => onPointHover(index)}
        onMouseLeave={() => onPointHover(null)}
        onClick={() => onPointClick(index)}
        tabIndex={0}
        role="button"
        aria-label={`Month ${data[index].monthLabel}, Rank ${numberToRank(data[index].rank)}`}
        onKeyDown={(e: any) => {
          if (e.key === "Enter" || e.key === " ") {
            onPointClick(index)
          }
        }}
      />
    )
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart
        data={data}
        margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
        onMouseLeave={() => onPointHover(null)}
      >
        <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.3} />
        <XAxis
          dataKey="monthLabel"
          stroke="hsl(var(--muted-foreground))"
          tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }}
        />
        <YAxis
          domain={[1, 9]}
          ticks={[1, 2, 3, 4, 5, 6, 7, 8, 9]}
          tickFormatter={(value) => numberToRank(value)}
          stroke="hsl(var(--muted-foreground))"
          tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }}
        />
        <Tooltip
          content={({ active, payload }) => {
            if (!active || !payload || !payload[0]) return null
            const data = payload[0].payload
            return (
              <div className="rounded-lg border border-border bg-card/95 p-2 text-xs backdrop-blur-sm">
                <p className="font-semibold">{data.monthLabel}</p>
                <p style={{ color: accentColor }}>{numberToRank(data.rank)}</p>
              </div>
            )
          }}
        />
        <Line
          type="monotone"
          dataKey="rank"
          stroke={accentColor}
          strokeWidth={3}
          dot={<CustomDot />}
          animationDuration={prefersReducedMotion ? 0 : 1000}
          animationEasing="ease-in-out"
        />
      </LineChart>
    </ResponsiveContainer>
  )
}
