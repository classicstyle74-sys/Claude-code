-- tweets テーブルの作成
create table if not exists public.tweets (
  id          uuid primary key default uuid_generate_v4(),
  user_id     uuid references auth.users(id) on delete cascade not null,
  user_email  text,
  content     text not null check (char_length(content) between 1 and 280),
  created_at  timestamptz default timezone('utc', now()) not null
);

-- Row Level Security を有効化
alter table public.tweets enable row level security;

-- 全員がツイートを読める
create policy "tweets_select_all"
  on public.tweets for select
  using (true);

-- ログイン済みユーザーが自分の user_id で投稿できる
create policy "tweets_insert_own"
  on public.tweets for insert
  with check (auth.uid() = user_id);

-- 自分のツイートのみ削除できる
create policy "tweets_delete_own"
  on public.tweets for delete
  using (auth.uid() = user_id);
