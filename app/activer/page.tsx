"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { BackIcon } from "@/components/Icons";
import MatchActif from "@/components/MatchActif";
import { fetchMyProfile } from "@/lib/profile";
import {
  getMySignal,
  createSignal,
  deleteMySignal,
  type Signal,
} from "@/lib/signal";
import {
  tickMatch,
  annulerMatch,
  monUserId,
  type Match,
} from "@/lib/match";
import styles from "./activer.module.css";

type Lieu = { id: string; nom: string; type: string; lat: number; lng: number };
type Etat =
  | "chargement"
  | "pret"
  | "localisation"
  | "confirmation"
  | "aucun_lieu"
  | "refus"
  | "actif"
  | "match"
  | "termine";

// Écrans 5, 6 et 7 — confirmation du lieu, signal actif, match.
export default function Activer() {
  const router = useRouter();
  const [etat, setEtat] = useState<Etat>("chargement");
  const [lieux, setLieux] = useState<Lieu[]>([]);
  const [choix, setChoix] = useState(0);
  const [signal, setSignal] = useState<Signal | null>(null);
  const [match, setMatch] = useState<Match | null>(null);
  const [myId, setMyId] = useState<string>("");
  const [occupe, setOccupe] = useState(false);

  useEffect(() => {
    let actif = true;
    (async () => {
      const profil = await fetchMyProfile();
      if (!actif) return;
      if (!profil) {
        router.replace("/compte");
        return;
      }
      const id = await monUserId();
      if (actif && id) setMyId(id);

      // Déjà en match ?
      const m = await tickMatch();
      if (!actif) return;
      if (m) {
        setMatch(m);
        setEtat("match");
        return;
      }
      // Signal déjà actif ?
      const s = await getMySignal();
      if (!actif) return;
      if (s) {
        setSignal(s);
        setEtat("actif");
      } else {
        setEtat("pret");
      }
    })();
    return () => {
      actif = false;
    };
  }, [router]);

  // Lit la position UNE seule fois, puis cherche le lieu.
  const activer = useCallback(() => {
    if (!("geolocation" in navigator)) {
      setEtat("refus");
      return;
    }
    setEtat("localisation");
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        try {
          const { latitude, longitude } = pos.coords;
          const res = await fetch(`/api/lieux?lat=${latitude}&lng=${longitude}`);
          const data = (await res.json()) as { lieux: Lieu[] };
          if (data.lieux && data.lieux.length > 0) {
            setLieux(data.lieux);
            setChoix(0);
            setEtat("confirmation");
          } else {
            setEtat("aucun_lieu");
          }
        } catch {
          setEtat("aucun_lieu");
        }
      },
      () => setEtat("refus"),
      { enableHighAccuracy: true, timeout: 12000, maximumAge: 0 }
    );
  }, []);

  async function confirmer() {
    const lieu = lieux[choix];
    if (!lieu || occupe) return;
    setOccupe(true);
    const { error } = await createSignal(lieu.id, lieu.nom, lieu.lat, lieu.lng);
    if (error) {
      setOccupe(false);
      return;
    }
    // Tente un match immédiat, sinon signal en attente.
    const m = await tickMatch();
    const s = await getMySignal();
    setOccupe(false);
    if (m) {
      setMatch(m);
      setEtat("match");
    } else if (s) {
      setSignal(s);
      setEtat("actif");
    }
  }

  function onMatch(m: Match) {
    setMatch(m);
    setSignal(null);
    setEtat("match");
  }

  async function annulerSignal() {
    setOccupe(true);
    await deleteMySignal();
    setSignal(null);
    setOccupe(false);
    router.push("/");
  }

  async function annulerLeMatch() {
    if (!match) return;
    setOccupe(true);
    await annulerMatch(match.id);
    setMatch(null);
    setOccupe(false);
    router.push("/");
  }

  return (
    <>
      {(etat === "pret" ||
        etat === "confirmation" ||
        etat === "aucun_lieu" ||
        etat === "refus") && (
        <Link href="/" className="corner corner--left" aria-label="Retour">
          <BackIcon />
        </Link>
      )}

      <main className="screen screen--center">
        {etat === "chargement" && <p className="muted">un instant…</p>}

        {etat === "pret" && (
          <div className={styles.bloc}>
            <h1 className="title">activer mon signal</h1>
            <p className="subtitle mt-2">
              Vous êtes sur place. Nod va reconnaître le lieu, une seule fois.
            </p>
            <button className="btn btn--primary btn--block mt-4" onClick={activer}>
              activer mon signal
            </button>
            <Link href="/evenement" className="link mt-3">
              événement privé ?
            </Link>
          </div>
        )}

        {etat === "localisation" && (
          <div className={styles.bloc}>
            <div className={styles.pulse} aria-hidden="true">
              <span className={styles.ring} />
              <span className={styles.ring} />
              <span className={styles.ring} />
            </div>
            <p className="subtitle mt-3">recherche du lieu…</p>
          </div>
        )}

        {etat === "confirmation" && lieux.length > 0 && (
          <div className={styles.bloc}>
            <p className="eyebrow">confirmation</p>
            <h1 className="title mt-2">vous êtes bien au {lieux[choix].nom} ?</h1>
            <p className="subtitle mt-2">{lieux[choix].type}</p>
            <button
              className="btn btn--primary btn--block mt-4"
              onClick={confirmer}
              disabled={occupe}
              style={{ opacity: occupe ? 0.5 : 1 }}
            >
              {occupe ? "activation…" : "oui, activer mon signal"}
            </button>

            {lieux.length > 1 && (
              <div className={styles.alternatives}>
                <p className="muted" style={{ fontSize: "0.95rem" }}>
                  un autre lieu ?
                </p>
                {lieux.map((l, i) =>
                  i === choix ? null : (
                    <button
                      key={l.id}
                      className={styles.alt}
                      onClick={() => setChoix(i)}
                    >
                      {l.nom}
                    </button>
                  )
                )}
              </div>
            )}

            <Link href="/evenement" className="link mt-3">
              événement privé ?
            </Link>
          </div>
        )}

        {etat === "aucun_lieu" && (
          <div className={styles.bloc}>
            <p className="eyebrow">aucun lieu détecté</p>
            <hr className="rule" />
            <p className="subtitle" style={{ maxWidth: 300 }}>
              Vous êtes peut-être dans un événement privé.
            </p>
            <Link href="/evenement" className="btn btn--primary btn--block mt-3">
              rejoindre par un code
            </Link>
          </div>
        )}

        {etat === "refus" && (
          <div className={styles.bloc}>
            <p className="eyebrow">localisation nécessaire</p>
            <hr className="rule" />
            <p className="subtitle" style={{ maxWidth: 300 }}>
              Nod a besoin de votre position, une seule fois, pour reconnaître le
              lieu. Autorisez-la puis réessayez.
            </p>
            <button className="btn btn--primary btn--block mt-3" onClick={activer}>
              réessayer
            </button>
            <Link href="/evenement" className="link mt-3">
              événement privé ?
            </Link>
          </div>
        )}

        {etat === "actif" && signal && (
          <SignalActif
            signal={signal}
            occupe={occupe}
            onAnnuler={annulerSignal}
            onMatch={onMatch}
            onExpire={() => {
              setSignal(null);
              setEtat("termine");
            }}
          />
        )}

        {etat === "match" && match && myId && (
          <MatchActif
            match={match}
            myId={myId}
            occupe={occupe}
            onAnnuler={annulerLeMatch}
            onExpire={() => {
              setMatch(null);
              setEtat("termine");
            }}
          />
        )}

        {etat === "termine" && (
          <div className={styles.bloc}>
            <p className="eyebrow">signal terminé</p>
            <hr className="rule" />
            <button
              className="btn btn--primary btn--block mt-3"
              onClick={() => router.push("/")}
            >
              retour à l'accueil
            </button>
          </div>
        )}
      </main>
    </>
  );
}

