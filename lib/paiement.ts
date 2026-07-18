"use client";

import { supabase } from "./supabase";

export interface Pack {
  id: string;
  credits: number;
  prix: string;
}

// Doit rester cohérent avec les montants côté serveur (api/stripe/checkout).
export const PACKS: Pack[] = [
  { id: "p5", credits: 5, prix: "4,99 €" },
  { id: "p15", credits: 15, prix: "9,99 €" },
];

export async function acheterCredits(
  packId: string
): Promise<{ url?: string; error?: string }> {
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) return { error: "Connectez-vous d'abord." };
  try {
    const res = await fetch("/api/stripe/checkout", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ packId, userId: user.id }),
    });
    if (!res.ok) {
      const j = await res.json().catch(() => ({}));
      return { error: j.error ?? "Paiement indisponible pour l'instant." };
    }
    const j = await res.json();
    return { url: j.url };
  } catch {
    return { error: "Paiement indisponible pour l'instant." };
  }
}
