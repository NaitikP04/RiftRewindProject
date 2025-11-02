/**
 * Persona-driven UI personalization utilities
 * Maps player personality to accent colors and theme adjustments
 */

export type PersonaAccent = "gold" | "blue" | "red"

export interface PersonaTheme {
  accent: PersonaAccent
  accentColor: string
  glowClass: string
  vignetteStyle: string
  tagline: string
}

export function getPersonaTheme(personality: string, role: string): PersonaTheme {
  const lowerPersonality = personality.toLowerCase()
  const lowerRole = role.toLowerCase()

  // Mid-Game Maestro → Gold
  if (lowerPersonality.includes("mid-game maestro") || lowerPersonality.includes("maestro")) {
    return {
      accent: "gold",
      accentColor: "#C5A35E",
      glowClass: "glow-gold",
      vignetteStyle: "radial-gradient(circle at center, transparent 40%, rgba(197, 163, 94, 0.15) 100%)",
      tagline: "Mid-Game Maestro — you make plays that tilt outcomes.",
    }
  }

  // Silent Mapmaker (Support) → Blue
  if (
    lowerPersonality.includes("silent mapmaker") ||
    lowerPersonality.includes("mapmaker") ||
    lowerRole === "support"
  ) {
    return {
      accent: "blue",
      accentColor: "#1B66FF",
      glowClass: "glow-blue",
      vignetteStyle: "radial-gradient(circle at center, transparent 40%, rgba(27, 102, 255, 0.2) 100%)",
      tagline: "Silent Mapmaker — games are won before fights even begin.",
    }
  }

  // Split Pusher → Red
  if (lowerPersonality.includes("split pusher") || lowerPersonality.includes("pusher")) {
    return {
      accent: "red",
      accentColor: "#E94560",
      glowClass: "glow-red",
      vignetteStyle: "radial-gradient(ellipse at 80% 50%, transparent 30%, rgba(233, 69, 96, 0.25) 100%)",
      tagline: "Split Pusher — when lanes are empty, you're already taking towers.",
    }
  }

  // Default fallback
  return {
    accent: "gold",
    accentColor: "#C5A35E",
    glowClass: "glow-gold",
    vignetteStyle: "radial-gradient(circle at center, transparent 40%, rgba(197, 163, 94, 0.15) 100%)",
    tagline: personality,
  }
}
