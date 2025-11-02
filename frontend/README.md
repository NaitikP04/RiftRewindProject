# RiftReview — AI Game Coach & Analyzer

A cinematic League of Legends stats dashboard showcasing interactive rank progression with playful event annotations.

## 🎮 Quick Start Demo

### Run the App

\`\`\`bash
npm install
npm run dev
\`\`\`

Open [http://localhost:3000](http://localhost:3000)

### Try the Interactive Demo

**On the landing page, enter any of these:**

1. **`demo1`** → Jeevi (Mid, Gold accent, Silver→Diamond climb)
2. **`demo2`** → WardLord (Support, Blue accent, Gold→Master climb)  
3. **`demo3`** → Mountains (Top, Red accent, Platinum→Grandmaster climb)

**Or use Riot-style inputs:**
- `Jeevi#0001` or `jeevi 0001`
- `WardLord#EUW` or `wardlord euw`
- `Mountains#0818` or `mountains 0818`

### 🎯 What to Look For

After entering a demo profile, you'll see:

1. **Dashboard Header**: Player avatar with rank badge and role
2. **Top Champions**: Glassy cards with win rates and game counts
3. **Performance Highlights**: Animated stat counters
4. **AI Analysis**: Personalized coaching insights
5. **Season Performance Trends** ⭐ — **The star feature:**
   - Interactive line chart showing 12-month rank progression
   - Hover any point to see playful event annotations
   - Click to pin annotations
   - Real rank progression: Silver→Diamond, Gold→Master, etc.
   - Witty messages like "Hot streak — wrapped up a 6-game win streak"

## ✨ Key Features

### Season Performance Trends (Interactive Chart)

The main showcase component with:
- **12-month rank timeline** from mock data
- **Hover annotations** with contextual messages
- **Click to pin** annotations for closer reading
- **Rank progression visualization** (Silver, Gold, Platinum, Diamond, Master, Grandmaster)
- **Event markers** showing key moments (win streaks, champion experiments, clutch plays)
- **Persona-themed colors** (gold/blue/red based on player personality)

### Persona-Driven UI

Each demo profile has a unique accent color:
- **Jeevi (demo1)**: Gold — "Mid-Game Maestro"
- **WardLord (demo2)**: Blue — "Silent Mapmaker"
- **Mountains (demo3)**: Red — "Split Pusher"

Colors affect buttons, chart lines, glows, and vignette overlays.

### Profile Pictures

All avatars use placeholder images with role-specific queries:
- Mid laner avatar for Jeevi
- Support player avatar for WardLord
- Top laner avatar for Mountains

## 🎨 Theme System

### Overview

RiftReview uses a **persona-driven theming system** that dynamically applies color palettes based on player personality. The system uses CSS variables and data attributes for runtime theme switching.

### Three Persona Themes

1. **Mid-Game Maestro (Gold)** - `data-theme="mid-game"`
   - Primary: `#C5A35E` (warm gold)
   - For strategic, decisive players who dominate mid-game
   
2. **Silent Mapmaker (Blue/Teal)** - `data-theme="mapmaker"`
   - Primary: `#1B66FF` (vibrant blue)
   - For tactical, vision-focused support players
   
3. **Split Pusher (Crimson)** - `data-theme="split-push"`
   - Primary: `#E94560` (bold crimson)
   - For aggressive, independent solo laners

### How It Works

The theme system automatically applies when player data loads:

1. **PlayerDataProvider** detects personality from player data
2. Calls `applyTheme()` to set `data-theme` attribute on `<html>`
3. CSS variables update based on `[data-theme="..."]` selectors
4. All components using theme tokens update instantly

### Using Theme Tokens in Components

Always use CSS variable tokens instead of hardcoded colors:

