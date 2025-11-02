"use client"

import { cn } from "@/lib/utils"
import Image from "next/image"
import { getAvatarUrl, getRankInitial } from "@/lib/avatar-utils"

interface PlayerAvatarProps {
  src: string
  alt: string
  size?: "sm" | "md" | "lg"
  showRankBadge?: boolean
  rank?: string
  className?: string
}

const sizeMap = {
  sm: "h-10 w-10",
  md: "h-16 w-16",
  lg: "h-24 w-24",
}

export function PlayerAvatar({
  src,
  alt,
  size = "md",
  showRankBadge = false,
  rank = "Platinum",
  className,
}: PlayerAvatarProps) {
  const avatarUrl = getAvatarUrl(src)
  const rankInitial = getRankInitial(rank)

  return (
    <div className={cn("relative inline-block", className)}>
      <div className={cn("relative overflow-hidden rounded-full border-2 border-border bg-muted", sizeMap[size])}>
        <Image
          src={avatarUrl || "/placeholder.svg"}
          alt={alt}
          fill
          className="object-cover"
          sizes={size === "lg" ? "96px" : size === "md" ? "64px" : "40px"}
        />
      </div>
      {showRankBadge && (
        <div
          className="absolute bottom-0 right-0 flex h-5 w-5 items-center justify-center rounded-full border-2 border-background bg-accent text-[10px] font-bold text-background"
          aria-label={`Rank: ${rank}`}
          title={rank}
        >
          {rankInitial}
        </div>
      )}
    </div>
  )
}
