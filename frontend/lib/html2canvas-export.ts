import html2canvas from "html2canvas"

/**
 * Utility for exporting DOM elements as images
 */

const FALLBACK_THEME_STYLES = `
:root {
  --foreground: #e9edf0;
  --card-foreground: #e9edf0;
  --popover-foreground: #e9edf0;
  --primary-foreground: #0b0c10;
  --secondary-foreground: #e9edf0;
  --accent-foreground: #0b0c10;
  --destructive-foreground: #0b0c10;
  --sidebar: #f5f7fa;
  --sidebar-foreground: #121318;
  --sidebar-primary: #d9e3ff;
  --sidebar-primary-foreground: #121318;
  --sidebar-accent: #eef3ff;
  --sidebar-accent-foreground: #1b66ff;
  --sidebar-border: #d1d5db;
  --sidebar-ring: #9aa0a6;
  --accent-primary-dark: #614921;
  --accent-primary-light: #f4d9a3;
}
.dark {
  --background: #0b0c10;
  --foreground: #e9edf0;
  --card: #121318;
  --card-foreground: #e9edf0;
  --popover: #121318;
  --popover-foreground: #e9edf0;
  --primary: #c5a35e;
  --primary-foreground: #0b0c10;
  --secondary: #1a1f26;
  --secondary-foreground: #e9edf0;
  --muted: #1a1f26;
  --muted-foreground: #9aa0a6;
  --accent: #1b66ff;
  --accent-foreground: #0b0c10;
  --destructive: #e94560;
  --destructive-foreground: #0b0c10;
  --border: #1f2530;
  --input: #1f2530;
  --ring: #c5a35e;
  --chart-1: #1b66ff;
  --chart-2: #c5a35e;
  --chart-3: #e94560;
  --chart-4: #6b48ff;
  --chart-5: #00d9ff;
  --sidebar: #121318;
  --sidebar-foreground: #e9edf0;
  --sidebar-primary: #1b66ff;
  --sidebar-primary-foreground: #0b0c10;
  --sidebar-accent: #1a1f26;
  --sidebar-accent-foreground: #e9edf0;
  --sidebar-border: #1f2530;
  --sidebar-ring: #c5a35e;
}
`

export async function exportToImage(elementId: string, filename = "riftreview-stats.png"): Promise<void> {
  const element = document.getElementById(elementId)

  if (!element) {
    throw new Error(`Element with id "${elementId}" not found`)
  }

  try {
    const canvas = await html2canvas(element, {
      backgroundColor: "#0b0c10",
      scale: 2,
      logging: false,
      useCORS: true,
      onclone: (clonedDocument) => {
        const fallbackStyle = clonedDocument.createElement("style")
        fallbackStyle.setAttribute("data-html2canvas-theme", "true")
        fallbackStyle.textContent = FALLBACK_THEME_STYLES
        clonedDocument.head.appendChild(fallbackStyle)
      },
    })

    // Convert to blob and download
    canvas.toBlob((blob) => {
      if (blob) {
        const url = URL.createObjectURL(blob)
        const link = document.createElement("a")
        link.href = url
        link.download = filename
        link.click()
        URL.revokeObjectURL(url)
      }
    })
  } catch (error) {
    console.error("Failed to export image:", error)
    throw error
  }
}
