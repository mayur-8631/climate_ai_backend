import type { Metadata } from "next";
import "./globals.css";
import { ClimateProvider } from "@/context/ClimateContext";

export const metadata: Metadata = {
  title: "ClimateTwin AI — Predict. Assess. Protect.",
  description:
    "Localized climate-intelligence and multi-hazard digital twin web platform. Developed by Team PrithviNex for PCCOE International Grand Challenge 2026.",
  keywords: [
    "ClimateTwin AI",
    "Climate Intelligence",
    "Multi-Hazard Risk Engine",
    "Digital Twin",
    "PCCOE Grand Challenge 2026",
    "Heatwave",
    "Flood Risk",
    "Air Quality AQI",
    "Water Stress",
  ],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark h-full antialiased">
      <head>
        <link rel="icon" href="/favicon.ico" sizes="any" />
        <link rel="stylesheet" href="/leaflet.css" />
      </head>
      <body className="min-h-full flex flex-col bg-[#071827] text-slate-100">
        <ClimateProvider>
          {children}
        </ClimateProvider>
      </body>
    </html>
  );
}
