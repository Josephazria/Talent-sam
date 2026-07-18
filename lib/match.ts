"use client";

import { supabase } from "./supabase";

export interface Match {
  id: string;
  venue_id: string;
  user_a: string;
  user_b: string;
  role_signe: string; // id de la personne qui fait le signe
  signe: string;
  phrase: string;
  reponse: string;
  created_at: string;
  expires_at: string;
  annule: boolean;
}

// Cherche/retourne le match de l'utilisateur.
// La fonction serveur renvoie un match existant, en crée un si une personne
// compatible attend dans le même lieu, ou renvoie null.
export async function tickMatch(): Promise<Match | null> {
  const { data, error } = await supabase.rpc("tick_match");
  if (error || !data) return null;
  return data as Match;
}

export async function annulerMatch(id: string): Promise<void> {
  await supabase.from("matches").update({ annule: true }).eq("id", id);
}

export async function monUserId(): Promise<string | null> {
  const {
    data: { user },
  } = await supabase.auth.getUser();
  return user?.id ?? null;
}
