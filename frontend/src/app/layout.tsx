import './globals.css'
import type { Metadata } from 'next'
import { Archivo, JetBrains_Mono } from 'next/font/google'

const archivo = Archivo({
  subsets: ['latin'],
  weight: ['400', '500', '600', '700', '800', '900'],
  variable: '--font-archivo',
})

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  weight: ['400', '500', '700'],
  variable: '--font-mono',
})

export const metadata: Metadata = {
  title: 'Shiny Fishstick — Website to API Compiler',
  description: 'Compile human-centric websites into semantic SDKs and MCP servers for AI agents.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={`h-full ${archivo.variable} ${jetbrainsMono.variable}`}>
      <body className="h-full flex flex-col">{children}</body>
    </html>
  )
}