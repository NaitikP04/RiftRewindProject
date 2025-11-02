"use client"

import { PlayerAvatar } from "./PlayerAvatar"
import { cn } from "@/lib/utils"

interface PlayerIdentityProps {
  displayName: string
  profilePicture: string
  mainRole: string
  size?: "sm" | "md" | "lg"
  showRole?: boolean
  className?: string
}

export function PlayerIdentity({
  displayName,
  profilePicture,
  mainRole,
  size = "md",
  showRole = true,
  className,
}: PlayerIdentityProps) {
  return (
    <div className={cn("flex items-center gap-3", className)}>
      <PlayerAvatar src={profilePicture} alt={displayName} size={size} showRankBadge />
      <div className="flex flex-col">
        <h2
          className={cn(
            "font-bold text-foreground",
            size === "lg" && "text-2xl",
            size === "md" && "text-lg",
            size === "sm" && "text-base",
          )}
        >
          {displayName}
        </h2>
        {showRole && <p className="text-sm text-muted-foreground">{mainRole}</p>}
      </div>
    </div>
  )
}
