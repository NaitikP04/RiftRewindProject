import html2canvas from "html2canvas"

/**
 * Utility for exporting DOM elements as images
 */

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
