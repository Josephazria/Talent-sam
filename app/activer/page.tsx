"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getProfile } from "@/lib/profile";
import AParaitre from "@/components/AParaitre";

// Le parcours d'activation (lieu, signal) est construit à l'étape 3.
// Règle : un compte est exigé à la première activation. Sans profil,
// on redirige vers l'inscription.
export default function Activer() {
  const router = useRouter();
  const [pret, setPret] = useState(false);

  useEffect(() => {
    if (getProfile()) {
      setPret(true);
    } else {
      router.replace("/compte");
    }
  }, [router]);

  if (!pret) return null;

  return <AParaitre titre="activer mon signal" />;
}
