import { NextResponse } from "next/server";
import webpush from "web-push";
import { createClient } from "@supabase/supabase-js";
import { SUPABASE_URL } from "@/lib/supabaseConfig";
import { VAPID_PUBLIC_KEY } from "@/lib/pushConfig";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  const priv = process.env.VAPID_PRIVATE_KEY;
  const service = process.env.SUPABASE_SERVICE_ROLE_KEY;
  if (!priv || !service) {
    return NextResponse.json({ error: "non configuré" }, { status: 503 });
  }

  const token = request.headers
    .get("authorization")
    ?.replace("Bearer ", "");
  if (!token) return NextResponse.json({ error: "non autorisé" }, { status: 401 });

  let toUserId: string | undefined;
  try {
    ({ toUserId } = await request.json());
  } catch {
    return NextResponse.json({ error: "invalide" }, { status: 400 });
  }
  if (!toUserId) return NextResponse.json({ error: "invalide" }, { status: 400 });

  const admin = createClient(SUPABASE_URL, service);

  // Vérifie l'appelant et qu'un match le lie bien à la cible (anti-abus).
  const {
    data: { user },
  } = await admin.auth.getUser(token);
  if (!user) return NextResponse.json({ error: "non autorisé" }, { status: 401 });

  const { data: lien } = await admin
    .from("matches")
    .select("id")
    .or(
      `and(user_a.eq.${user.id},user_b.eq.${toUserId}),and(user_a.eq.${toUserId},user_b.eq.${user.id})`
    )
    .eq("annule", false)
    .limit(1)
    .maybeSingle();
  if (!lien) return NextResponse.json({ ok: false });

  const { data: sub } = await admin
    .from("push_subscriptions")
    .select("subscription")
    .eq("user_id", toUserId)
    .maybeSingle();
  if (!sub) return NextResponse.json({ ok: false });

  webpush.setVapidDetails("mailto:contact@nod.app", VAPID_PUBLIC_KEY, priv);
  try {
    await webpush.sendNotification(
      sub.subscription,
      JSON.stringify({
        title: "nod",
        body: "Une rencontre vous attend.",
        url: "/activer",
      })
    );
  } catch {
    // abonnement périmé ou injoignable — ignoré
  }
  return NextResponse.json({ ok: true });
}
