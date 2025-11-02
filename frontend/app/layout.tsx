import type React from "react"
import type { Metadata } from "next"
import { Inter } from "next/font/google"
import { Analytics } from "@vercel/analytics/next"
import { PlayerDataProvider } from "@/context/PlayerDataProvider"
import "./globals.css"

const inter = Inter({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700", "800"],
  variable: "--font-sans",
})

export const metadata: Metadata = {
  title: "RiftReview — AI Game Coach & Analyzer",
  description: "Elevate your League of Legends gameplay with AI-powered insights and analytics",
  generator: "v0.app",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.variable} font-sans antialiased`}>
        <PlayerDataProvider>{children}</PlayerDataProvider>
        <Analytics />
      </body>
    </html>
  )
}
