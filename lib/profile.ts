// Profil utilisateur, stocké dans Supabase (table profiles).

import { supabase } from "./supabase";

export type Genre = "femme" | "homme" | "autre";
export type Recherche = "femmes" | "hommes" | "les_deux";

export interface Profile {
  naissance: string; // date ISO "AAAA-MM-JJ"
  genre: Genre;
  recherche: Recherche;
}

// Âge révolu à partir d'une date de naissance ISO.
export function ageFromISO(iso: string): number {
  const naissance = new Date(iso + "T00:00:00");
  const aujourdhui = new Date();
  let age = aujourdhui.getFullYear() - naissance.getFullYear();
  const m = aujourdhui.getMonth() - naissance.getMonth();
  if (m < 0 || (m === 0 && aujourdhui.getDate() < naissance.getDate())) {
    age--;
  }
  return age;
}

// Récupère le profil de l'utilisateur connecté, ou null.
export async function fetchMyProfile(): Promise<Profile | null> {
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) return null;
  const { data } = await supabase
    .from("profiles")
    .select("naissance, genre, recherche")
    .eq("id", user.id)
    .maybeSingle();
  return (data as Profile | null) ?? null;
}

// Enregistre (crée ou met à jour) le profil de l'utilisateur connecté.
export async function saveMyProfile(
  p: Profile
): Promise<{ error: string | null }> {
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) return { error: "non_connecte" };
  const { error } = await supabase
    .from("profiles")
    .upsert({ id: user.id, ...p });
  return { error: error ? error.message : null };
}
