"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { fetchMyProfile } from "@/lib/profile";
import AParaitre from "@/components/AParaitre";

// Règle : un compte (et un profil complet) est exigé à la première activation.
// Sinon, on redirige vers l'inscription. Le parcours d'activation lui-même
// (lieu, signal) est construit à l'étape 3.
export default function Activer() {
  const router = useRouter();
  const [pret, setPret] = useState(false);

  useEffect(() => {
    let actif = true;
    (async () => {
      const profil = await fetchMyProfile();
      if (!actif) return;
      if (profil) setPret(true);
      else router.replace("/compte");
    })();
    return () => {
      actif = false;
    };
  }, [router]);

  if (!pret) return null;

  return <AParaitre titre="activer mon signal" />;
}
