"use client"

import { cn } from "@/lib/utils"
import Image from "next/image"
import { getAvatarUrl } from "@/lib/avatar-utils"
import { getRankIconDataUri, getRankTierLabel } from "@/lib/rank-utils"

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
  rank = "Unranked",
  className,
}: PlayerAvatarProps) {
  const avatarUrl = getAvatarUrl(src)
  const rankIcon = getRankIconDataUri(rank)
  const rankLabel = getRankTierLabel(rank)

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
          className="absolute -bottom-1 -right-1 flex h-7 w-7 items-center justify-center rounded-full border-2 border-background bg-background/60 backdrop-blur"
          aria-label={`Rank: ${rank}`}
          title={rank}
        >
          <Image
            src={rankIcon}
            alt={`${rankLabel} rank emblem`}
            width={24}
            height={24}
            className="h-6 w-6"
          />
        </div>
      )}
    </div>
  )
}
