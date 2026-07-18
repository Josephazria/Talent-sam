"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { BackIcon } from "@/components/Icons";
import Modale from "@/components/Modale";
import {
  getProfilComplet,
  updateProfil,
  updateReconnaissance,
  bloquerDernierMatch,
  seDeconnecter,
  supprimerCompte,
  signaler,
  SIGNES,
  PHRASE_DEFAUT,
  REPONSE_DEFAUT,
  type ProfilComplet,
} from "@/lib/parametres";
import styles from "./parametres.module.css";

type Fenetre =
  | null
  | "profil"
  | "reconnaissance"
  | "signaler"
  | "supprimer";

const GENRES: [string, string][] = [
  ["femme", "une femme"],
  ["homme", "un homme"],
  ["autre", "autre"],
];
const RECHERCHES: [string, string][] = [
  ["femmes", "des femmes"],
  ["hommes", "des hommes"],
  ["les_deux", "les deux"],
];

export default function Parametres() {
  const router = useRouter();
  const [profil, setProfil] = useState<ProfilComplet | null>(null);
  const [charge, setCharge] = useState(false);
  const [fenetre, setFenetre] = useState<Fenetre>(null);
  const [info, setInfo] = useState<string | null>(null);

  async function recharger() {
    setProfil(await getProfilComplet());
    setCharge(true);
  }
  useEffect(() => {
    recharger();
  }, []);

  if (!charge) {
    return (
      <>
        <Coin />
        <main className="screen screen--center">
          <p className="muted">un instant…</p>
        </main>
      </>
    );
  }

  // Non connecté : accès au légal et à la connexion uniquement.
  if (!profil) {
    return (
      <>
        <Coin />
        <main className="screen">
          <Titre />
          <Section titre="légal">
            <Ligne label="Conditions d'utilisation" href="/cgu" />
            <Ligne label="Confidentialité" href="/confidentialite" />
          </Section>
          <div className="mt-3">
            <Link href="/compte" className="btn btn--primary btn--block">
              se connecter
            </Link>
          </div>
        </main>
      </>
    );
  }

  const genreLabel = GENRES.find((g) => g[0] === profil.genre)?.[1] ?? profil.genre;
  const rechLabel =
    RECHERCHES.find((r) => r[0] === profil.recherche)?.[1] ?? profil.recherche;

  return (
    <>
      <Coin />
      <main className="screen">
        <Titre />

        {info && <p className={styles.info}>{info}</p>}

        <Section titre="mon profil">
          <Ligne
            label="Je suis"
            valeur={genreLabel}
            onClick={() => setFenetre("profil")}
          />
          <Ligne
            label="Je cherche"
            valeur={rechLabel}
            onClick={() => setFenetre("profil")}
          />
        </Section>

        <Section titre="ma reconnaissance">
          <Ligne
            label="Mon signe"
            valeur={profil.signe ? "personnalisé" : "aléatoire"}
            onClick={() => setFenetre("reconnaissance")}
          />
          <Ligne
            label="Ma phrase"
            valeur={profil.phrase ? "personnalisée" : "par défaut"}
            onClick={() => setFenetre("reconnaissance")}
          />
        </Section>

        <Section titre="mes signaux">
          <Ligne
            label="Crédits"
            valeur={profil.illimite ? "illimités" : String(profil.credits)}
          />
          {!profil.illimite && (
            <Ligne label="Acheter des crédits" href="/paywall" />
          )}
        </Section>

        <Section titre="sécurité">
          <Ligne
            label="Bloquer mon dernier match"
            onClick={async () => {
              const ok = await bloquerDernierMatch();
              setInfo(ok ? "Personne bloquée." : "Aucun match récent.");
            }}
          />
          <Ligne
            label="Signaler un problème"
            onClick={() => setFenetre("signaler")}
          />
        </Section>

        <Section titre="légal">
          <Ligne label="Conditions d'utilisation" href="/cgu" />
          <Ligne label="Confidentialité" href="/confidentialite" />
        </Section>

        <Section titre="compte">
          <Ligne label="E-mail" valeur={profil.email} />
          <Ligne
            label="Se déconnecter"
            onClick={async () => {
              await seDeconnecter();
              router.push("/");
            }}
          />
          <Ligne
            label="Supprimer mon compte"
            danger
            onClick={() => setFenetre("supprimer")}
          />
        </Section>

        <div style={{ height: "2rem" }} />
      </main>

      {fenetre === "profil" && (
        <FenetreProfil
          profil={profil}
          onClose={() => setFenetre(null)}
          onSave={async (g, r) => {
            await updateProfil(g, r);
            await recharger();
            setFenetre(null);
          }}
        />
      )}

      {fenetre === "reconnaissance" && (
        <FenetreReconnaissance
          profil={profil}
          onClose={() => setFenetre(null)}
          onSave={async (s, p, rep) => {
            await updateReconnaissance(s, p, rep);
            await recharger();
            setFenetre(null);
          }}
        />
      )}

      {fenetre === "signaler" && (
        <FenetreSignaler
          onClose={() => setFenetre(null)}
          onSend={async (msg) => {
            await signaler(msg);
            setFenetre(null);
            setInfo("Merci, votre signalement a été transmis.");
          }}
        />
      )}

      {fenetre === "supprimer" && (
        <Modale onClose={() => setFenetre(null)}>
          <p className="eyebrow">supprimer mon compte</p>
          <p className="subtitle mt-2">
            Votre compte et toutes vos données seront effacés
            immédiatement et définitivement. Cette action est irréversible.
          </p>
          <button
            className={`btn btn--primary btn--block mt-3 ${styles.danger}`}
            onClick={async () => {
              const ok = await supprimerCompte();
              if (ok) router.push("/");
              else setInfo("Suppression impossible pour l'instant.");
              setFenetre(null);
            }}
          >
            supprimer définitivement
          </button>
          <button className="btn btn--ghost mt-2" onClick={() => setFenetre(null)}>
            annuler
          </button>
        </Modale>
      )}
    </>
  );
}

