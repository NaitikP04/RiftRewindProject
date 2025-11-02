/**
 * Avatar utility functions for handling placeholder fallbacks
 */

export const PLACEHOLDER_AVATAR = "/assets/avatars/placeholder.jpg"

/**
 * Returns a valid avatar URL or falls back to placeholder
 */
export function getAvatarUrl(profilePicture?: string): string {
  if (!profilePicture || profilePicture.trim() === "") {
    console.debug("[v0] Using placeholder avatar - no profilePicture provided")
    return PLACEHOLDER_AVATAR
  }
  return profilePicture
}

/**
 * Gets the first letter of a rank for badge display
 */
export function getRankInitial(rank?: string): string {
  if (!rank) return "?"
  return rank.charAt(0).toUpperCase()
}
