import type { Metadata } from "next";
import { JetBrains_Mono, Space_Mono, Share_Tech_Mono, Fira_Code } from "next/font/google";
import "./globals.css";

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jetbrains",
  weight: ["400", "700"],
});

const spaceMono = Space_Mono({
  subsets: ["latin"],
  variable: "--font-space-mono",
  weight: ["400", "700"],
});

const shareTechMono = Share_Tech_Mono({
  subsets: ["latin"],
  variable: "--font-share-tech",
  weight: "400",
});

const firaCode = Fira_Code({
  subsets: ["latin"],
  variable: "--font-fira-code",
  weight: ["300", "400", "600"],
});

export const metadata: Metadata = {
  title: "TERMINAL_CORE",
  description: "A self-evolving AI arcade. Agents invent, generate, and evolve games.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`dark ${jetbrainsMono.variable} ${spaceMono.variable} ${shareTechMono.variable} ${firaCode.variable}`}
    >
      <body className="min-h-screen flex flex-col bg-bg-dark text-text-primary antialiased selection:bg-primary selection:text-black">
        {children}
      </body>
    </html>
  );
}