\`\`\`tsx
// ✅ Good - uses theme-aware tokens
<div className="bg-accent text-white border-accent">
  <span className="text-accent">Themed text</span>
</div>

// ❌ Bad - hardcoded colors
<div className="bg-[#C5A35E] text-white border-[#C5A35E]">
  <span style={{ color: '#C5A35E' }}>Hardcoded text</span>
</div>
\`\`\`

### Available Theme Tokens

**Color Tokens:**
- `--accent-primary` - Main accent color
- `--accent-secondary` - Lighter accent variant
- `--accent-highlight` - Brightest accent for highlights
- `--accent-rim` - Subtle accent for borders (with alpha)
- `--glow` - Glow effect color (with alpha)

**Tailwind Utilities:**
- `bg-accent` - Background with accent color
- `text-accent` - Text with accent color
- `border-accent` - Border with accent color
- `glow-accent` - Glow effect with accent color
- `glass-card` - Glass morphism card with theme-aware rim

**Chart Tokens:**
- `--chart-1` - Primary chart color (matches accent)
- `--chart-1-boost` - Chart fill gradient

**Vignette Tokens:**
- `--vignette-start` - Gradient start color
- `--vignette-end` - Gradient end color
- `--vignette-direction` - Gradient direction (deg)

### Theme Preview

Visit `/theme-preview` to see all three themes side-by-side with:
- Interactive theme switcher
- Live color palettes
- CSS variable inspector
- Sample UI elements in each theme

### Manual Theme Switching

For testing or custom implementations:

\`\`\`tsx
import { applyTheme } from '@/lib/theme-utils'

// Switch to a specific theme
applyTheme('mid-game')    // Gold
applyTheme('mapmaker')    // Blue
applyTheme('split-push')  // Crimson
\`\`\`

### Accessibility

All theme combinations meet **WCAG AA** contrast standards:
- Text on background: 4.5:1 minimum
- Large text on background: 3:1 minimum
- Accent colors optimized for visibility on dark backgrounds

Run accessibility audit:

\`\`\`tsx
import { auditThemeAccessibility } from '@/lib/theme-utils'

auditThemeAccessibility() // Logs contrast ratios to console
\`\`\`

### File Structure

\`\`\`
styles/
  └── tokens.css              # Theme definitions with CSS variables
app/
  └── globals.css             # Theme utilities and Tailwind config
lib/
  ├── theme-utils.ts          # Theme application and utilities
  └── personalization.ts      # Personality → theme mapping
context/
  └── PlayerDataProvider.tsx  # Automatic theme application
components/
  └── ThemePreview.tsx        # Theme testing component
\`\`\`

### Adding New Themes

To add a new persona theme:

1. **Define CSS variables in `styles/tokens.css`:**

\`\`\`css
[data-theme="new-persona"] {
  --accent-primary: #YOUR_COLOR;
  --accent-secondary: #LIGHTER_VARIANT;
  --accent-highlight: #BRIGHTEST_VARIANT;
  --accent-rim: rgba(YOUR_RGB, 0.18);
  --glow: rgba(YOUR_RGB, 0.22);
  /* ... other tokens */
}
\`\`\`

2. **Add theme mapping in `lib/theme-utils.ts`:**

\`\`\`tsx
export type ThemeName = "mid-game" | "mapmaker" | "split-push" | "new-persona"
\`\`\`

3. **Update personality mapping in `lib/personalization.ts`:**

\`\`\`tsx
if (lowerPersonality.includes("new persona")) {
  return {
    accent: "new-color",
    accentColor: "#YOUR_COLOR",
    // ...
  }
}
\`\`\`

## 📁 Project Structure

\`\`\`
src/
├── app/
│   ├── page.tsx              # Landing page
│   ├── dashboard/page.tsx    # Dashboard with Season Trends
│   ├── share/page.tsx        # Share page
│   └── theme-preview/page.tsx # Theme testing page
├── features/
│   ├── landing/              # Landing components
│   ├── dashboard/
│   │   ├── Charts/
│   │   │   ├── SeasonTrendContainer.tsx  # Main chart container
│   │   │   ├── SeasonTrendChart.tsx      # Recharts line chart
│   │   │   └── SeasonAnnotation.tsx      # Hover/pin annotations
│   │   ├── HeroRow/          # Champion & stats
│   │   └── MiniWidgets/      # Role badges
│   └── share/                # Share components
├── components/
│   ├── ui/
│   │   ├── PlayerAvatar.tsx      # Avatar with rank badge
│   │   ├── PlayerIdentity.tsx    # Avatar + name display
│   │   ├── PersonaVignette.tsx   # Background gradient overlay
│   │   ├── GlassCard.tsx         # Glassy card component
│   │   └── StatCounter.tsx       # Animated stat counter
│   └── ThemePreview.tsx      # Theme testing component
├── context/
│   └── PlayerDataProvider.tsx  # Global state + theme application
├── lib/
│   ├── types.ts              # TypeScript types
│   ├── rank-utils.ts         # Rank conversion utilities
│   ├── avatar-utils.ts       # Avatar fallback logic
│   ├── personalization.ts    # Persona theming
│   └── theme-utils.ts        # Theme application utilities
├── styles/
│   └── tokens.css            # Theme CSS variables
└── data/
    └── mock-player-data.json # Demo profiles with season data
\`\`\`

## 🎨 Design System

### Colors

\`\`\`css
/* Base (consistent across themes) */
--bg-900: #0b0c10;           /* Dark background */
--bg-800: #121318;           /* Card background */
--glass: rgba(255, 255, 255, 0.04);
--muted-gray: #9aa0a6;       /* Secondary text */

/* Theme-specific (changes with persona) */
--accent-primary: [varies]   /* Main accent color */
--accent-secondary: [varies] /* Lighter variant */
--accent-highlight: [varies] /* Brightest variant */
\`\`\`

### Typography

- **Headings**: Bold, white text
- **Body**: Muted gray for secondary text
- **Stats**: Large, animated counters

## 🔧 Tech Stack

- **Framework**: Next.js 16 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS v4
- **Animation**: Framer Motion
- **Charts**: Recharts
- **State**: React Context API
- **Export**: html2canvas
- **Theming**: CSS Variables + Data Attributes

## 📊 Mock Data Structure

Each demo profile includes:

\`\`\`json
{
  "personality": "Mid-Game Maestro",
  "seasonMonths": ["2024-01", "2024-02", ..., "2024-12"],
  "rankTimeline": ["Silver", "Silver", "Gold", ..., "Diamond"],
  "rankEvents": {
    "2024-06": {
      "message": "Hot streak — wrapped up a 6-game win streak",
      "champion": "Ahri",
      "effect": "win"
    }
  }
}
\`\`\`

## 🎯 Demo Checklist

Test these features:

- [ ] Enter `demo1` → loads Jeevi with gold accent
- [ ] Dashboard shows Season Performance Trends chart
- [ ] Chart displays 12 months of rank progression
- [ ] Hover any point → annotation appears with event message
- [ ] Click a point → annotation pins (click again to unpin)
- [ ] Try `demo2` → blue accent, different rank progression
- [ ] Try `demo3` → red accent, Grandmaster climb
- [ ] Avatar displays with placeholder image
- [ ] Vignette overlay matches persona color
- [ ] Share button navigates to share page
- [ ] Visit `/theme-preview` → see all themes side-by-side
- [ ] Switch themes → entire UI updates instantly

## 🚀 Deployment

Deploy to Vercel:

\`\`\`bash
vercel deploy
\`\`\`

Or build for production:

\`\`\`bash
npm run build
npm start
\`\`\`

## 🐛 Debug Logging

Console logs prefixed with `[v0]` show:
- Demo matching logic
- Persona theme application
- Chart data processing
- Theme switching events

Remove these in production by searching for `console.log("[v0]"` or `console.debug("[v0]"`.

## 📝 Future Enhancements

- [ ] Real Riot API integration
- [ ] More demo profiles
- [ ] Match history timeline
- [ ] Champion mastery details
- [ ] Social sharing
- [ ] Live match analysis
- [ ] Additional persona themes
- [ ] User-customizable color schemes

## 📄 License

MIT

---

**Built with v0.app** — Showcasing interactive data visualization with Recharts, Framer Motion, and dynamic theming
