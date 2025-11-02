"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { applyTheme, type ThemeName, getCurrentThemeTokens } from "@/lib/theme-utils"
import { Button } from "@/components/ui/button"
import { GlassCard } from "@/components/ui/GlassCard"

/**
 * Theme Preview Component
 * Displays all three persona themes side-by-side for testing and comparison
 * Allows manual theme switching to preview the entire app in different themes
 */

interface ThemeOption {
  name: ThemeName
  label: string
  personality: string
  description: string
  primaryColor: string
  secondaryColor: string
  highlightColor: string
}

const themes: ThemeOption[] = [
  {
    name: "mid-game",
    label: "Mid-Game Maestro",
    personality: "Strategic & Decisive",
    description: "Gold palette for players who dominate the mid-game with calculated plays",
    primaryColor: "#C5A35E",
    secondaryColor: "#E3C98A",
    highlightColor: "#FFD88A",
  },
  {
    name: "mapmaker",
    label: "Silent Mapmaker",
    personality: "Tactical & Supportive",
    description: "Blue/teal palette for vision-focused players who control the map",
    primaryColor: "#1B66FF",
    secondaryColor: "#5EA8FF",
    highlightColor: "#9FD0FF",
  },
  {
    name: "split-push",
    label: "Split Pusher",
    personality: "Aggressive & Independent",
    description: "Crimson palette for solo lane dominators who pressure objectives",
    primaryColor: "#E94560",
    secondaryColor: "#FF7B95",
    highlightColor: "#FFB1C1",
  },
]

