import { ClerkProvider } from '@clerk/nextjs'
import { Inter } from 'next/font/google'
import "./globals.css";

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
});
export const metadata = {
  title: "Dandeli Travel Workspace",
  description: "A refined travel planning workspace for resort research, itinerary design, and booking follow-up.",
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
