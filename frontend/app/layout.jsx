import { ClerkProvider } from '@clerk/nextjs'
import { Inter } from 'next/font/google'
import "./globals.css";

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
});
export const metadata = {
  title: "Vana AI | Resort & Booking Assistant",
  description: "Find the best resorts, plan trips, and book your stay in Dandeli with our smart AI assistant.",
  keywords: "Dandeli resorts, book Dandeli trips, Dandeli tourism, Vana AI, Dandeli travel agent, best resorts in Dandeli",
  icons: {
    icon: "/assets/logo.png",
  },
};



export default function RootLayout({ children }) {
  return (
    <ClerkProvider>
      <html lang="en">
        <body className={`${inter.variable}`}>{children}</body>
      </html>
    </ClerkProvider>
  );
}
