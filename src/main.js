import { supabase } from './supabaseClient.js'

let currentUser = null

async function init() {
  const { data: { session } } = await supabase.auth.getSession()
  currentUser = session?.user ?? null

  supabase.auth.onAuthStateChange((_event, session) => {
    currentUser = session?.user ?? null
    render()
  })

  render()
}

function render() {
  const app = document.getElementById('app')
  if (currentUser) {
    app.innerHTML = renderFeed()
    setupFeedListeners()
    loadTweets()
  } else {
    app.innerHTML = renderAuth()
    setupAuthListeners()
  }
}

function renderAuth() {
  return `
    <div class="container">
      <h1 class="logo">🐦 つぶやき</h1>
      <div class="auth-box">
        <div class="auth-tabs">
          <button id="tab-login" class="tab active">ログイン</button>
          <button id="tab-signup" class="tab">新規登録</button>
        </div>
        <div class="auth-form">
          <input type="email" id="email" placeholder="メールアドレス" autocomplete="email" />
          <input type="password" id="password" placeholder="パスワード（6文字以上）" autocomplete="current-password" />
          <button id="auth-btn" class="btn-primary">ログイン</button>
          <p id="auth-message" class="message"></p>
        </div>
      </div>
    </div>
  `
}

function renderFeed() {
  const email = currentUser.email || ''
  const displayName = email.split('@')[0]
  return `
    <div class="container">
      <header class="header">
        <h1 class="logo">🐦 つぶやき</h1>
        <div class="user-info">
          <span class="user-name">@${displayName}</span>
          <button id="logout-btn" class="btn-logout">ログアウト</button>
        </div>
      </header>
      <div class="post-form">
        <textarea id="tweet-input" placeholder="今何してる？" maxlength="280"></textarea>
        <div class="post-footer">
          <span id="char-count" class="char-count">280</span>
          <button id="post-btn" class="btn-primary">投稿</button>
        </div>
      </div>
      <div id="tweets-container" class="tweets-container">
        <p class="loading">読み込み中...</p>
      </div>
    </div>
  `
}

function setupAuthListeners() {
  let isLogin = true

  document.getElementById('tab-login').addEventListener('click', () => {
    isLogin = true
    document.getElementById('tab-login').classList.add('active')
    document.getElementById('tab-signup').classList.remove('active')
    document.getElementById('auth-btn').textContent = 'ログイン'
    document.getElementById('auth-message').textContent = ''
  })

  document.getElementById('tab-signup').addEventListener('click', () => {
    isLogin = false
    document.getElementById('tab-signup').classList.add('active')
    document.getElementById('tab-login').classList.remove('active')
    document.getElementById('auth-btn').textContent = '登録する'
    document.getElementById('auth-message').textContent = ''
  })

  document.getElementById('auth-btn').addEventListener('click', async () => {
    const email = document.getElementById('email').value.trim()
    const password = document.getElementById('password').value
    const messageEl = document.getElementById('auth-message')

    if (!email || !password) {
      showMessage(messageEl, 'メールアドレスとパスワードを入力してください', 'error')
      return
    }

    const btn = document.getElementById('auth-btn')
    btn.disabled = true
    btn.textContent = '処理中...'

    try {
      if (isLogin) {
        const { error } = await supabase.auth.signInWithPassword({ email, password })
        if (error) showMessage(messageEl, 'ログインに失敗しました: ' + error.message, 'error')
      } else {
        const { error } = await supabase.auth.signUp({ email, password })
        if (error) {
          showMessage(messageEl, '登録に失敗しました: ' + error.message, 'error')
        } else {
          showMessage(messageEl, '確認メールを送信しました。メールを確認してください。', 'success')
        }
      }
    } finally {
      btn.disabled = false
      btn.textContent = isLogin ? 'ログイン' : '登録する'
    }
  })

  document.getElementById('email').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') document.getElementById('password').focus()
  })
  document.getElementById('password').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') document.getElementById('auth-btn').click()
  })
}

function setupFeedListeners() {
  document.getElementById('logout-btn').addEventListener('click', async () => {
    await supabase.auth.signOut()
  })

  const input = document.getElementById('tweet-input')
  const charCount = document.getElementById('char-count')
  const postBtn = document.getElementById('post-btn')

  input.addEventListener('input', () => {
    const remaining = 280 - input.value.length
    charCount.textContent = remaining
    charCount.classList.toggle('warning', remaining < 20)
  })

  postBtn.addEventListener('click', () => postTweet())

  input.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') postTweet()
  })
}

async function postTweet() {
  const input = document.getElementById('tweet-input')
  const content = input.value.trim()
  if (!content) return

  const btn = document.getElementById('post-btn')
  btn.disabled = true

  const { error } = await supabase.from('tweets').insert({
    content,
    user_id: currentUser.id,
    user_email: currentUser.email
  })

  btn.disabled = false

  if (!error) {
    input.value = ''
    document.getElementById('char-count').textContent = '280'
    loadTweets()
  } else {
    console.error('投稿エラー:', error)
  }
}

async function loadTweets() {
  const container = document.getElementById('tweets-container')
  if (!container) return

  const { data, error } = await supabase
    .from('tweets')
    .select('*')
    .order('created_at', { ascending: false })
    .limit(50)

  if (error) {
    container.innerHTML = '<p class="error-msg">ツイートの読み込みに失敗しました</p>'
    return
  }

  if (!data.length) {
    container.innerHTML = '<p class="empty">まだつぶやきがありません。最初のつぶやきをしてみよう！</p>'
    return
  }

  container.innerHTML = data.map(tweet => {
    const displayName = (tweet.user_email || '').split('@')[0] || tweet.user_id.slice(0, 8)
    const isOwn = tweet.user_id === currentUser.id
    return `
      <div class="tweet" data-id="${tweet.id}">
        <div class="tweet-header">
          <span class="tweet-user">@${escapeHtml(displayName)}</span>
          <span class="tweet-time">${formatDate(tweet.created_at)}</span>
          ${isOwn ? `<button class="btn-delete" data-id="${tweet.id}">削除</button>` : ''}
        </div>
        <div class="tweet-content">${escapeHtml(tweet.content)}</div>
      </div>
    `
  }).join('')

  container.querySelectorAll('.btn-delete').forEach(btn => {
    btn.addEventListener('click', async () => {
      const id = btn.dataset.id
      const { error } = await supabase.from('tweets').delete().eq('id', id).eq('user_id', currentUser.id)
      if (!error) loadTweets()
    })
  })
}

function showMessage(el, text, type) {
  el.textContent = text
  el.className = 'message ' + type
}

function escapeHtml(str) {
  const div = document.createElement('div')
  div.textContent = str
  return div.innerHTML
}

function formatDate(dateStr) {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now - date
  if (diff < 60000) return 'たった今'
  if (diff < 3600000) return Math.floor(diff / 60000) + '分前'
  if (diff < 86400000) return Math.floor(diff / 3600000) + '時間前'
  return date.toLocaleDateString('ja-JP', { month: 'short', day: 'numeric' })
}

init()
