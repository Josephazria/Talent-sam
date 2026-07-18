"use client";

import { supabase } from "./supabase";

export interface Signal {
  id: string;
  venue_id: string;
  venue_name: string;
  expires_at: string;
}

export type Statut =
  | "ok"
  | "paywall"
  | "non_connecte"
  | "pas_de_signal"
  | "erreur";

export const DUREE_MIN = 30;

// Signal actif de l'utilisateur, ou null. Un signal expiré est supprimé.
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

// Active un signal en appliquant les règles de crédits (côté serveur).
export async function activerSignal(
  venue_id: string,
  venue_name: string,
  lat: number | null,
  lng: number | null
): Promise<Statut> {
  const { data, error } = await supabase.rpc("activer_signal", {
    p_venue_id: venue_id,
    p_venue_name: venue_name,
    p_lat: lat,
    p_lng: lng,
  });
  if (error) return "erreur";
  return (data as Statut) ?? "erreur";
}

// Prolonge le signal actif de 30 minutes.
export async function prolongerSignal(): Promise<Statut> {
  const { data, error } = await supabase.rpc("prolonger_signal");
  if (error) return "erreur";
  return (data as Statut) ?? "erreur";
}

export async function deleteMySignal(): Promise<void> {
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) return;
  await supabase.from("signals").delete().eq("user_id", user.id);
}

export interface Compte {
  genre: string;
  credits: number;
  signaux_utilises: number;
  illimite: boolean;
}

// Lit le solde de crédits et le statut (femmes/others = illimité).
export async function getMonCompte(): Promise<Compte | null> {
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) return null;
  const { data } = await supabase
    .from("profiles")
    .select("genre, credits, signaux_utilises")
    .eq("id", user.id)
    .maybeSingle();
  if (!data) return null;
  const illimite = data.genre === "femme" || data.genre === "autre";
  return {
    genre: data.genre,
    credits: data.credits ?? 0,
    signaux_utilises: data.signaux_utilises ?? 0,
    illimite,
  };
}
