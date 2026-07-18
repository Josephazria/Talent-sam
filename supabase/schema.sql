-- Nod — schéma de base de données
-- À exécuter dans Supabase : SQL Editor > New query > coller > Run.

-- Table des profils : une ligne par utilisateur, liée au compte d'auth.
create table if not exists public.profiles (
  id uuid primary key references auth.users (id) on delete cascade,
  naissance date not null,
  genre text not null check (genre in ('femme', 'homme', 'autre')),
  recherche text not null check (recherche in ('femmes', 'hommes', 'les_deux')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- Sécurité au niveau des lignes : chacun n'accède qu'à sa propre ligne.
alter table public.profiles enable row level security;

drop policy if exists "profils : lecture de soi" on public.profiles;
create policy "profils : lecture de soi"
  on public.profiles for select
  using (auth.uid() = id);

drop policy if exists "profils : création de soi" on public.profiles;
create policy "profils : création de soi"
  on public.profiles for insert
  with check (auth.uid() = id);

drop policy if exists "profils : mise à jour de soi" on public.profiles;
create policy "profils : mise à jour de soi"
  on public.profiles for update
  using (auth.uid() = id)
  with check (auth.uid() = id);

-- Tient à jour la date de modification.
create or replace function public.touch_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists profiles_touch_updated_at on public.profiles;
create trigger profiles_touch_updated_at
  before update on public.profiles
  for each row execute function public.touch_updated_at();

-- Signaux : un seul signal actif par personne, valable 30 minutes.
-- « Sans trace » : les signaux expirés sont supprimés (côté app à l'ouverture,
-- et côté serveur par le nettoyage périodique ci-dessous).
create table if not exists public.signals (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null unique references auth.users (id) on delete cascade,
  venue_id text not null,
  venue_name text not null,
  lat double precision,
  lng double precision,
  created_at timestamptz not null default now(),
  expires_at timestamptz not null
);

alter table public.signals enable row level security;

drop policy if exists "signaux_lecture_de_soi" on public.signals;
create policy "signaux_lecture_de_soi"
  on public.signals for select using (auth.uid() = user_id);
drop policy if exists "signaux_creation_de_soi" on public.signals;
create policy "signaux_creation_de_soi"
  on public.signals for insert with check (auth.uid() = user_id);
drop policy if exists "signaux_maj_de_soi" on public.signals;
create policy "signaux_maj_de_soi"
  on public.signals for update using (auth.uid() = user_id) with check (auth.uid() = user_id);
drop policy if exists "signaux_suppr_de_soi" on public.signals;
create policy "signaux_suppr_de_soi"
  on public.signals for delete using (auth.uid() = user_id);

-- ===========================================================================
-- Matching (étape 4)
-- ===========================================================================

-- Compatibilité : la préférence « recherche » inclut-elle ce « genre » ?
create or replace function public.compatible(recherche text, genre text)
returns boolean language sql immutable as $$
  select case
    when recherche = 'les_deux' then true
    when recherche = 'femmes' then genre = 'femme'
    when recherche = 'hommes' then genre = 'homme'
    else false
  end;
$$;

create table if not exists public.matches (
  id uuid primary key default gen_random_uuid(),
  venue_id text not null,
  user_a uuid not null references auth.users (id) on delete cascade,
  user_b uuid not null references auth.users (id) on delete cascade,
  role_signe uuid not null,
  signe text not null,
  phrase text not null,
  reponse text not null,
  created_at timestamptz not null default now(),
  expires_at timestamptz not null,
  annule boolean not null default false
);

alter table public.matches enable row level security;

drop policy if exists "matchs_lecture" on public.matches;
create policy "matchs_lecture" on public.matches for select
  using (auth.uid() = user_a or auth.uid() = user_b);
drop policy if exists "matchs_maj" on public.matches;
create policy "matchs_maj" on public.matches for update
  using (auth.uid() = user_a or auth.uid() = user_b)
  with check (auth.uid() = user_a or auth.uid() = user_b);

-- Renvoie le match courant, en crée un si une personne compatible attend
-- dans le même lieu, ou renvoie null. S'exécute avec les droits du
-- propriétaire (accès à tous les signaux) pour trouver les candidats.
create or replace function public.tick_match()
returns public.matches
language plpgsql security definer set search_path = public as $$
declare
  moi uuid := auth.uid();
  mon_signal public.signals;
  mon_profil public.profiles;
  cand public.signals;
  cand_profil public.profiles;
  m public.matches;
  signes text[] := array[
    'un verre vide retourné, posé devant vous',
    'un sous-verre posé sur le dessus du verre',
    'le téléphone posé face contre la table',
    'la veste sur une seule épaule',
    'une paille pliée en deux, posée sur la table',
    'une serviette nouée autour du poignet',
    'deux verres côte à côte, dont un vide',
    'la montre portée cadran côté paume'
  ];
  phrases text[] := array[
    'La soirée vous plaît ?',
    'Vous venez souvent ici ?',
    'Belle ambiance, ce soir.',
    'Vous permettez une question ?'
  ];
  reponses text[] := array[
    'Davantage à l''instant.',
    'Jamais assez, visiblement.',
    'Elle vient de s''améliorer.',
    'Seulement si c''est la bonne.'
  ];
  si int;
  pi int;
  qui_signe uuid;
begin
  if moi is null then return null; end if;

  select * into m from public.matches
    where (user_a = moi or user_b = moi) and annule = false and expires_at > now()
    order by created_at desc limit 1;
  if found then return m; end if;

  select * into mon_signal from public.signals where user_id = moi;
  if not found then return null; end if;
  select * into mon_profil from public.profiles where id = moi;
  if not found then return null; end if;

  for cand in
    select s.* from public.signals s
    where s.venue_id = mon_signal.venue_id
      and s.user_id <> moi
      and s.expires_at > now()
    order by s.created_at asc
    for update skip locked
  loop
    select * into cand_profil from public.profiles where id = cand.user_id;
    if not found then continue; end if;
    if public.compatible(mon_profil.recherche, cand_profil.genre)
       and public.compatible(cand_profil.recherche, mon_profil.genre) then
      si := 1 + floor(random() * array_length(signes, 1))::int;
      pi := 1 + floor(random() * array_length(phrases, 1))::int;
      if random() < 0.5 then qui_signe := moi; else qui_signe := cand.user_id; end if;
      insert into public.matches
        (venue_id, user_a, user_b, role_signe, signe, phrase, reponse, expires_at)
      values
        (mon_signal.venue_id, moi, cand.user_id, qui_signe,
         signes[si], phrases[pi], reponses[pi], now() + interval '10 minutes')
      returning * into m;
      delete from public.signals where user_id in (moi, cand.user_id);
      return m;
    end if;
  end loop;

  return null;
end;
$$;

grant execute on function public.compatible(text, text) to authenticated;
grant execute on function public.tick_match() to authenticated;

-- ===========================================================================
-- Carte (étape 6) — agrégats anonymes par lieu
-- ===========================================================================
-- Renvoie, pour chaque lieu où au moins 4 personnes compatibles sont actives :
-- la position, un niveau d'intensité, un palier (jamais le chiffre exact) et
-- une tranche d'âge de 10 ans. Aucune donnée individuelle n'est exposée.
create or replace function public.carte_halos()
returns table (
  venue_id text, venue_name text, lat float8, lng float8,
  niveau text, bucket text, tranche text
)
language plpgsql security definer set search_path = public as $$
declare
  moi uuid := auth.uid();
  mon public.profiles;
begin
  if moi is not null then
    select * into mon from public.profiles where id = moi;
  end if;
  return query
  with actifs as (
    select s.venue_id, s.venue_name, s.lat, s.lng,
           p.genre, p.recherche,
           extract(year from age(p.naissance))::int as age
    from public.signals s
    join public.profiles p on p.id = s.user_id
    where s.expires_at > now() and s.lat is not null and s.lng is not null
  ),
  compat as (
    select * from actifs a
    where moi is null or (
      public.compatible(mon.recherche, a.genre)
      and public.compatible(a.recherche, mon.genre)
    )
  ),
  grp as (
    select c.venue_id,
           max(c.venue_name) as venue_name,
           avg(c.lat)::float8 as lat,
           avg(c.lng)::float8 as lng,
           count(*)::int as n,
           avg(c.age)::numeric as avgage
    from compat c group by c.venue_id
  )
  select g.venue_id, g.venue_name, g.lat, g.lng,
    case when g.n >= 10 then 'tres_actif' else 'actif' end,
    case when g.n >= 10 then '10+' when g.n >= 8 then '8+'
         when g.n >= 6 then '6+' else '4+' end,
    (greatest(18, (round(g.avgage/5)*5 - 5))::int)::text || '-' ||
    (greatest(28, (round(g.avgage/5)*5 + 5))::int)::text || ' ans'
  from grp g where g.n >= 4;
end;
$$;

grant execute on function public.carte_halos() to anon, authenticated;

-- ===========================================================================
-- Crédits et paywall (étape 7)
-- ===========================================================================
alter table public.profiles add column if not exists credits int not null default 0;
alter table public.profiles add column if not exists signaux_utilises int not null default 0;

-- Packs événement (sans UI) : un organisateur peut offrir des signaux
-- illimités à tous les participants d'un venue/code donné.
create table if not exists public.event_packs (
  venue_id text primary key,
  illimite boolean not null default true,
  expires_at timestamptz
);
alter table public.event_packs enable row level security;
drop policy if exists "packs_lecture" on public.event_packs;
create policy "packs_lecture" on public.event_packs for select using (true);

-- Active un signal en appliquant les règles de crédits (femmes/others :
-- illimité ; hommes : 3 gratuits puis 1 crédit). Renvoie 'ok' ou 'paywall'.
create or replace function public.activer_signal(
  p_venue_id text, p_venue_name text, p_lat float8, p_lng float8
) returns text
language plpgsql security definer set search_path = public as $$
declare
  moi uuid := auth.uid();
  prof public.profiles;
  existant public.signals;
  gratuit boolean;
begin
  if moi is null then return 'non_connecte'; end if;
  select * into prof from public.profiles where id = moi;
  if not found then return 'non_connecte'; end if;

  -- Signal déjà actif : on le remplace sans reconsommer.
  select * into existant from public.signals where user_id = moi and expires_at > now();
  if found then
    update public.signals
      set venue_id = p_venue_id, venue_name = p_venue_name, lat = p_lat, lng = p_lng
      where user_id = moi;
    return 'ok';
  end if;

  gratuit := prof.genre in ('femme', 'autre');
  if exists (
    select 1 from public.event_packs
    where venue_id = p_venue_id and (expires_at is null or expires_at > now())
  ) then
    gratuit := true;
  end if;

  if not gratuit then
    if prof.signaux_utilises < 3 then
      update public.profiles set signaux_utilises = signaux_utilises + 1 where id = moi;
    elsif prof.credits > 0 then
      update public.profiles set credits = credits - 1 where id = moi;
    else
      return 'paywall';
    end if;
  end if;

  insert into public.signals (user_id, venue_id, venue_name, lat, lng, expires_at)
    values (moi, p_venue_id, p_venue_name, p_lat, p_lng, now() + interval '30 minutes')
  on conflict (user_id) do update
    set venue_id = excluded.venue_id, venue_name = excluded.venue_name,
        lat = excluded.lat, lng = excluded.lng,
        expires_at = excluded.expires_at, created_at = now();
  return 'ok';
end;
$$;

-- Prolonge le signal actif de 30 min (1 crédit pour les hommes).
create or replace function public.prolonger_signal()
returns text language plpgsql security definer set search_path = public as $$
declare moi uuid := auth.uid(); prof public.profiles; sig public.signals; gratuit boolean;
begin
  if moi is null then return 'non_connecte'; end if;
  select * into sig from public.signals where user_id = moi and expires_at > now();
  if not found then return 'pas_de_signal'; end if;
  select * into prof from public.profiles where id = moi;
  gratuit := prof.genre in ('femme', 'autre');
  if exists (select 1 from public.event_packs where venue_id = sig.venue_id
             and (expires_at is null or expires_at > now())) then
    gratuit := true;
  end if;
  if not gratuit then
    if prof.credits > 0 then
      update public.profiles set credits = credits - 1 where id = moi;
    else
      return 'paywall';
    end if;
  end if;
  update public.signals set expires_at = expires_at + interval '30 minutes' where user_id = moi;
  return 'ok';
end;
$$;

grant execute on function public.activer_signal(text, text, float8, float8) to authenticated;
grant execute on function public.prolonger_signal() to authenticated;

-- Ajout de crédits après paiement (appelé par le webhook via la clé service).
create or replace function public.ajouter_credits(p_user uuid, p_montant int)
returns void language sql security definer set search_path = public as $$
  update public.profiles set credits = credits + p_montant where id = p_user;
$$;
grant execute on function public.ajouter_credits(uuid, int) to service_role;

-- ===========================================================================
-- Notifications push (étape 4 — suite)
-- ===========================================================================
create table if not exists public.push_subscriptions (
  user_id uuid primary key references auth.users (id) on delete cascade,
  subscription jsonb not null,
  updated_at timestamptz not null default now()
);
alter table public.push_subscriptions enable row level security;
drop policy if exists "push_self" on public.push_subscriptions;
create policy "push_self" on public.push_subscriptions for all
  using (auth.uid() = user_id) with check (auth.uid() = user_id);
