"use client";

import { supabase } from "./supabase";

// Liste des signes (identique au serveur). Le premier choix « aléatoire »
// correspond à signe = null.
export const SIGNES: string[] = [
  "un verre vide retourné, posé devant vous",
  "un sous-verre posé sur le dessus du verre",
  "le téléphone posé face contre la table",
  "la veste sur une seule épaule",
  "une paille pliée en deux, posée sur la table",
  "une serviette nouée autour du poignet",
  "deux verres côte à côte, dont un vide",
  "la montre portée cadran côté paume",
];

export const PHRASE_DEFAUT = "La soirée vous plaît ?";
export const REPONSE_DEFAUT = "Davantage à l'instant.";

export interface ProfilComplet {
  email: string;
  genre: string;
  recherche: string;
  signe: string | null;
  phrase: string | null;
  reponse: string | null;
  credits: number;
  illimite: boolean;
}

export async function getProfilComplet(): Promise<ProfilComplet | null> {
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) return null;
  const { data } = await supabase
    .from("profiles")
    .select("genre, recherche, signe, phrase, reponse, credits")
    .eq("id", user.id)
    .maybeSingle();
  if (!data) return null;
  return {
    email: user.email ?? "",
    genre: data.genre,
    recherche: data.recherche,
    signe: data.signe ?? null,
    phrase: data.phrase ?? null,
    reponse: data.reponse ?? null,
    credits: data.credits ?? 0,
    illimite: data.genre === "femme" || data.genre === "autre",
  };
}

export async function updateProfil(
  genre: string,
  recherche: string
): Promise<void> {
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) return;
  await supabase.from("profiles").update({ genre, recherche }).eq("id", user.id);
}

export async function updateReconnaissance(
  signe: string | null,
  phrase: string | null,
  reponse: string | null
): Promise<void> {
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) return;
  await supabase
    .from("profiles")
    .update({ signe, phrase, reponse })
    .eq("id", user.id);
}

// Bloque la dernière personne rencontrée et annule le match en cours.
export async function bloquerDernierMatch(): Promise<boolean> {
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) return false;
  const { data: m } = await supabase
    .from("matches")
    .select("user_a, user_b")
    .or(`user_a.eq.${user.id},user_b.eq.${user.id}`)
    .order("created_at", { ascending: false })
    .limit(1)
    .maybeSingle();
  if (!m) return false;
  const autre = m.user_a === user.id ? m.user_b : m.user_a;
  await supabase.from("blocks").upsert({ blocker: user.id, blocked: autre });
  await supabase
    .from("matches")
    .update({ annule: true })
    .or(`user_a.eq.${user.id},user_b.eq.${user.id}`)
    .eq("annule", false);
  return true;
}

export async function signaler(message: string): Promise<boolean> {
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) return false;
  const { error } = await supabase
    .from("signalements")
    .insert({ user_id: user.id, message });
  return !error;
}

export async function seDeconnecter(): Promise<void> {
  await supabase.auth.signOut();
}

export async function supprimerCompte(): Promise<boolean> {
  const {
    data: { session },
  } = await supabase.auth.getSession();
  if (!session) return false;
  try {
    const res = await fetch("/api/compte/supprimer", {
      method: "POST",
      headers: { Authorization: `Bearer ${session.access_token}` },
    });
    if (!res.ok) return false;
    await supabase.auth.signOut();
    return true;
  } catch {
    return false;
  }
}
