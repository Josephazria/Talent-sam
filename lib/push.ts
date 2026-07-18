"use client";

import { supabase } from "./supabase";
import { VAPID_PUBLIC_KEY } from "./pushConfig";

function base64ToUint8(base64: string): Uint8Array {
  const padding = "=".repeat((4 - (base64.length % 4)) % 4);
  const b64 = (base64 + padding).replace(/-/g, "+").replace(/_/g, "/");
  const raw = atob(b64);
  const arr = new Uint8Array(raw.length);
  for (let i = 0; i < raw.length; i++) arr[i] = raw.charCodeAt(i);
  return arr;
}

// Demande l'autorisation et enregistre l'abonnement push. Best-effort :
// renvoie false si non supporté ou refusé (l'app retombe sur la vérification
// en direct toutes les 4 s tant qu'elle est ouverte).
export async function activerNotifications(): Promise<boolean> {
  try {
    if (!("serviceWorker" in navigator) || !("PushManager" in window)) {
      return false;
    }
    const reg = await navigator.serviceWorker.register("/sw.js");
    if (Notification.permission === "denied") return false;
    const perm =
      Notification.permission === "granted"
        ? "granted"
        : await Notification.requestPermission();
    if (perm !== "granted") return false;

    let sub = await reg.pushManager.getSubscription();
    if (!sub) {
      sub = await reg.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: base64ToUint8(VAPID_PUBLIC_KEY),
      });
    }
    const {
      data: { user },
    } = await supabase.auth.getUser();
    if (!user) return false;
    await supabase.from("push_subscriptions").upsert({
      user_id: user.id,
      subscription: sub.toJSON(),
      updated_at: new Date().toISOString(),
    });
    return true;
  } catch {
    return false;
  }
}

// Envoie une notification à l'autre personne d'un match.
export async function notifierMatch(toUserId: string): Promise<void> {
  try {
    const {
      data: { session },
    } = await supabase.auth.getSession();
    if (!session) return;
    await fetch("/api/push/notify", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${session.access_token}`,
      },
      body: JSON.stringify({ toUserId }),
    });
  } catch {
    // sans effet si l'envoi échoue
  }
}
