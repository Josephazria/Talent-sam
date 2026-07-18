import { NextResponse } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

// Détection de lieux via OpenStreetMap (Overpass). Gratuit, sans clé.
// Renvoie les bars / clubs / cafés / restaurants proches d'une position,
// triés du plus proche au plus lointain.

type Lieu = {
  id: string;
  nom: string;
  type: string;
  lat: number;
  lng: number;
  distance: number; // mètres
};

const TYPES = "bar|pub|nightclub|cafe|restaurant|biergarten|events_venue";

function distanceM(
  lat1: number,
  lng1: number,
  lat2: number,
  lng2: number
): number {
  const R = 6371000;
  const toRad = (d: number) => (d * Math.PI) / 180;
  const dLat = toRad(lat2 - lat1);
  const dLng = toRad(lng2 - lng1);
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLng / 2) ** 2;
  return Math.round(R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a)));
}

function libelleType(amenity: string): string {
  const map: Record<string, string> = {
    bar: "bar",
    pub: "pub",
    nightclub: "club",
    cafe: "café",
    restaurant: "restaurant",
    biergarten: "bar",
    events_venue: "lieu d'événement",
  };
  return map[amenity] ?? "lieu";
}

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const lat = parseFloat(searchParams.get("lat") ?? "");
  const lng = parseFloat(searchParams.get("lng") ?? "");
  if (!isFinite(lat) || !isFinite(lng)) {
    return NextResponse.json({ error: "position invalide" }, { status: 400 });
  }

  const query = `[out:json][timeout:20];
(
  node["amenity"~"^(${TYPES})$"](around:200,${lat},${lng});
  way["amenity"~"^(${TYPES})$"](around:200,${lat},${lng});
);
out center tags 40;`;

  try {
    const res = await fetch("https://overpass-api.de/api/interpreter", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "nod-app/1.0 (venue detection)",
      },
      body: "data=" + encodeURIComponent(query),
      cache: "no-store",
    });
    if (!res.ok) throw new Error("overpass " + res.status);
    const data = (await res.json()) as {
      elements: Array<{
        type: string;
        id: number;
        lat?: number;
        lon?: number;
        center?: { lat: number; lon: number };
        tags?: Record<string, string>;
      }>;
    };

    const vus = new Set<string>();
    const lieux: Lieu[] = [];
    for (const el of data.elements ?? []) {
      const nom = el.tags?.name;
      const amenity = el.tags?.amenity;
      if (!nom || !amenity) continue;
      const plat = el.lat ?? el.center?.lat;
      const plng = el.lon ?? el.center?.lon;
      if (plat == null || plng == null) continue;
      const cle = nom.toLowerCase();
      if (vus.has(cle)) continue;
      vus.add(cle);
      lieux.push({
        id: `${el.type}/${el.id}`,
        nom,
        type: libelleType(amenity),
        lat: plat,
        lng: plng,
        distance: distanceM(lat, lng, plat, plng),
      });
    }

    lieux.sort((a, b) => a.distance - b.distance);
    return NextResponse.json({ lieux: lieux.slice(0, 5) });
  } catch {
    // En cas d'échec du service, on renvoie une liste vide : l'app proposera
    // alors le repli « événement privé » (code à 6 caractères, étape 5).
    return NextResponse.json({ lieux: [] });
  }
}