function Coin() {
  return (
    <Link href="/" className="corner corner--left" aria-label="Retour">
      <BackIcon />
    </Link>
  );
}
function Titre() {
  return (
    <header className={styles.head}>
      <p className="eyebrow">paramètres</p>
      <hr className="rule" style={{ margin: "1.25rem 0 0" }} />
    </header>
  );
}

function Section({
  titre,
  children,
}: {
  titre: string;
  children: React.ReactNode;
}) {
  return (
    <section className={styles.section}>
      <h2 className={styles.sectionTitre}>{titre}</h2>
      <div className={styles.rows}>{children}</div>
    </section>
  );
}

function Ligne({
  label,
  valeur,
  href,
  onClick,
  danger,
}: {
  label: string;
  valeur?: string;
  href?: string;
  onClick?: () => void;
  danger?: boolean;
}) {
  const contenu = (
    <>
      <span className={danger ? styles.rowDanger : styles.rowLabel}>{label}</span>
      {valeur !== undefined && <span className={styles.rowValeur}>{valeur}</span>}
    </>
  );
  if (href) {
    return (
      <Link href={href} className={styles.row}>
        {contenu}
      </Link>
    );
  }
  return (
    <button className={styles.row} onClick={onClick} type="button">
      {contenu}
    </button>
  );
}

function FenetreProfil({
  profil,
  onClose,
  onSave,
}: {
  profil: ProfilComplet;
  onClose: () => void;
  onSave: (genre: string, recherche: string) => void;
}) {
  const [genre, setGenre] = useState(profil.genre);
  const [recherche, setRecherche] = useState(profil.recherche);
  return (
    <Modale onClose={onClose}>
      <p className="eyebrow">je suis</p>
      <div className={styles.choix}>
        {GENRES.map(([v, l]) => (
          <button
            key={v}
            className={`${styles.opt} ${genre === v ? styles.optOn : ""}`}
            onClick={() => setGenre(v)}
          >
            {l}
          </button>
        ))}
      </div>
      <p className="eyebrow mt-3">je cherche</p>
      <div className={styles.choix}>
        {RECHERCHES.map(([v, l]) => (
          <button
            key={v}
            className={`${styles.opt} ${recherche === v ? styles.optOn : ""}`}
            onClick={() => setRecherche(v)}
          >
            {l}
          </button>
        ))}
      </div>
      <button
        className="btn btn--primary btn--block mt-3"
        onClick={() => onSave(genre, recherche)}
      >
        enregistrer
      </button>
    </Modale>
  );
}

function FenetreReconnaissance({
  profil,
  onClose,
  onSave,
}: {
  profil: ProfilComplet;
  onClose: () => void;
  onSave: (
    signe: string | null,
    phrase: string | null,
    reponse: string | null
  ) => void;
}) {
  const [signe, setSigne] = useState<string | null>(profil.signe);
  const [phrase, setPhrase] = useState(profil.phrase ?? "");
  const [reponse, setReponse] = useState(profil.reponse ?? "");
  return (
    <Modale onClose={onClose}>
      <p className="eyebrow">mon signe</p>
      <div className={styles.choix}>
        <button
          className={`${styles.opt} ${signe === null ? styles.optOn : ""}`}
          onClick={() => setSigne(null)}
        >
          aléatoire
        </button>
        {SIGNES.map((s) => (
          <button
            key={s}
            className={`${styles.opt} ${signe === s ? styles.optOn : ""}`}
            onClick={() => setSigne(s)}
          >
            {s}
          </button>
        ))}
      </div>
      <p className="eyebrow mt-3">ma phrase de code</p>
      <input
        className={styles.champ}
        value={phrase}
        placeholder={PHRASE_DEFAUT}
        onChange={(e) => setPhrase(e.target.value)}
      />
      <input
        className={styles.champ}
        value={reponse}
        placeholder={REPONSE_DEFAUT}
        onChange={(e) => setReponse(e.target.value)}
      />
      <button
        className="btn btn--primary btn--block mt-3"
        onClick={() =>
          onSave(
            signe,
            phrase.trim() ? phrase.trim() : null,
            reponse.trim() ? reponse.trim() : null
          )
        }
      >
        enregistrer
      </button>
    </Modale>
  );
}

function FenetreSignaler({
  onClose,
  onSend,
}: {
  onClose: () => void;
  onSend: (message: string) => void;
}) {
  const [msg, setMsg] = useState("");
  return (
    <Modale onClose={onClose}>
      <p className="eyebrow">signaler un problème</p>
      <textarea
        className={styles.zone}
        value={msg}
        rows={4}
        placeholder="Décrivez la situation…"
        onChange={(e) => setMsg(e.target.value)}
      />
      <button
        className="btn btn--primary btn--block mt-2"
        disabled={!msg.trim()}
        style={{ opacity: msg.trim() ? 1 : 0.4 }}
        onClick={() => onSend(msg.trim())}
      >
        envoyer
      </button>
    </Modale>
  );
}
