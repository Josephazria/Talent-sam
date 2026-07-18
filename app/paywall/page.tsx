"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { BackIcon } from "@/components/Icons";
import { acheterCredits, PACKS } from "@/lib/paiement";
import styles from "./paywall.module.css";

// Écran 9 — Paywall. N'apparaît qu'au moment où un utilisateur à 0 crédit
// tente d'activer. Sobre : prix, achat, retour immédiat au flow.
export default function Paywall() {
  const router = useRouter();
  const [occupe, setOccupe] = useState<string | null>(null);
  const [erreur, setErreur] = useState<string | null>(null);

  async function acheter(packId: string) {
    setErreur(null);
    setOccupe(packId);
    const r = await acheterCredits(packId);
    if (r.url) {
      window.location.href = r.url;
    } else {
      setOccupe(null);
      setErreur(r.error ?? "Paiement indisponible pour l'instant.");
    }
  }

  return (
    <>
      <button
        onClick={() => router.back()}
        className="corner corner--left"
        aria-label="Retour"
      >
        <BackIcon />
      </button>

      <main className="screen screen--center">
        <div className={styles.bloc}>
          <p className="eyebrow">signaux épuisés</p>
          <hr className="rule" />
          <p className="subtitle" style={{ maxWidth: 300 }}>
            Rechargez pour continuer à vous signaler.
          </p>

          <div className={styles.packs}>
            {PACKS.map((p) => (
              <button
                key={p.id}
                className={styles.pack}
                onClick={() => acheter(p.id)}
                disabled={!!occupe}
                style={{ opacity: occupe && occupe !== p.id ? 0.4 : 1 }}
              >
                <span className={styles.packN}>{p.credits} signaux</span>
                <span className={styles.packP}>
                  {occupe === p.id ? "…" : p.prix}
                </span>
              </button>
            ))}
          </div>

          {erreur && <p className={styles.err}>{erreur}</p>}
        </div>
      </main>
    </>
  );
}
