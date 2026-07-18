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
