// Stockage temporaire du profil côté navigateur (localStorage).
// Sera remplacé par Supabase (base de données) une fois l'authentification
// branchée. L'interface reste la même pour faciliter la bascule.

export type Genre = "femme" | "homme" | "autre";
export type Recherche = "femmes" | "hommes" | "les_deux";

export interface Profile {
  naissance: string; // date ISO "AAAA-MM-JJ"
  genre: Genre;
  recherche: Recherche;
}

const KEY = "nod_profile";

export function getProfile(): Profile | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.localStorage.getItem(KEY);
    return raw ? (JSON.parse(raw) as Profile) : null;
  } catch {
    return null;
  }
}

export function saveProfile(p: Profile): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(KEY, JSON.stringify(p));
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
