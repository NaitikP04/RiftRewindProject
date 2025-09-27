export const metadata = {
  title: 'Rift Rewind - League Match Tracker',
  description: 'Track your recent League of Legends matches using Riot Games API',
}

import './globals.css'

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="bg-gray-900 text-white min-h-screen">{children}</body>
    </html>
  )
}
