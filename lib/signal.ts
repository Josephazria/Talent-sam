"use client";

import { supabase } from "./supabase";

export interface Signal {
  id: string;
  venue_id: string;
  venue_name: string;
  expires_at: string;
}

export const DUREE_MIN = 30;

// Signal actif de l'utilisateur, ou null. Si le signal est expiré, il est
// supprimé immédiatement (promesse « sans trace »).
export async function getMySignal(): Promise<Signal | null> {
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) return null;
  const { data } = await supabase
    .from("signals")
    .select("id, venue_id, venue_name, expires_at")
    .eq("user_id", user.id)
    .maybeSingle();
  if (!data) return null;
  if (new Date(data.expires_at).getTime() <= Date.now()) {
    await supabase.from("signals").delete().eq("user_id", user.id);
    return null;
  }
  return data as Signal;
}

// Active (ou remplace) le signal de l'utilisateur pour 30 minutes.
export async function createSignal(
  venue_id: string,
  venue_name: string,
  lat: number | null,
  lng: number | null
): Promise<{ error: string | null }> {
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) return { error: "non_connecte" };
  const expires_at = new Date(Date.now() + DUREE_MIN * 60 * 1000).toISOString();
  const { error } = await supabase.from("signals").upsert(
    {
      user_id: user.id,
      venue_id,
      venue_name,
      lat,
      lng,
      created_at: new Date().toISOString(),
      expires_at,
    },
    { onConflict: "user_id" }
  );
  return { error: error ? error.message : null };
}

// Supprime le signal (annulation ou expiration) — aucune trace conservée.
export async function deleteMySignal(): Promise<void> {
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) return;
  await supabase.from("signals").delete().eq("user_id", user.id);
}
