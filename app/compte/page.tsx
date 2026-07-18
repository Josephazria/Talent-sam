"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { BackIcon } from "@/components/Icons";
import {
  saveProfile,
  ageFromISO,
  type Genre,
  type Recherche,
} from "@/lib/profile";
import styles from "./compte.module.css";

// Écran 4 — Création de compte.
// Ordre imposé : connexion, puis date de naissance (blocage < 18 ans),
// puis genre, puis « je cherche ». Une question par écran.
type Etape = "connexion" | "naissance" | "genre" | "recherche" | "fait";

export default function Compte() {
  const router = useRouter();
  const [etape, setEtape] = useState<Etape>("connexion");
  const [naissance, setNaissance] = useState("");
  const [genre, setGenre] = useState<Genre | null>(null);
  const [recherche, setRecherche] = useState<Recherche | null>(null);

  const age = naissance ? ageFromISO(naissance) : null;
  const mineur = age !== null && age < 18;

  function retour() {
    if (etape === "connexion") router.push("/");
    else if (etape === "naissance") setEtape("connexion");
    else if (etape === "genre") setEtape("naissance");
    else if (etape === "recherche") setEtape("genre");
    else router.push("/");
  }

  function terminer(r: Recherche) {
    setRecherche(r);
    if (naissance && genre) {
      saveProfile({ naissance, genre, recherche: r });
      setEtape("fait");
    }
  }

  return (
    <>
      {etape !== "fait" && (
        <button
          onClick={retour}
          className="corner corner--left"
          aria-label="Retour"
        >
          <BackIcon />
        </button>
      )}

      <main className="screen screen--center">
        {etape !== "connexion" && etape !== "fait" && (
          <Progression etape={etape} />
        )}

        {etape === "connexion" && (
          <div className={styles.step}>
            <h1 className="title">créer mon compte</h1>
            <p className="subtitle mt-2">
              Sans mot de passe. Nécessaire seulement pour activer un signal.
            </p>
            <div className={styles.oauth}>
              <button
                className="btn btn--primary btn--block"
                onClick={() => setEtape("naissance")}
              >
                continuer avec Google
              </button>
              <button
                className="btn btn--primary btn--block"
                onClick={() => setEtape("naissance")}
              >
                continuer avec Apple
              </button>
            </div>
          </div>
        )}

        {etape === "naissance" && (
          <div className={styles.step}>
            <h1 className="title">votre date de naissance</h1>
            <p className="subtitle mt-2">
              Nod est réservé aux personnes majeures.
            </p>
            <input
              type="date"
              className={styles.date}
              value={naissance}
              max="2099-12-31"
              onChange={(e) => setNaissance(e.target.value)}
              aria-label="Date de naissance"
            />
            {mineur ? (
              <p className={styles.block}>nod est réservé aux adultes</p>
            ) : (
              <button
                className="btn btn--primary btn--block mt-3"
                disabled={!naissance}
                style={{ opacity: naissance ? 1 : 0.4 }}
                onClick={() => setEtape("genre")}
              >
                continuer
              </button>
            )}
          </div>
        )}

        {etape === "genre" && (
          <div className={styles.step}>
            <h1 className="title">vous êtes</h1>
            <div className={styles.options}>
              {(
                [
                  ["femme", "une femme"],
                  ["homme", "un homme"],
                  ["autre", "autre"],
                ] as [Genre, string][]
              ).map(([val, label]) => (
                <button
                  key={val}
                  className={`${styles.option} ${
                    genre === val ? styles.optionOn : ""
                  }`}
                  onClick={() => {
                    setGenre(val);
                    setEtape("recherche");
                  }}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>
        )}

        {etape === "recherche" && (
          <div className={styles.step}>
            <h1 className="title">vous cherchez</h1>
            <div className={styles.options}>
              {(
                [
                  ["femmes", "des femmes"],
                  ["hommes", "des hommes"],
                  ["les_deux", "les deux"],
                ] as [Recherche, string][]
              ).map(([val, label]) => (
                <button
                  key={val}
                  className={`${styles.option} ${
                    recherche === val ? styles.optionOn : ""
                  }`}
                  onClick={() => terminer(val)}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>
        )}

        {etape === "fait" && (
          <div className={styles.step}>
            <p className="eyebrow">votre profil est prêt</p>
            <hr className="rule" />
            <p className="subtitle" style={{ maxWidth: 300 }}>
              Vous pourrez tout modifier plus tard dans les paramètres.
            </p>
            <Link
              href="/activer"
              className="btn btn--primary btn--block mt-3"
            >
              activer mon signal
            </Link>
          </div>
        )}
      </main>
    </>
  );
}

function Progression({ etape }: { etape: Etape }) {
  const ordre: Etape[] = ["naissance", "genre", "recherche"];
  const index = ordre.indexOf(etape);
  return (
    <div className={styles.progress} aria-hidden="true">
      {ordre.map((_, i) => (
        <span
          key={i}
          className={`${styles.dot} ${i <= index ? styles.dotOn : ""}`}
        />
      ))}
    </div>
  );
}
