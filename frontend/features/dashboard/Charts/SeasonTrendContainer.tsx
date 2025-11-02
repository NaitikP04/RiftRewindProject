"use client"

import { useState } from "react"
import { usePlayerData } from "@/context/PlayerDataProvider"
import { GlassCard } from "@/components/ui/GlassCard"
import { SeasonTrendChart } from "./SeasonTrendChart"
import { SeasonAnnotation } from "./SeasonAnnotation"
import { rankToNumber, formatMonth } from "@/lib/rank-utils"

export function SeasonTrendContainer() {
  const { playerData, personaTheme } = usePlayerData()
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null)
  const [pinnedIndex, setPinnedIndex] = useState<number | null>(null)

  if (!playerData || !personaTheme) return null

  const { seasonMonths, rankTimeline, rankEvents } = playerData

  if (!seasonMonths || !rankTimeline || seasonMonths.length === 0) {
    console.debug("[v0] Season trend data missing or empty")
    return null
  }

  const chartData = seasonMonths.map((month, index) => ({
    month,
    rank: rankToNumber(rankTimeline[index]),
    monthLabel: formatMonth(month),
  }))

  const activeIndex = pinnedIndex !== null ? pinnedIndex : hoveredIndex
  const activeMonth = activeIndex !== null ? seasonMonths[activeIndex] : null
  const activeRank = activeIndex !== null ? rankTimeline[activeIndex] : null
  const activeEvent = activeMonth ? rankEvents?.[activeMonth] : undefined

  const handlePointClick = (index: number) => {
    console.debug("[v0] Pinned annotation at index:", index)
    setPinnedIndex(pinnedIndex === index ? null : index)
  }

  return (
    <GlassCard className="col-span-full">
      <div className="space-y-4">
        <div>
          <h3 className="text-lg font-bold text-foreground">Season Performance Trends</h3>
          <p className="text-sm text-muted-foreground">
            Hover a point to see what happened that month (fun facts included)
          </p>
        </div>

        <SeasonTrendChart
          data={chartData}
          accentColor={personaTheme.accent}
          onPointHover={setHoveredIndex}
          onPointClick={handlePointClick}
          hoveredIndex={hoveredIndex}
          pinnedIndex={pinnedIndex}
        />

        {activeIndex !== null && activeMonth && activeRank && (
          <div className="mt-4">
            <SeasonAnnotation
              month={formatMonth(activeMonth)}
              rank={activeRank}
              event={activeEvent}
              isPinned={pinnedIndex === activeIndex}
              onClose={() => setPinnedIndex(null)}
              accentColor={personaTheme.accent}
            />
          </div>
        )}
      </div>
    </GlassCard>
  )
}
