import { ClerkProvider } from "@clerk/nextjs";
import { Inter } from "next/font/google";
import "./globals.css";
import "./responsive.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata = {
  title: "Vana AI | Resort & Booking Assistant",
  description:
    "Find the best resorts, plan trips, and book your stay in Dandeli with our smart AI assistant.",
  keywords:
    "Dandeli resorts, book Dandeli trips, Dandeli tourism, Vana AI, Dandeli travel agent, best resorts in Dandeli",
  icons: {
    icon: "/assets/logo.png",
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