export function ThemePreview() {
  const [activeTheme, setActiveTheme] = useState<ThemeName>("mid-game")
  const [showTokens, setShowTokens] = useState(false)

  const handleThemeChange = (themeName: ThemeName) => {
    setActiveTheme(themeName)
    applyTheme(themeName)
  }

  const currentTokens = getCurrentThemeTokens()

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="mx-auto max-w-7xl">
        {/* Header */}
        <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="mb-8 text-center">
          <h1 className="text-5xl font-bold text-white">
            <span className="text-accent">RIFT</span>REVIEW
          </h1>
          <p className="mt-2 text-lg text-muted-foreground">Persona Theme System Preview</p>
        </motion.div>

        {/* Theme Switcher */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="mb-8"
        >
          <GlassCard>
            <h2 className="mb-4 text-xl font-bold text-white">Active Theme</h2>
            <div className="flex flex-wrap gap-3">
              {themes.map((theme) => (
                <Button
                  key={theme.name}
                  onClick={() => handleThemeChange(theme.name)}
                  className={`flex-1 ${
                    activeTheme === theme.name
                      ? "bg-accent text-black hover:bg-accent/90"
                      : "bg-card text-white hover:bg-card/80"
                  }`}
                  style={
                    activeTheme === theme.name
                      ? {}
                      : {
                          borderColor: theme.primaryColor,
                          borderWidth: "2px",
                        }
                  }
                >
                  {theme.label}
                </Button>
              ))}
            </div>
            <div className="mt-4 text-center">
              <p className="text-sm text-muted-foreground">
                Current:{" "}
                <span className="font-bold text-accent">{themes.find((t) => t.name === activeTheme)?.label}</span>
              </p>
            </div>
          </GlassCard>
        </motion.div>

        {/* Theme Comparison Grid */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="mb-8 grid gap-6 md:grid-cols-3"
        >
          {themes.map((theme, index) => (
            <motion.div
              key={theme.name}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.3 + index * 0.1 }}
            >
              <GlassCard className={activeTheme === theme.name ? "ring-2 ring-accent" : ""}>
                <div className="mb-4">
                  <h3 className="text-xl font-bold text-white">{theme.label}</h3>
                  <p className="text-sm text-muted-foreground">{theme.personality}</p>
                </div>

                <p className="mb-4 text-sm leading-relaxed text-muted-foreground">{theme.description}</p>

                {/* Color Palette */}
                <div className="space-y-2">
                  <p className="text-xs font-semibold text-white">Color Palette</p>
                  <div className="flex gap-2">
                    <div
                      className="h-12 flex-1 rounded-lg border border-border"
                      style={{ backgroundColor: theme.primaryColor }}
                      title="Primary"
                    />
                    <div
                      className="h-12 flex-1 rounded-lg border border-border"
                      style={{ backgroundColor: theme.secondaryColor }}
                      title="Secondary"
                    />
                    <div
                      className="h-12 flex-1 rounded-lg border border-border"
                      style={{ backgroundColor: theme.highlightColor }}
                      title="Highlight"
                    />
                  </div>
                  <div className="flex justify-between text-[10px] text-muted-foreground">
                    <span>Primary</span>
                    <span>Secondary</span>
                    <span>Highlight</span>
                  </div>
                </div>

                {/* Sample UI Elements */}
                <div className="mt-4 space-y-3">
                  <div
                    className="rounded-lg border-2 p-3 text-center text-sm font-bold"
                    style={{ borderColor: theme.primaryColor, color: theme.primaryColor }}
                  >
                    Sample Button
                  </div>
                  <div className="flex items-center gap-2">
                    <div
                      className="h-3 w-3 rounded-full"
                      style={{ backgroundColor: theme.primaryColor, boxShadow: `0 0 10px ${theme.primaryColor}` }}
                    />
                    <span className="text-xs text-white">Accent Indicator</span>
                  </div>
                  <div
                    className="h-2 rounded-full"
                    style={{
                      background: `linear-gradient(to right, ${theme.primaryColor}, transparent)`,
                    }}
                  />
                </div>
              </GlassCard>
            </motion.div>
          ))}
        </motion.div>

        {/* Live Theme Tokens */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="mb-8"
        >
          <GlassCard>
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-xl font-bold text-white">Live CSS Variables</h2>
              <Button onClick={() => setShowTokens(!showTokens)} variant="outline" size="sm">
                {showTokens ? "Hide" : "Show"} Tokens
              </Button>
            </div>

            {showTokens && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                className="grid gap-2 md:grid-cols-2"
              >
                {Object.entries(currentTokens).map(([key, value]) => (
                  <div key={key} className="flex items-center justify-between rounded-lg bg-card/50 p-2 text-xs">
                    <span className="font-mono text-muted-foreground">
                      --{key.replace(/([A-Z])/g, "-$1").toLowerCase()}
                    </span>
                    <span className="font-mono text-white">{value}</span>
                  </div>
                ))}
              </motion.div>
            )}
          </GlassCard>
        </motion.div>

        {/* Sample Dashboard Elements */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}>
          <GlassCard glow="accent">
            <h2 className="mb-4 text-xl font-bold text-white">Sample Dashboard Elements</h2>

            <div className="grid gap-4 md:grid-cols-3">
              {/* Stat Card */}
              <div className="glass-card rounded-xl p-4">
                <p className="text-sm text-muted-foreground">Win Rate</p>
                <p className="mt-2 text-3xl font-bold text-accent">67%</p>
                <div className="mt-3 h-1 rounded-full bg-gradient-to-r from-accent to-transparent" />
              </div>

              {/* Champion Card */}
              <div className="glass-card rounded-xl p-4">
                <div className="mb-2 flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-br from-accent to-accent-secondary text-2xl font-bold text-white">
                  A
                </div>
                <p className="mt-2 font-bold text-white">Ahri</p>
                <p className="text-sm text-muted-foreground">24 games</p>
              </div>

              {/* Badge */}
              <div className="glass-card flex items-center justify-center rounded-xl p-4">
                <div className="inline-flex items-center gap-2 rounded-full border-2 border-accent px-4 py-2">
                  <div
                    className="h-3 w-3 rounded-full bg-accent"
                    style={{ boxShadow: "0 0 10px var(--accent-primary)" }}
                  />
                  <span className="font-bold text-white">Mid Lane</span>
                </div>
              </div>
            </div>
          </GlassCard>
        </motion.div>

        {/* Footer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
          className="mt-8 text-center text-sm text-muted-foreground"
        >
          <p>Theme system powered by CSS variables and data attributes</p>
          <p className="mt-1">Switch themes above to see the entire preview update in real-time</p>
        </motion.div>
      </div>
    </div>
  )
}
