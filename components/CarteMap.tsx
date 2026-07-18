"use client";

import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { BackIcon } from "@/components/Icons";
import { supabase } from "@/lib/supabase";
import styles from "./CarteMap.module.css";

interface Halo {
  venue_id: string;
  venue_name: string;
  lat: number;
  lng: number;
  niveau: string;
  bucket: string;
  tranche: string;
}

// Écran 3 — Carte. Halos dorés sur fond sombre, sans chiffre exact ni profil.
export default function CarteMap() {
  const conteneur = useRef<HTMLDivElement>(null);
  const [sel, setSel] = useState<Halo | null>(null);
  const [vide, setVide] = useState(false);

  useEffect(() => {
    if (!conteneur.current) return;
    const map = L.map(conteneur.current, {
      zoomControl: false,
      attributionControl: true,
    }).setView([48.8566, 2.3522], 13);

    L.tileLayer(
      "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
      {
        subdomains: "abcd",
        maxZoom: 20,
        attribution: "© OpenStreetMap, © CARTO",
      }
    ).addTo(map);

    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (p) => map.setView([p.coords.latitude, p.coords.longitude], 14),
        () => {},
        { timeout: 8000 }
      );
    }

    (async () => {
      const { data } = await supabase.rpc("carte_halos");
      const halos = (data as Halo[]) ?? [];
      if (halos.length === 0) {
        setVide(true);
        return;
      }
      const pts: [number, number][] = [];
      for (const h of halos) {
        const fort = h.niveau === "tres_actif";
        const taille = fort ? 130 : 84;
        const icon = L.divIcon({
          className: "",
          html: `<div class="${styles.halo} ${fort ? styles.haloFort : ""}"></div>`,
          iconSize: [taille, taille],
          iconAnchor: [taille / 2, taille / 2],
        });
        L.marker([h.lat, h.lng], { icon })
          .addTo(map)
          .on("click", () => setSel(h));
        pts.push([h.lat, h.lng]);
      }
      if (pts.length > 0) {
        map.fitBounds(pts, { padding: [70, 70], maxZoom: 15 });
      }
    })();

    return () => {
      map.remove();
    };
  }, []);

  return (
    <>
      <div ref={conteneur} className={styles.map} />
      <Link href="/" className="corner corner--left" aria-label="Retour">
        <BackIcon />
      </Link>

      {vide && (
        <div className={styles.vide}>
          Aucun lieu actif pour l&apos;instant.
          <br />
          La carte s&apos;anime le soir venu.
        </div>
      )}

      {sel && (
        <>
          <div className={styles.overlay} onClick={() => setSel(null)} />
          <div className={styles.sheet}>
            <h2 className={styles.nom}>{sel.venue_name}</h2>
            <p className={styles.agg}>
              {sel.bucket} personnes compatibles actives · {sel.tranche}
            </p>
            <button
              className="btn btn--primary btn--block"
              onClick={() => setSel(null)}
            >
              j&apos;y vais
            </button>
          </div>
        </>
      )}
    </>
  );
}
