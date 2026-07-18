"use client";

import dynamic from "next/dynamic";

// La carte utilise Leaflet (besoin du navigateur) : chargement côté client.
const CarteMap = dynamic(() => import("@/components/CarteMap"), {
  ssr: false,
  loading: () => (
    <main className="screen screen--center">
      <p className="muted">chargement de la carte…</p>
    </main>
  ),
});

// Écran 3 — Carte (consultable sans compte).
export default function Carte() {
  return <CarteMap />;
}
