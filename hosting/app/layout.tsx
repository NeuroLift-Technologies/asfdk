import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Agent Solidarity Kit — NeuroLift Technologies",
  description:
    "The unified agent development framework — the layer between the model and the agent. Combines RRT Advocate, NLT-OTOI, and Sleepwalker Protocol.",
  keywords: [
    "AI",
    "agent framework",
    "NeuroLift Technologies",
    "RRT Advocate",
    "NLT-OTOI",
    "Sleepwalker Protocol",
    "governance",
  ],
  openGraph: {
    title: "Agent Solidarity Kit — NeuroLift Technologies",
    description:
      "The unified agent development framework — the layer between the model and the agent.",
    url: "https://neurolift-technologies.github.io/solidarity-framework/",
    siteName: "NeuroLift Technologies",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body style={{ margin: 0, padding: 0, fontFamily: "system-ui, -apple-system, sans-serif" }}>
        {children}
      </body>
    </html>
  );
}
