import Link from "next/link";
import { BackIcon } from "@/components/Icons";
import styles from "../cgu/legal.module.css";

export const metadata = { title: "nod — confidentialité" };

export default function Confidentialite() {
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
        <p className="eyebrow">confidentialité</p>
        <hr className="rule" style={{ margin: "1rem 0 2rem" }} />

        <h2 className={styles.h}>Sans trace</h2>
        <p className={styles.p}>
          C&apos;est notre promesse centrale. Les données de session — position,
          lieu, signal, match — sont supprimées à leur expiration. Nous ne
          conservons pas d&apos;historique de vos rencontres.
        </p>

        <h2 className={styles.h}>Position</h2>
        <p className={styles.p}>
          Votre position n&apos;est lue qu&apos;une seule fois, au moment où vous
          activez un signal, pour reconnaître le lieu. Il n&apos;y a jamais de
          suivi continu de votre localisation.
        </p>

        <h2 className={styles.h}>Données conservées</h2>
        <p className={styles.p}>
          Nous conservons uniquement le minimum nécessaire à votre compte :
          votre e-mail, votre date de naissance (pour la vérification
          d&apos;âge), votre genre et votre préférence. Aucune de ces
          informations n&apos;est vendue.
        </p>

        <h2 className={styles.h}>Anonymat sur la carte</h2>
        <p className={styles.p}>
          La carte n&apos;affiche que des agrégats anonymes. Aucun profil, aucune
          photo, aucune position individuelle n&apos;est jamais exposée.
        </p>

        <h2 className={styles.h}>Vos droits (RGPD)</h2>
        <p className={styles.p}>
          Vous pouvez supprimer votre compte et l&apos;intégralité de vos données
          à tout moment, depuis les paramètres. La suppression est réelle et
          immédiate.
        </p>

        <p className={styles.note}>
          Document indicatif — à faire valider par un professionnel du droit
          avant la mise en ligne publique.
        </p>
      </main>
    </>
  );
}
