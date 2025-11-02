/**
 * Theme utility functions for runtime theme management
 * Handles CSS variable manipulation, contrast checks, and theme application
 */

export type ThemeName = "mid-game" | "mapmaker" | "split-push" | "neutral"

export interface ThemeTokens {
  accentPrimary: string
  accentSecondary: string
  accentHighlight: string
  accentRim: string
  glow: string
  vignetteStart: string
  vignetteEnd: string
  vignetteDirection: string
  chart1: string
  chart1Boost: string
  particle: string
}

/**
 * Map personality strings to theme names
 */
export function getThemeNameFromPersonality(personality: string): ThemeName {
  const lower = personality.toLowerCase()

  if (lower.includes("mid-game maestro") || lower.includes("maestro")) {
    return "mid-game"
  }

  if (lower.includes("silent mapmaker") || lower.includes("mapmaker")) {
    return "mapmaker"
  }

  if (lower.includes("split pusher") || lower.includes("pusher")) {
    return "split-push"
  }

  return "mid-game" // default
}

/**
 * Apply theme to document root via data attribute
 */
export function applyTheme(themeName: ThemeName) {
  if (typeof document !== "undefined") {
    document.documentElement.setAttribute("data-theme", themeName)
    console.log(`[v0] Applied theme: ${themeName}`)
  }
}

/**
 * Get current theme tokens from CSS variables
 */
export function getCurrentThemeTokens(): ThemeTokens {
  if (typeof window === "undefined") {
    return getDefaultThemeTokens()
  }

  const style = getComputedStyle(document.documentElement)

  return {
    accentPrimary: style.getPropertyValue("--accent-primary").trim(),
    accentSecondary: style.getPropertyValue("--accent-secondary").trim(),
    accentHighlight: style.getPropertyValue("--accent-highlight").trim(),
    accentRim: style.getPropertyValue("--accent-rim").trim(),
    glow: style.getPropertyValue("--glow").trim(),
    vignetteStart: style.getPropertyValue("--vignette-start").trim(),
    vignetteEnd: style.getPropertyValue("--vignette-end").trim(),
    vignetteDirection: style.getPropertyValue("--vignette-direction").trim(),
    chart1: style.getPropertyValue("--chart-1").trim(),
    chart1Boost: style.getPropertyValue("--chart-1-boost").trim(),
    particle: style.getPropertyValue("--particle").trim(),
  }
}

/**
 * Default theme tokens (Mid-Game Maestro)
 */
function getDefaultThemeTokens(): ThemeTokens {
  return {
    accentPrimary: "#c5a35e",
    accentSecondary: "#e3c98a",
    accentHighlight: "#ffd88a",
    accentRim: "rgba(197, 163, 94, 0.18)",
    glow: "rgba(197, 163, 94, 0.22)",
    vignetteStart: "rgba(0, 0, 0, 0)",
    vignetteEnd: "rgba(10, 6, 2, 0.6)",
    vignetteDirection: "180deg",
    chart1: "#c5a35e",
    chart1Boost: "rgba(197, 163, 94, 0.14)",
    particle: "rgba(245, 223, 136, 0.08)",
  }
}

/**
 * Calculate relative luminance for contrast checking
 * Based on WCAG 2.1 formula
 */
function getLuminance(r: number, g: number, b: number): number {
  const [rs, gs, bs] = [r, g, b].map((c) => {
    const sRGB = c / 255
    return sRGB <= 0.03928 ? sRGB / 12.92 : Math.pow((sRGB + 0.055) / 1.055, 2.4)
  })
  return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs
}

/**
 * Parse hex color to RGB
 */
function hexToRgb(hex: string): { r: number; g: number; b: number } | null {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
  return result
    ? {
        r: Number.parseInt(result[1], 16),
        g: Number.parseInt(result[2], 16),
        b: Number.parseInt(result[3], 16),
      }
    : null
}

/**
 * Calculate contrast ratio between two colors
 * Returns ratio (1-21), where 4.5:1 is WCAG AA for normal text
 */
export function getContrastRatio(color1: string, color2: string): number {
  const rgb1 = hexToRgb(color1)
  const rgb2 = hexToRgb(color2)

  if (!rgb1 || !rgb2) return 0

  const lum1 = getLuminance(rgb1.r, rgb1.g, rgb1.b)
  const lum2 = getLuminance(rgb2.r, rgb2.g, rgb2.b)

  const lighter = Math.max(lum1, lum2)
  const darker = Math.min(lum1, lum2)

  return (lighter + 0.05) / (darker + 0.05)
}

/**
 * Check if color combination meets WCAG AA standards
 */
export function meetsWCAG_AA(foreground: string, background: string, largeText = false): boolean {
  const ratio = getContrastRatio(foreground, background)
  return largeText ? ratio >= 3 : ratio >= 4.5
}

/**
 * Run accessibility audit on current theme
 * Logs warnings for failing combinations
 */
export function auditThemeAccessibility() {
  if (typeof window === "undefined") return

  const tokens = getCurrentThemeTokens()
  const bgColor = "#121318" // --bg-800
  const textColor = "#e9edf0" // --text-primary

  console.group("[v0] Theme Accessibility Audit")

  // Check text on background
  const textContrast = getContrastRatio(textColor, bgColor)
  console.log(`Text on background: ${textContrast.toFixed(2)}:1 ${textContrast >= 4.5 ? "✓ PASS" : "✗ FAIL"}`)

  // Check accent on background
  const accentContrast = getContrastRatio(tokens.accentPrimary, bgColor)
  console.log(
    `Accent on background: ${accentContrast.toFixed(2)}:1 ${accentContrast >= 3 ? "✓ PASS (large text)" : "⚠ WARNING"}`,
  )

  // Check accent on card
  const cardBg = "#0f1014" // approximate card-bg
  const accentOnCard = getContrastRatio(tokens.accentPrimary, cardBg)
  console.log(`Accent on card: ${accentOnCard.toFixed(2)}:1 ${accentOnCard >= 3 ? "✓ PASS (large text)" : "⚠ WARNING"}`)

  console.groupEnd()
}
