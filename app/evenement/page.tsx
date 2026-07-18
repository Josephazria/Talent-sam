"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import QRCode from "qrcode";
import { BackIcon } from "@/components/Icons";
import { fetchMyProfile } from "@/lib/profile";
import { activerSignal } from "@/lib/signal";
import { activerNotifications } from "@/lib/push";
import styles from "./evenement.module.css";

// Écran 5 — Codes événement (venue virtuel).
// Repli discret quand aucun lieu n'est détectable : créer ou rejoindre un
// code à 6 caractères. Le signal s'active alors dans ce lieu virtuel.
type Etat = "chargement" | "menu" | "creer" | "rejoindre";

// Alphabet sans caractères ambigus (ni O/0, ni I/1).
const ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";

function genererCode(): string {
  const a = new Uint32Array(6);
  crypto.getRandomValues(a);
  return Array.from(a, (n) => ALPHABET[n % ALPHABET.length]).join("");
}

export default function Evenement() {
  const router = useRouter();
  const [etat, setEtat] = useState<Etat>("chargement");
  const [code, setCode] = useState("");
  const [saisie, setSaisie] = useState("");
  const [qr, setQr] = useState<string | null>(null);
  const [occupe, setOccupe] = useState(false);
  const [erreur, setErreur] = useState<string | null>(null);

  useEffect(() => {
    let actif = true;
    (async () => {
      const profil = await fetchMyProfile();
      if (!actif) return;
      if (!profil) {
        router.replace("/compte");
        return;
      }
      // Rejoindre directement via un lien QR (?code=XXXXXX)
      const depuisLien = new URLSearchParams(window.location.search)
        .get("code")
        ?.toUpperCase()
        .slice(0, 6);
      if (depuisLien && depuisLien.length === 6) {
        setSaisie(depuisLien);
        setEtat("rejoindre");
      } else {
        setEtat("menu");
      }
    })();
    return () => {
      actif = false;
    };
  }, [router]);

  // Génère un code + son QR à l'entrée dans « créer ».
  const creer = useCallback(async () => {
    const c = genererCode();
    setCode(c);
    setEtat("creer");
    try {
      const url = `${window.location.origin}/evenement?code=${c}`;
      const data = await QRCode.toDataURL(url, {
        margin: 1,
        width: 240,
        color: { dark: "#250810", light: "#efe6d6" },
      });
      setQr(data);
    } catch {
      setQr(null);
    }
  }, []);

  async function activer(codeEvenement: string) {
    if (occupe) return;
    void activerNotifications();
    setErreur(null);
    setOccupe(true);
    const statut = await activerSignal(
      `event:${codeEvenement}`,
      `Événement · ${codeEvenement}`,
      null,
      null
    );
    setOccupe(false);
    if (statut === "paywall") {
      router.push("/paywall");
      return;
    }
    if (statut !== "ok") {
      setErreur("Activation impossible. Réessayez.");
      return;
    }
    router.push("/activer");
  }

  function retour() {
    if (etat === "menu" || etat === "chargement") router.push("/");
    else setEtat("menu");
  }

  return (
    <>
      <button onClick={retour} className="corner corner--left" aria-label="Retour">
        <BackIcon />
      </button>

      <main className="screen screen--center">
        {etat === "chargement" && <p className="muted">un instant…</p>}

        {etat === "menu" && (
          <div className={styles.bloc}>
            <h1 className="title">événement privé</h1>
            <p className="subtitle mt-2">
              Un lieu sans adresse ? Créez un code, ou rejoignez celui d'un
              organisateur.
            </p>
            <button
              className="btn btn--primary btn--block mt-4"
              onClick={creer}
            >
              créer un événement
            </button>
            <button
              className="btn btn--primary btn--block mt-2"
              onClick={() => setEtat("rejoindre")}
            >
              rejoindre un événement
            </button>
          </div>
        )}

        {etat === "creer" && (
          <div className={styles.bloc}>
            <p className="eyebrow">votre code</p>
            <p className={styles.code}>{code}</p>
            {qr && (
              /* eslint-disable-next-line @next/next/no-img-element */
              <img src={qr} alt="QR code de l'événement" className={styles.qr} />
            )}
            <p className="muted" style={{ fontSize: "0.95rem" }}>
              Partagez ce code ou ce QR. Il reste valable 24 h.
            </p>
            {erreur && <p className={styles.erreur}>{erreur}</p>}
            <button
              className="btn btn--primary btn--block mt-3"
              onClick={() => activer(code)}
              disabled={occupe}
              style={{ opacity: occupe ? 0.5 : 1 }}
            >
              {occupe ? "activation…" : "activer mon signal ici"}
            </button>
          </div>
        )}

        {etat === "rejoindre" && (
          <div className={styles.bloc}>
            <h1 className="title">rejoindre</h1>
            <p className="subtitle mt-2">Entrez le code à 6 caractères.</p>
            <input
              className={styles.input}
              value={saisie}
              onChange={(e) =>
                setSaisie(
                  e.target.value.toUpperCase().replace(/[^A-Z0-9]/g, "").slice(0, 6)
                )
              }
              placeholder="ABC234"
              inputMode="text"
              autoCapitalize="characters"
              autoComplete="off"
              aria-label="Code de l'événement"
            />
            {erreur && <p className={styles.erreur}>{erreur}</p>}
            <button
              className="btn btn--primary btn--block mt-3"
              onClick={() => activer(saisie)}
              disabled={occupe || saisie.length !== 6}
              style={{ opacity: occupe || saisie.length !== 6 ? 0.5 : 1 }}
            >
              {occupe ? "activation…" : "activer mon signal ici"}
            </button>
          </div>
        )}
      </main>
    </>
  );
}
