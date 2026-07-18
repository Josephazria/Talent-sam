"use client";

import styles from "./Modale.module.css";

// Modale avec overlay sombre uni (~85 %) : l'arrière-plan n'est jamais lisible.
export default function Modale({
  children,
  onClose,
}: {
  children: React.ReactNode;
  onClose: () => void;
}) {
  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.panel} onClick={(e) => e.stopPropagation()}>
        {children}
      </div>
    </div>
  );
}
