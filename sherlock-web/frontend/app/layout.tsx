export const metadata = {
  title: 'Sherlock',
  description: 'Find your username in many websites.',
}

import "../node_modules/reset-css/reset.css";
import "./global.css";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        <title>Sherlock</title>
      </head>
      <body>{children}</body>
    </html>
  )
}
