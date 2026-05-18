/* Root layout for the Next.js frontend application. */
/* File: frontend/app/layout.jsx */


import { ClerkProvider } from "@clerk/nextjs";
import { Inter } from "next/font/google";
import "./globals.css";
import "./responsive.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata = {
  title: "WayFind | AI Travel Assistant",
  description:
    "Find the best resorts, plan trips, and book your stay with WayFind - your intelligent AI travel assistant.",
  keywords:
    "travel assistant, resort booking, trip planning, AI travel, find resorts, travel agent, best resorts",
  icons: {
    icon: "/assets/Gemini_Generated_Image.png",
  },
  viewport: {
    width: "device-width",
    initialScale: 1,
    maximumScale: 5,
    minimumScale: 1,
  },
};

export default function RootLayout({ children }) {
  return (
    <ClerkProvider>
      <html lang="en">
        <head>
          <meta
            name="viewport"
            content="width=device-width, initial-scale=1, maximum-scale=5, minimum-scale=1"
          />
          <meta name="theme-color" content="#047857" />
          <meta name="apple-mobile-web-app-capable" content="yes" />
          <meta
            name="apple-mobile-web-app-status-bar-style"
            content="black-translucent"
          />
        </head>
        <body className={`${inter.variable}`}>{children}</body>
      </html>
    </ClerkProvider>
  );
}