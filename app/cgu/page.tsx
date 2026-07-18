import Link from "next/link";
import { BackIcon } from "@/components/Icons";
import styles from "./legal.module.css";

export const metadata = { title: "nod — conditions d'utilisation" };

export default function CGU() {
  return (
    <>
      <Link
        href="/parametres"
        className="corner corner--left"
        aria-label="Retour"
      >
        <BackIcon />
      </Link>
      <main className={`screen ${styles.page}`}>
        <p className="eyebrow">conditions d&apos;utilisation</p>
        <hr className="rule" style={{ margin: "1rem 0 2rem" }} />

        <h2 className={styles.h}>Objet</h2>
        <p className={styles.p}>
          Nod met en relation, de façon discrète, des personnes présentes dans
          un même lieu et mutuellement ouvertes à une rencontre. L&apos;usage du
          service implique l&apos;acceptation des présentes conditions.
        </p>

        <h2 className={styles.h}>Âge requis</h2>
        <p className={styles.p}>
          Nod est strictement réservé aux personnes majeures (18 ans et plus).
          Toute inscription d&apos;un mineur est interdite.
        </p>

        <h2 className={styles.h}>Comportement</h2>
        <p className={styles.p}>
          Chacun s&apos;engage à un comportement respectueux. Le harcèlement,
          les propos haineux et toute conduite illégale entraînent la
          suspension du compte. Un système de signalement et de blocage est à
          votre disposition.
        </p>

        <h2 className={styles.h}>Crédits et paiements</h2>
        <p className={styles.p}>
          Certaines fonctionnalités reposent sur des crédits payants. Les achats
          sont traités par notre prestataire de paiement. Les crédits ne sont
          pas remboursables une fois utilisés.
        </p>

        <h2 className={styles.h}>Responsabilité</h2>
        <p className={styles.p}>
          Nod fournit un outil de mise en relation mais n&apos;organise pas les
          rencontres et ne saurait être tenu responsable des interactions entre
          utilisateurs. Soyez prudent lors de vos rencontres.
        </p>

        <p className={styles.note}>
          Document indicatif — à faire valider par un professionnel du droit
          avant la mise en ligne publique.
        </p>
      </main>
    </>
  );
}
