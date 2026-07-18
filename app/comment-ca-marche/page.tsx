import Link from "next/link";
import { BackIcon } from "@/components/Icons";
import styles from "./page.module.css";

// Écran 2 — Comment ça marche
const etapes = [
  {
    n: "I",
    titre: "Activez votre signal",
    texte:
      "Sur place, vous vous signalez ouvert à une rencontre. Personne ne le sait, sauf ceux qui le sont aussi.",
  },
  {
    n: "II",
    titre: "Une rencontre se dessine",
    texte:
      "Si quelqu'un de compatible est présent au même endroit, vous êtes reliés tous les deux, en même temps.",
  },
  {
    n: "III",
    titre: "Le signe de reconnaissance",
    texte:
      "L'un de vous fait un signe discret. L'autre dit une phrase de code. Le premier répond pour confirmer.",
  },
  {
    n: "IV",
    titre: "Sans trace",
    texte:
      "Sans rencontre, le signal expire en silence. Rien n'est conservé. Jamais de rejet, jamais d'historique.",
  },
];

export default function CommentCaMarche() {
  return (
    <>
      <Link href="/" className="corner corner--left" aria-label="Retour">
        <BackIcon />
      </Link>

      <main className="screen">
        <header className={styles.head}>
          <p className="eyebrow">comment ça marche</p>
          <hr className="rule" style={{ margin: "1.25rem 0 0" }} />
        </header>

        <ol className={styles.list}>
          {etapes.map((e) => (
            <li key={e.n} className={styles.item}>
              <span className={styles.num}>{e.n}</span>
              <div className={styles.itemBody}>
                <h2 className={styles.itemTitle}>{e.titre}</h2>
                <p className={styles.itemText}>{e.texte}</p>
              </div>
            </li>
          ))}
        </ol>

        <div className={styles.footer}>
          <Link href="/activer" className="btn btn--primary btn--block">
            activer mon signal
          </Link>
        </div>
      </main>
    </>
  );
}
