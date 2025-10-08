export const metadata = {
  title: 'Rift Review - AI Year-End Review',
  description: 'Get your personalized League of Legends Year-End Review powered by AI',
}

import './globals.css'

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="bg-gray-900 text-white min-h-screen antialiased">
        {children}
      </body>
    </html>
  )
}
