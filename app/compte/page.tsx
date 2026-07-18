"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { BackIcon } from "@/components/Icons";
import { supabase } from "@/lib/supabase";
import {
  fetchMyProfile,
  saveMyProfile,
  ageFromISO,
  type Genre,
  type Recherche,
} from "@/lib/profile";
import styles from "./compte.module.css";

// Écran 4 — Création de compte.
// Ordre : connexion (lien e-mail), puis date de naissance (blocage < 18 ans),
// puis genre, puis « je cherche ». Une question par écran.
type Etape =
  | "chargement"
  | "connexion"
  | "email_envoye"
  | "naissance"
  | "genre"
  | "recherche"
  | "fait";

export default function Compte() {
  const router = useRouter();
  const [etape, setEtape] = useState<Etape>("chargement");
  const [email, setEmail] = useState("");
  const [envoi, setEnvoi] = useState(false);
  const [erreur, setErreur] = useState<string | null>(null);

  const [naissance, setNaissance] = useState("");
  const [genre, setGenre] = useState<Genre | null>(null);
  const [enregistrement, setEnregistrement] = useState(false);

  const age = naissance ? ageFromISO(naissance) : null;
  const mineur = age !== null && age < 18;

  // Au chargement et à chaque changement d'état d'authentification :
  // si connecté avec un profil, on file à l'activation ; connecté sans profil,
  // on poursuit l'inscription ; sinon, on demande l'e-mail.
  useEffect(() => {
    let actif = true;
    async function router_selon_session() {
      const {
        data: { session },
      } = await supabase.auth.getSession();
      if (!actif) return;
      if (!session) {
        setEtape("connexion");
        return;
      }
      const profil = await fetchMyProfile();
      if (!actif) return;
      if (profil) router.replace("/activer");
      else setEtape((e) => (e === "chargement" || e === "connexion" || e === "email_envoye" ? "naissance" : e));
    }
    router_selon_session();
    const { data: sub } = supabase.auth.onAuthStateChange(() => {
      router_selon_session();
    });
    return () => {
      actif = false;
      sub.subscription.unsubscribe();
    };
  }, [router]);

  async function envoyerLien() {
    setErreur(null);
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
      setErreur("Adresse e-mail invalide.");
      return;
    }
    setEnvoi(true);
    const { error } = await supabase.auth.signInWithOtp({
      email,
      options: {
        emailRedirectTo: `${window.location.origin}/compte`,
        shouldCreateUser: true,
      },
    });
    setEnvoi(false);
    if (error) setErreur("Envoi impossible. Réessayez dans un instant.");
    else setEtape("email_envoye");
  }

  async function terminer(r: Recherche) {
    if (!naissance || !genre) return;
    setEnregistrement(true);
    const { error } = await saveMyProfile({ naissance, genre, recherche: r });
    setEnregistrement(false);
    if (error) {
      setErreur("Enregistrement impossible. Réessayez.");
      return;
    }
    setEtape("fait");
  }

  function retour() {
    if (etape === "naissance" || etape === "connexion") router.push("/");
    else if (etape === "email_envoye") setEtape("connexion");
    else if (etape === "genre") setEtape("naissance");
    else if (etape === "recherche") setEtape("genre");
  }

  return (
    <>
      {etape !== "fait" && etape !== "chargement" && (
        <button
          onClick={retour}
          className="corner corner--left"
          aria-label="Retour"
        >
          <BackIcon />
        </button>
      )}

      <main className="screen screen--center">
        {(etape === "naissance" ||
          etape === "genre" ||
          etape === "recherche") && <Progression etape={etape} />}

        {etape === "chargement" && <p className="muted">un instant…</p>}

        {etape === "connexion" && (
          <div className={styles.step}>
            <h1 className="title">créer mon compte</h1>
            <p className="subtitle mt-2">
              Sans mot de passe. Vous recevrez un lien de connexion par e-mail.
            </p>
            <input
              type="email"
              inputMode="email"
              autoComplete="email"
              className={styles.input}
              placeholder="votre@email.fr"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && envoyerLien()}
              aria-label="Adresse e-mail"
            />
            {erreur && <p className={styles.erreur}>{erreur}</p>}
            <button
              className="btn btn--primary btn--block mt-3"
              onClick={envoyerLien}
              disabled={envoi}
              style={{ opacity: envoi ? 0.5 : 1 }}
            >
              {envoi ? "envoi…" : "recevoir mon lien"}
            </button>
          </div>
        )}

        {etape === "email_envoye" && (
          <div className={styles.step}>
            <p className="eyebrow">vérifiez vos e-mails</p>
            <hr className="rule" />
            <p className="subtitle" style={{ maxWidth: 300 }}>
              Un lien de connexion a été envoyé à {email}. Ouvrez-le sur cet
              appareil pour continuer.
            </p>
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
                    enregistrement ? styles.optionOff : ""
                  }`}
                  disabled={enregistrement}
                  onClick={() => terminer(val)}
                >
                  {label}
                </button>
              ))}
            </div>
            {erreur && <p className={styles.erreur}>{erreur}</p>}
          </div>
        )}

        {etape === "fait" && (
          <div className={styles.step}>
            <p className="eyebrow">votre profil est prêt</p>
            <hr className="rule" />
            <p className="subtitle" style={{ maxWidth: 300 }}>
              Vous pourrez tout modifier plus tard dans les paramètres.
            </p>
            <button
              className="btn btn--primary btn--block mt-3"
              onClick={() => router.push("/activer")}
            >
              activer mon signal
            </button>
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
