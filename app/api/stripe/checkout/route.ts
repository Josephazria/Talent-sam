import { NextResponse } from "next/server";
import Stripe from "stripe";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

// Montants côté serveur (source de vérité). Cohérent avec lib/paiement.ts.
const PACKS: Record<string, { credits: number; montant: number; label: string }> = {
  p5: { credits: 5, montant: 499, label: "nod — 5 signaux" },
  p15: { credits: 15, montant: 999, label: "nod — 15 signaux" },
};

export async function POST(request: Request) {
  const key = process.env.STRIPE_SECRET_KEY;
  if (!key) {
    return NextResponse.json(
      { error: "Le paiement n'est pas encore configuré." },
      { status: 503 }
    );
  }

  let body: { packId?: string; userId?: string };
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "Requête invalide." }, { status: 400 });
  }
  const pack = body.packId ? PACKS[body.packId] : undefined;
  if (!pack || !body.userId) {
    return NextResponse.json({ error: "Requête invalide." }, { status: 400 });
  }

  const stripe = new Stripe(key);
  const origin =
    request.headers.get("origin") ?? "https://talent-sam.vercel.app";

  const session = await stripe.checkout.sessions.create({
    mode: "payment",
    line_items: [
      {
        quantity: 1,
        price_data: {
          currency: "eur",
          unit_amount: pack.montant,
          product_data: { name: pack.label },
        },
      },
    ],
    metadata: { user_id: body.userId, credits: String(pack.credits) },
    success_url: `${origin}/activer?achat=ok`,
    cancel_url: `${origin}/paywall`,
  });

  return NextResponse.json({ url: session.url });
}
