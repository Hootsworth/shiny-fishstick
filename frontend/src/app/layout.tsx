import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Shiny Fishstick Dashboard',
  description: 'AI-friendly navigation specifications compiler for browser agents.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="h-full">
      <body className="h-full flex flex-col">{children}</body>
    </html>
  )
}
