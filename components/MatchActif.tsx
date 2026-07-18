"use client";

import { useEffect, useRef, useState } from "react";
import type { Match } from "@/lib/match";
import styles from "./MatchActif.module.css";

// Écran 7 — Match. Rôles attribués aléatoirement par le serveur :
// l'un fait un signe physique, l'autre dit une phrase de code, le premier
// confirme par une phrase de réponse. Chacun voit clairement son rôle.
export default function MatchActif({
  match,
  myId,
  occupe,
  onAnnuler,
  onExpire,
}: {
  match: Match;
  myId: string;
  occupe: boolean;
  onAnnuler: () => void;
  onExpire: () => void;
}) {
  const jeFaisLeSigne = match.role_signe === myId;

  const [reste, setReste] = useState(() =>
    Math.max(
      0,
      Math.floor((new Date(match.expires_at).getTime() - Date.now()) / 1000)
    )
  );
  const expireRef = useRef(onExpire);
  expireRef.current = onExpire;

  useEffect(() => {
    const id = setInterval(() => {
      const s = Math.max(
        0,
        Math.floor((new Date(match.expires_at).getTime() - Date.now()) / 1000)
      );
      setReste(s);
      if (s <= 0) {
        clearInterval(id);
        expireRef.current();
      }
    }, 1000);
    return () => clearInterval(id);
  }, [match.expires_at]);

  const mm = String(Math.floor(reste / 60)).padStart(2, "0");
  const ss = String(reste % 60).padStart(2, "0");

  return (
    <div className={styles.bloc}>
      <p className="eyebrow">une rencontre</p>

      {jeFaisLeSigne ? (
        <>
          <h1 className={styles.role}>faites ce signe</h1>
          <p className={styles.action}>{match.signe}</p>
          <hr className="rule" />
          <p className={styles.instruction}>
            Quand on vous aborde par «&nbsp;{match.phrase}&nbsp;», répondez :
          </p>
          <p className={styles.dit}>«&nbsp;{match.reponse}&nbsp;»</p>
        </>
      ) : (
        <>
          <h1 className={styles.role}>dites cette phrase</h1>
          <p className={styles.dit}>«&nbsp;{match.phrase}&nbsp;»</p>
          <hr className="rule" />
          <p className={styles.instruction}>
            À la personne qui montre&nbsp;: {match.signe}. Elle répondra
            «&nbsp;{match.reponse}&nbsp;».
          </p>
        </>
      )}

      <p className={styles.count}>
        {mm}:{ss}
      </p>

      <button
        className="btn btn--ghost"
        onClick={onAnnuler}
        disabled={occupe}
      >
        annuler
      </button>
    </div>
  );
}
