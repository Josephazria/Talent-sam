import { NextResponse } from "next/server";
import Stripe from "stripe";
import { createClient } from "@supabase/supabase-js";
import { SUPABASE_URL } from "@/lib/supabaseConfig";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

// Confirme le paiement Stripe et crédite le compte (via la clé de service,
// côté serveur uniquement).
export async function POST(request: Request) {
  const key = process.env.STRIPE_SECRET_KEY;
  const whSecret = process.env.STRIPE_WEBHOOK_SECRET;
  const serviceKey = process.env.SUPABASE_SERVICE_ROLE_KEY;
  if (!key || !whSecret || !serviceKey) {
    return NextResponse.json({ error: "non configuré" }, { status: 503 });
  }

  const stripe = new Stripe(key);
  const signature = request.headers.get("stripe-signature");
  const raw = await request.text();

  let event: Stripe.Event;
  try {
    event = stripe.webhooks.constructEvent(raw, signature ?? "", whSecret);
  } catch {
    return NextResponse.json({ error: "signature invalide" }, { status: 400 });
  }

  if (event.type === "checkout.session.completed") {
    const s = event.data.object as Stripe.Checkout.Session;
    const uid = s.metadata?.user_id;
    const credits = parseInt(s.metadata?.credits ?? "0", 10);
    if (uid && credits > 0) {
      const admin = createClient(SUPABASE_URL, serviceKey);
      await admin.rpc("ajouter_credits", { p_user: uid, p_montant: credits });
    }
  }

  return NextResponse.json({ received: true });
}
