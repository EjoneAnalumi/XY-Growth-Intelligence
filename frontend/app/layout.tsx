import type { Metadata } from "next";

import "./globals.css";

export const metadata: Metadata = {
  title: "XY CYBER Growth Intelligence",
  description: "Internal Growth Intelligence MVP"
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