function SignalActif({
  signal,
  occupe,
  onAnnuler,
  onMatch,
  onExpire,
}: {
  signal: Signal;
  occupe: boolean;
  onAnnuler: () => void;
  onMatch: (m: Match) => void;
  onExpire: () => void;
}) {
  const [reste, setReste] = useState(() =>
    Math.max(
      0,
      Math.floor((new Date(signal.expires_at).getTime() - Date.now()) / 1000)
    )
  );
  const expireRef = useRef(onExpire);
  expireRef.current = onExpire;
  const matchRef = useRef(onMatch);
  matchRef.current = onMatch;

  // Compte à rebours
  useEffect(() => {
    const id = setInterval(() => {
      const s = Math.max(
        0,
        Math.floor((new Date(signal.expires_at).getTime() - Date.now()) / 1000)
      );
      setReste(s);
      if (s <= 0) {
        clearInterval(id);
        expireRef.current();
      }
    }, 1000);
    return () => clearInterval(id);
  }, [signal.expires_at]);

  // Vérifie régulièrement si une rencontre se forme.
  useEffect(() => {
    let vivant = true;
    const id = setInterval(async () => {
      const m = await tickMatch();
      if (vivant && m) {
        clearInterval(id);
        matchRef.current(m);
      }
    }, 4000);
    return () => {
      vivant = false;
      clearInterval(id);
    };
  }, []);

  const mm = String(Math.floor(reste / 60)).padStart(2, "0");
  const ss = String(reste % 60).padStart(2, "0");

  return (
    <div className={styles.bloc}>
      <div className={styles.pulse}>
        <span className={styles.ring} />
        <span className={styles.ring} />
        <span className={styles.ring} />
        <span className={styles.count}>
          {mm}:{ss}
        </span>
      </div>
      <p className={styles.venue}>{signal.venue_name}</p>
      <p className="muted mt-2">en attente d'un match</p>
      <button className="btn btn--ghost mt-4" onClick={onAnnuler} disabled={occupe}>
        annuler
      </button>
    </div>
  );
}
