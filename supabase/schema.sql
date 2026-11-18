-- Run this file once in Supabase Dashboard > SQL Editor.
-- It is safe to run again: tables and policies are created idempotently.

create extension if not exists pgcrypto;

create table if not exists public.categories (
    id bigint generated always as identity primary key,
    name text not null unique,
    created_at timestamptz not null default now()
);

create table if not exists public.books (
    id bigint generated always as identity primary key,
    upc text not null unique,
    category_id bigint not null references public.categories(id),
    title text not null,
    description text,
    product_url text not null,
    image_url text not null,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists public.scrape_runs (
    id uuid primary key default gen_random_uuid(),
    status text not null default 'running'
        check (status in ('running', 'completed', 'failed')),
    started_at timestamptz not null default now(),
    completed_at timestamptz,
    requested_max_books integer check (requested_max_books is null or requested_max_books > 0),
    requested_max_pages integer check (requested_max_pages is null or requested_max_pages > 0),
    books_found integer check (books_found is null or books_found >= 0),
    error_message text
);

create table if not exists public.book_observations (
    id bigint generated always as identity primary key,
    book_id bigint not null references public.books(id) on delete cascade,
    scrape_run_id uuid not null references public.scrape_runs(id) on delete cascade,
    scraped_at timestamptz not null,
    price_excl_tax_gbp numeric(10, 2) not null check (price_excl_tax_gbp >= 0),
    price_incl_tax_gbp numeric(10, 2) not null check (price_incl_tax_gbp >= 0),
    tax_gbp numeric(10, 2) not null check (tax_gbp >= 0),
    availability_text text not null,
    stock_count integer not null check (stock_count >= 0),
    rating smallint not null check (rating between 0 and 5),
    number_of_reviews integer not null check (number_of_reviews >= 0),
    unique (book_id, scrape_run_id)
);

create index if not exists books_category_id_idx on public.books(category_id);
create index if not exists books_title_lower_idx on public.books(lower(title));
create index if not exists observations_book_scraped_idx
    on public.book_observations(book_id, scraped_at desc);
create index if not exists observations_run_idx
    on public.book_observations(scrape_run_id);

create or replace function public.set_updated_at()
returns trigger
language plpgsql
set search_path = ''
as $$
begin
    new.updated_at = now();
    return new;
end;
$$;

drop trigger if exists books_set_updated_at on public.books;
create trigger books_set_updated_at
before update on public.books
for each row execute function public.set_updated_at();

-- A convenient read-only view containing the newest observation for every book.
create or replace view public.current_books
with (security_invoker = true)
as
select
    b.id,
    b.upc,
    b.title,
    c.name as category,
    b.description,
    b.product_url,
    b.image_url,
    o.price_excl_tax_gbp,
    o.price_incl_tax_gbp,
    o.tax_gbp,
    o.availability_text,
    o.stock_count,
    o.rating,
    o.number_of_reviews,
    o.scraped_at
from public.books b
join public.categories c on c.id = b.category_id
left join lateral (
    select observation.*
    from public.book_observations observation
    where observation.book_id = b.id
    order by observation.scraped_at desc
    limit 1
) o on true;

-- Protect every table. Browser users may read catalogue data but cannot write it.
alter table public.categories enable row level security;
alter table public.books enable row level security;
alter table public.scrape_runs enable row level security;
alter table public.book_observations enable row level security;

revoke all on public.categories, public.books, public.scrape_runs,
    public.book_observations from anon, authenticated;
grant select on public.categories, public.books, public.book_observations
    to anon, authenticated;
grant select on public.current_books to anon, authenticated;
grant select on public.current_books to service_role;

drop policy if exists "public read categories" on public.categories;
create policy "public read categories" on public.categories
    for select to anon, authenticated using (true);

drop policy if exists "public read books" on public.books;
create policy "public read books" on public.books
    for select to anon, authenticated using (true);

drop policy if exists "public read observations" on public.book_observations;
create policy "public read observations" on public.book_observations
    for select to anon, authenticated using (true);

grant all on public.categories, public.books, public.scrape_runs,
    public.book_observations to service_role;
grant usage, select on all sequences in schema public to service_role;

