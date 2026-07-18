import { NextResponse } from "next/server";
import { createClient } from "@supabase/supabase-js";
import { SUPABASE_URL } from "@/lib/supabaseConfig";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

// Suppression RGPD : efface le compte d'authentification. Toutes les données
// liées (profil, signaux, matchs, abonnements push, blocages) disparaissent
// en cascade. Réelle et immédiate.
export async function POST(request: Request) {
  const service = process.env.SUPABASE_SERVICE_ROLE_KEY;
  if (!service) {
    return NextResponse.json({ error: "non configuré" }, { status: 503 });
  }
  const token = request.headers.get("authorization")?.replace("Bearer ", "");
  if (!token) return NextResponse.json({ error: "non autorisé" }, { status: 401 });

  const admin = createClient(SUPABASE_URL, service);
  const {
    data: { user },
  } = await admin.auth.getUser(token);
  if (!user) return NextResponse.json({ error: "non autorisé" }, { status: 401 });

  const { error } = await admin.auth.admin.deleteUser(user.id);
  if (error) {
    return NextResponse.json({ error: "échec" }, { status: 500 });
  }
  return NextResponse.json({ ok: true });
}
