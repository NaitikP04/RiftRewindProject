# RiftReview Theme System Documentation

## Overview

RiftReview implements a **persona-driven theming system** that dynamically applies color palettes based on player personality types. The system uses CSS variables and HTML data attributes for instant runtime theme switching without page reloads.

## Architecture

### Core Components

1. **CSS Variables** (`styles/tokens.css`)
   - Defines all theme color tokens
   - Uses `[data-theme="..."]` selectors for theme variants
   - Provides fallback values in `:root`

2. **Theme Utilities** (`lib/theme-utils.ts`)
   - `applyTheme(themeName)` - Sets data attribute on document
   - `getCurrentThemeTokens()` - Reads computed CSS variables
   - `getContrastRatio()` - Accessibility checking
   - `auditThemeAccessibility()` - WCAG compliance testing

3. **Personalization** (`lib/personalization.ts`)
   - Maps personality strings to theme names
   - Provides accent colors and glow classes
   - Returns taglines and vignette styles

4. **Provider Integration** (`context/PlayerDataProvider.tsx`)
   - Automatically applies theme when player data loads
   - Uses `useEffect` to watch personality changes
   - Triggers theme application via `applyTheme()`

## Three Persona Themes

### 1. Mid-Game Maestro (Gold)

**Theme Name:** `mid-game`  
**Personality:** Strategic, decisive players who dominate mid-game

**Color Palette:**
\`\`\`css
--accent-primary: #C5A35E;      /* Warm gold */
--accent-secondary: #E3C98A;    /* Light gold */
--accent-highlight: #FFD88A;    /* Bright gold */
--accent-rim: rgba(197, 163, 94, 0.18);
--glow: rgba(197, 163, 94, 0.22);
\`\`\`

**Use Cases:**
- Mid lane players
- Strategic shot-callers
- Players with high objective control

### 2. Silent Mapmaker (Blue/Teal)

**Theme Name:** `mapmaker`  
**Personality:** Tactical, vision-focused support players

**Color Palette:**
\`\`\`css
--accent-primary: #1B66FF;      /* Vibrant blue */
--accent-secondary: #5EA8FF;    /* Sky blue */
--accent-highlight: #9FD0FF;    /* Light blue */
--accent-rim: rgba(27, 102, 255, 0.14);
--glow: rgba(27, 102, 255, 0.18);
\`\`\`

**Use Cases:**
- Support players
- Vision-focused players
- Map control specialists

### 3. Split Pusher (Crimson)

**Theme Name:** `split-push`  
**Personality:** Aggressive, independent solo laners

**Color Palette:**
\`\`\`css
--accent-primary: #E94560;      /* Bold crimson */
--accent-secondary: #FF7B95;    /* Pink-red */
--accent-highlight: #FFB1C1;    /* Light pink */
--accent-rim: rgba(233, 69, 96, 0.16);
--glow: rgba(233, 69, 96, 0.22);
\`\`\`

**Use Cases:**
- Top lane players
- Split push specialists
- Aggressive duelists

## Implementation Guide

### Using Theme Tokens in Components

Always use CSS variable tokens instead of hardcoded colors:

#### ✅ Correct Usage

\`\`\`tsx
// Tailwind utility classes
<div className="bg-accent text-white border-accent">
  <span className="text-accent-secondary">Themed text</span>
</div>

// CSS variables in inline styles
<div style={{ backgroundColor: 'var(--accent-primary)' }}>
  Content
</div>

// Theme-aware utilities
<div className="glass-card glow-accent">
  <button className="bg-accent hover:bg-accent/90">
    Button
  </button>
</div>
\`\`\`

#### ❌ Incorrect Usage

\`\`\`tsx
// Hardcoded hex colors
<div className="bg-[#C5A35E]">Content</div>

// Hardcoded inline styles
<div style={{ color: '#1B66FF' }}>Text</div>

// Specific theme classes
<div className="bg-accent-gold">Content</div>
\`\`\`

### Available Theme Tokens

#### Color Tokens

| Token | Purpose | Example Value |
|-------|---------|---------------|
| `--accent-primary` | Main accent color | `#C5A35E` |
| `--accent-secondary` | Lighter accent variant | `#E3C98A` |
| `--accent-highlight` | Brightest accent | `#FFD88A` |
| `--accent-rim` | Subtle borders (alpha) | `rgba(197, 163, 94, 0.18)` |
| `--glow` | Glow effects (alpha) | `rgba(197, 163, 94, 0.22)` |

#### Tailwind Utility Classes

| Class | CSS Output |
|-------|------------|
| `bg-accent` | `background-color: var(--accent-primary)` |
| `text-accent` | `color: var(--accent-primary)` |
| `text-accent-secondary` | `color: var(--accent-secondary)` |
| `text-accent-highlight` | `color: var(--accent-highlight)` |
| `border-accent` | `border-color: var(--accent-primary)` |
| `border-accent-rim` | `border-color: var(--accent-rim)` |

#### Special Utilities

| Class | Purpose |
|-------|---------|
| `glass-card` | Glass morphism with theme-aware rim |
| `glow-accent` | Box shadow with theme glow |
| `glow-accent-sm` | Small glow effect |
| `glow-accent-lg` | Large glow effect |
| `persona-vignette` | Background gradient overlay |

#### Chart Tokens

| Token | Purpose |
|-------|---------|
| `--chart-1` | Primary chart line color |
| `--chart-1-boost` | Chart fill gradient |

#### Vignette Tokens

| Token | Purpose |
|-------|---------|
| `--vignette-start` | Gradient start color |
| `--vignette-end` | Gradient end color |
| `--vignette-direction` | Gradient angle (deg) |

### Automatic Theme Application

The theme system automatically applies when player data loads:

\`\`\`tsx
// In PlayerDataProvider.tsx
useEffect(() => {
  if (playerData?.personality) {
    const themeName = getThemeNameFromPersonality(playerData.personality)
    applyTheme(themeName)
  }
}, [playerData?.personality])
\`\`\`

### Manual Theme Switching

For testing or custom implementations:

\`\`\`tsx
import { applyTheme } from '@/lib/theme-utils'

// Switch to specific theme
applyTheme('mid-game')    // Gold theme
applyTheme('mapmaker')    // Blue theme
applyTheme('split-push')  // Crimson theme
\`\`\`

### Reading Current Theme

\`\`\`tsx
import { getCurrentThemeTokens } from '@/lib/theme-utils'

const tokens = getCurrentThemeTokens()
console.log(tokens.accentPrimary) // "#C5A35E"
\`\`\`

## Theme Preview Component

Visit `/theme-preview` to access the interactive theme testing interface:

### Features

- **Side-by-side comparison** of all three themes
- **Interactive theme switcher** to test entire app
- **Live color palettes** showing all accent variants
- **CSS variable inspector** displaying computed values
- **Sample UI elements** in each theme
- **Real-time updates** when switching themes

### Usage

\`\`\`tsx
import { ThemePreview } from '@/components/ThemePreview'

export default function ThemePreviewPage() {
  return <ThemePreview />
}
\`\`\`

## Accessibility

### WCAG Compliance

All theme combinations meet **WCAG AA** standards:

- **Normal text**: 4.5:1 contrast minimum
- **Large text**: 3:1 contrast minimum
- **UI components**: 3:1 contrast minimum

### Contrast Checking

Run accessibility audit in browser console:

\`\`\`tsx
import { auditThemeAccessibility } from '@/lib/theme-utils'

auditThemeAccessibility()
// Logs contrast ratios for current theme
\`\`\`

### Manual Contrast Check

\`\`\`tsx
import { getContrastRatio, meetsWCAG_AA } from '@/lib/theme-utils'

const ratio = getContrastRatio('#C5A35E', '#121318')
console.log(`Contrast: ${ratio.toFixed(2)}:1`)

const passes = meetsWCAG_AA('#C5A35E', '#121318')
console.log(`WCAG AA: ${passes ? 'PASS' : 'FAIL'}`)
\`\`\`

## Adding New Themes

### Step 1: Define CSS Variables

Add new theme in `styles/tokens.css`:

\`\`\`css
[data-theme="new-persona"],
.theme-new-persona {
  --accent-primary: #YOUR_COLOR;
  --accent-secondary: #LIGHTER_VARIANT;
  --accent-highlight: #BRIGHTEST_VARIANT;
  --accent-rim: rgba(YOUR_RGB, 0.18);
  --glow: rgba(YOUR_RGB, 0.22);
  --vignette-start: rgba(0, 0, 0, 0);
  --vignette-end: rgba(YOUR_RGB_DARK, 0.6);
  --vignette-direction: 180deg;
  --chart-1: #YOUR_COLOR;
  --chart-1-boost: rgba(YOUR_RGB, 0.14);
  --particle: rgba(YOUR_RGB_LIGHT, 0.08);
}
\`\`\`

### Step 2: Update Type Definitions

In `lib/theme-utils.ts`:

\`\`\`tsx
export type ThemeName = "mid-game" | "mapmaker" | "split-push" | "new-persona"
\`\`\`

### Step 3: Add Personality Mapping

In `lib/personalization.ts`:

\`\`\`tsx
export function getPersonaTheme(personality: string, role: string): PersonaTheme {
  const lowerPersonality = personality.toLowerCase()
  
  if (lowerPersonality.includes("new persona")) {
    return {
      accent: "new-color",
      accentColor: "#YOUR_COLOR",
      glowClass: "glow-new",
      vignetteStyle: "radial-gradient(...)",
      tagline: "New Persona — description",
    }
  }
  
}
\`\`\`

### Step 4: Update Theme Utils

In `lib/theme-utils.ts`:

\`\`\`tsx
export function getThemeNameFromPersonality(personality: string): ThemeName {
  const lower = personality.toLowerCase()
  
  if (lower.includes("new persona")) {
    return "new-persona"
  }
  
}
\`\`\`

### Step 5: Test in Theme Preview

1. Add new theme to `ThemePreview.tsx` themes array
2. Visit `/theme-preview`
3. Verify colors, contrast, and UI elements
4. Run accessibility audit

## Best Practices

### Do's

- ✅ Always use CSS variable tokens (`var(--accent-primary)`)
- ✅ Use Tailwind utility classes (`bg-accent`, `text-accent`)
- ✅ Test all themes in `/theme-preview`
- ✅ Run accessibility audits before deployment
- ✅ Use semantic token names (`--accent-primary` not `--gold`)
- ✅ Provide fallback values in `:root`

### Don'ts

- ❌ Never hardcode hex colors in components
- ❌ Don't use theme-specific classes (`bg-accent-gold`)
- ❌ Don't skip contrast checking
- ❌ Don't mix hardcoded and token-based colors
- ❌ Don't forget to update TypeScript types
- ❌ Don't use `!important` to override theme colors

## Troubleshooting

### Theme Not Applying

1. Check `data-theme` attribute on `<html>` element
2. Verify CSS variables are defined in `tokens.css`
3. Ensure `applyTheme()` is called after personality loads
4. Check browser console for `[v0]` theme logs

### Colors Not Updating

1. Verify component uses CSS variables, not hardcoded colors
2. Check Tailwind utilities are mapped in `globals.css`
3. Clear browser cache and rebuild
4. Inspect computed styles in DevTools

### Contrast Issues

1. Run `auditThemeAccessibility()` in console
2. Check contrast ratios meet WCAG AA (4.5:1 for text)
3. Adjust `--accent-primary` lightness if needed
4. Test with browser accessibility tools

## File Reference

| File | Purpose |
|------|---------|
| `styles/tokens.css` | Theme CSS variable definitions |
| `app/globals.css` | Tailwind utilities and theme mapping |
| `lib/theme-utils.ts` | Theme application and utilities |
| `lib/personalization.ts` | Personality → theme mapping |
| `context/PlayerDataProvider.tsx` | Automatic theme application |
| `components/ThemePreview.tsx` | Theme testing interface |

## Resources

- [CSS Variables (MDN)](https://developer.mozilla.org/en-US/docs/Web/CSS/Using_CSS_custom_properties)
- [WCAG Contrast Guidelines](https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html)
- [Tailwind CSS v4 Documentation](https://tailwindcss.com/docs)
- [Data Attributes (MDN)](https://developer.mozilla.org/en-US/docs/Learn/HTML/Howto/Use_data_attributes)

---

**Last Updated:** 2025-01-27  
**Version:** 1.0.0
