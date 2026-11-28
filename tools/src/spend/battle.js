// Crate Battles: everyone opens the same crates; the side that pulls the most value wins every item opened, paid as coins.
// Play alone against bots, or with friends through a party code (codes start with K). Bots fill empty seats.
//
// Fair without a server: each player's browser picks a secret, publishes only its fingerprint (SHA-256) before the battle,
// and reveals the secret once everyone is locked in. The seed is made from all the secrets together, so no single player,
// not even the host, can steer what anyone pulls; and every browser checks the secrets against their fingerprints.
// Coins: the coins saved in this browser. Signed in to an account, battles are just for fun for now (no coins change).
(() => {
  const $ = s => document.querySelector(s);
  const root = $("#battles");
  if (!root) return;
  const C = window.OTCoins, K = window.Crates, S = window.BJSound;
  const MQTT_SRC = "https://unpkg.com/mqtt@5.10.1/dist/mqtt.min.js";
  const BROKERS = ["wss://broker.emqx.io:8084/mqtt", "wss://broker.hivemq.com:8884/mqtt"];
  const TOPIC = "obscure-trivia/battle/v1/";
  const ALPH = "ABCDEFGHJKMNPQRSTUVWXYZ23456789";
  const MAX_CRATES = 8;
  const esc = s => String(s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const fmt = n => Math.round(n).toLocaleString();
  const calm = () => window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
  const coinsCount = () => !C.user();               // signed in: account coins can only change on the server, so battles are for fun
  const seatsOf = mode => mode === "2v2" ? 4 : 2;
  const randHex = n => Array.from(crypto.getRandomValues(new Uint8Array(n)), b => b.toString(16).padStart(2, "0")).join("");
  const store = (k, v) => { try { if (v === undefined) return localStorage.getItem(k); if (v === null) localStorage.removeItem(k); else localStorage.setItem(k, v); } catch (e) { return null; } };
  const ledger = key => { try { return JSON.parse(store("ot-cb:" + key) || "{}"); } catch (e) { return {}; } };
  const setLedger = (key, v) => store("ot-cb:" + key, JSON.stringify(v));

  let B = { view: "menu", mode: "1v1", counts: { fruit: 1, space: 1, gem: 0, pirate: 0, dragon: 0 }, err: "", busy: false };
  const nick = () => (store("tt-nick") || "").trim().slice(0, 20);
  const crateList = () => K.CRATES.flatMap(c => Array(B.counts[c.id] || 0).fill(c.id));

  // ---------------------------------------------------------------- the menu
  function menu() {
    B.view = "menu"; B.arena = 0;
    root.innerHTML = `
      <div class="panel-head"><h3>Crate Battles</h3><span class="purse" id="cb-coins">${fmt(C.get())}</span></div>
      <p class="muted small" style="margin:0">Everyone opens the same crates. The side that pulls the most value wins every item opened, as coins. 1v1 or 2v2, with friends or bots.</p>
      ${coinsCount() ? "" : `<p class="bj-mode small">You're signed in, so battles are just for fun for now: no coins change.</p>`}
      <label class="cb-field"><span class="muted small">Your name</span><input class="input cb-name" id="cb-name" maxlength="20" placeholder="e.g. Sam" value="${esc(nick())}" autocomplete="nickname"></label>
      <div class="cb-choices">
        <button class="btn gold" id="cb-solo">Battle bots</button>
        <button class="btn" id="cb-host">Battle friends</button>
      </div>
      <form class="cb-join" id="cb-join" autocomplete="off"><input class="input" id="cb-code" maxlength="5" placeholder="CODE" aria-label="Battle code"><button class="btn" type="submit">Join</button></form>
      <p class="err small" id="cb-err" role="alert">${esc(B.err)}</p>
      <details class="bj-rules"><summary>Crates and odds</summary>${oddsTable()}</details>`;
    B.err = "";
    $("#cb-name").oninput = e => store("tt-nick", e.target.value.trim().slice(0, 20));
    const needName = () => { if (nick()) return true; $("#cb-err").textContent = "Type your name first."; $("#cb-name").focus(); return false; };
    $("#cb-solo").onclick = () => { if (needName()) setup("solo"); };
    $("#cb-host").onclick = () => { if (needName()) setup("host"); };
    $("#cb-join").onsubmit = e => {
      e.preventDefault();
      if (!needName()) return;
      const c = normCode($("#cb-code").value);
      if (c.length !== 5 || ![...c].every(ch => ALPH.includes(ch))) { $("#cb-err").textContent = "Codes are 5 letters or numbers, like K7QX2."; return; }
      if (c[0] !== "K") { $("#cb-err").textContent = "Crate battle codes start with K. Other codes belong to a quiz: type them on the home page."; return; }
      join(c);
    };
  }
  function oddsTable() {
    return K.CRATES.map(c => `<div class="cb-odds"><b>${c.icon} ${esc(c.name)}</b> <span class="muted small">${fmt(c.price)} coins · pays back ${(K.ev(c) / c.price * 100).toFixed(1)}% on average</span>
      <ul>${c.items.map((it, i) => `<li class="t-${K.tier(c, it[2])}"><span class="e">${it[0]}</span>${esc(it[1])}<span class="v">${fmt(it[2])}</span><span class="p">${(K.chance(c, i) * 100).toFixed(K.chance(c, i) < 0.01 ? 2 : 1)}%</span></li>`).join("")}</ul></div>`).join("");
  }
  const normCode = s => String(s || "").toUpperCase().replace(/[^A-Z0-9]/g, "").replace(/O/g, "0").replace(/[IL]/g, "1");

  // ---------------------------------------------------------------- choosing the battle (alone, or as the host)
  function setup(role) {
    B.view = "setup"; B.role = role; B.arena = 0;
    const draw = () => {
      const list = crateList(), cost = K.price(list), n = list.length;
      root.innerHTML = `
        <div class="panel-head"><h3>${role === "solo" ? "Battle bots" : "Battle friends"}</h3><span class="purse" id="cb-coins">${fmt(C.get())}</span></div>
        <div class="cb-modes" role="group" aria-label="Mode">${["1v1", "2v2"].map(m => `<button class="btn ${B.mode === m ? "on" : ""}" data-mode="${m}" aria-pressed="${B.mode === m}">${m}</button>`).join("")}</div>
        <p class="muted small" style="margin:0">${B.mode === "1v1" ? "You against one other player." : "Two teams of two. Teammates share the win."}${role === "solo" ? " The other seats are bots." : " Empty seats can be filled with bots."}</p>
        <div class="cb-crates">${K.CRATES.map(c => `<div class="cb-crate"><span class="cb-ci">${c.icon}</span><span class="cb-cn"><b>${esc(c.name)}</b><span class="muted small">${fmt(c.price)} coins</span></span>
          <span class="cb-step"><button class="btn" data-minus="${c.id}" aria-label="One less ${esc(c.name)}" ${B.counts[c.id] ? "" : "disabled"}>−</button><b>${B.counts[c.id] || 0}</b><button class="btn" data-plus="${c.id}" aria-label="One more ${esc(c.name)}" ${n >= MAX_CRATES ? "disabled" : ""}>+</button></span></div>`).join("")}</div>
        <p class="cb-cost"><span>${n} crate${n === 1 ? "" : "s"}</span><b>${fmt(cost)} coins each</b></p>
        <p class="err small" id="cb-err" role="alert">${esc(B.err)}</p>
        <div class="cb-choices"><button class="btn gold" id="cb-go" ${n ? "" : "disabled"}>${role === "solo" ? "Start battle" : "Create battle"}</button><button class="btn" id="cb-back">Back</button></div>`;
      B.err = "";
      root.querySelectorAll("[data-mode]").forEach(b => b.onclick = () => { B.mode = b.dataset.mode; S.play("chip"); draw(); });
      root.querySelectorAll("[data-plus]").forEach(b => b.onclick = () => { if (crateList().length < MAX_CRATES) { B.counts[b.dataset.plus]++; S.wake(); S.play("chip"); } draw(); });
      root.querySelectorAll("[data-minus]").forEach(b => b.onclick = () => { B.counts[b.dataset.minus] = Math.max(0, B.counts[b.dataset.minus] - 1); S.play("chip"); draw(); });
      $("#cb-back").onclick = menu;
      $("#cb-go").onclick = () => {
        S.wake();
        if (coinsCount() && C.get() < cost) { B.err = `This battle costs ${fmt(cost)} coins and you have ${fmt(C.get())}. Win more in any quiz, or pick cheaper crates.`; draw(); return; }
        role === "solo" ? solo() : host();
      };
    };
    draw();
  }

  // ---------------------------------------------------------------- alone against bots
  async function solo() {
    const list = crateList(), cost = K.price(list), n = seatsOf(B.mode);
    const seats = ["me"].concat(Array(n - 1).fill("bot"));
    if (coinsCount()) C.add(-cost);
    const purse = C.get();
    const seed = await K.sha256hex(randHex(32) + "|solo");
    const res = await K.play(seed, B.mode, list);
    if (coinsCount() && res.teams[res.win].includes(0)) C.add(res.share);
    arena({ purse, seats: seats.map((s, i) => s === "me" ? { name: nick() || "You", me: true } : { name: botName(i), bot: true }), list, res, cost, me: 0,
            again: () => { setup("solo"); }, rematch: () => { if (coinsCount() && C.get() < cost) { B.err = `You need ${fmt(cost)} coins for that battle.`; setup("solo"); } else solo(); } });
  }
  const CALLED_OFF = "Someone didn't lock in, so the battle was called off. Everyone who paid got their coins back.";
  const BOTS = ["Bolt", "Pixel", "Nugget", "Sprocket"];
  const botName = i => BOTS[i % BOTS.length];
  // pay out once: a seat on the winning side gets its share (a tie is settled by the seed, like everything else)
  function settle(key, res, mySeat, cost) {
    const L = ledger(key);
    if (L.settled || !coinsCount()) return;
    const won = res.teams[res.win].includes(mySeat);
    if (won) C.add(res.share);
    setLedger(key, Object.assign(L, { settled: 1, won: won ? res.share : 0, cost, t: Date.now() }));
  }

  // ---------------------------------------------------------------- with friends: a party over the same relays as the quizzes
  let net = null;
  async function loadMqtt() {
    if (window.mqtt) return window.mqtt;
    await new Promise((ok, bad) => { const s = document.createElement("script"); s.src = MQTT_SRC; s.onload = ok; s.onerror = bad; document.head.appendChild(s); });
    return window.mqtt;
  }
  function newCode() { const a = crypto.getRandomValues(new Uint32Array(4)); return "K" + Array.from(a, x => ALPH[x % ALPH.length]).join(""); }
  function newPid() { return randHex(6).slice(0, 12).replace(/[^a-z0-9]/g, "0"); }

  // P: everything about the party; peers: what each player has published
  let P = null;
  function freshParty(code, role) {
    return { code, role, pid: newPid(), peers: new Map(), meta: null, n: 0, secret: "", commit: "", j: Date.now(), gone: false, shown: "", note: "" };
  }
  async function connect(onReady) {
    const mqtt = await loadMqtt();
    const cfg = window.TT_MQTT || {};
    const v5 = cfg.protocolVersion !== 4;
    const base = TOPIC + P.code + "/", me = base + P.pid, on = me + "/on";
    const keep = v5 ? { properties: { messageExpiryInterval: 86400 } } : {};
    const opts = { qos: 1, retain: true, ...keep };
    let ready = false;
    const clients = (cfg.brokers || BROKERS).map(url => {
      const c = mqtt.connect(url, { protocolVersion: v5 ? 5 : 4, clientId: "cb_" + P.pid + "_" + randHex(3), clean: true, connectTimeout: 10000, reconnectPeriod: 5000,
                                    keepalive: 30, will: { topic: on, payload: "0", qos: 1, retain: true, ...keep } });
      c.on("connect", () => {
        c.subscribe(base + "#", { qos: 1 }, () => setTimeout(() => { if (!ready) { ready = true; onReady(); } }, 1500));
        c.publish(on, "1", opts);
        publishState(c);
        if (P.role === "host" && P.meta) c.publish(base + "meta", JSON.stringify(P.meta), opts);
      });
      c.on("message", (topic, buf) => onMessage(topic.slice(base.length), buf.toString()));
      c.on("error", () => {});
      return c;
    });
    const each = f => clients.forEach(c => { if (c.connected) f(c); });
    function publishState(only) {
      const s = JSON.stringify({ name: nick() || "Player", j: P.j, n: P.n, commit: P.commit, reveal: P.revealed ? P.secret : "", want: P.want ?? -1,
                                 canPay: !coinsCount() || !!P.revealed || C.get() >= K.price(P.meta ? P.meta.list : []) });
      (only ? [only] : clients.filter(c => c.connected)).forEach(c => c.publish(me, s, opts));
    }
    net = {
      state: () => publishState(),
      meta: m => each(c => c.publish(base + "meta", JSON.stringify(m), opts)),
      close: remove => clients.forEach(c => { try { if (c.connected) { if (remove) { c.publish(me, "", { qos: 1, retain: true }); c.publish(on, "", { qos: 1, retain: true }); } else c.publish(on, "0", opts); } c.end(false); } catch (e) {} }),
      live: () => clients.some(c => c.connected),
    };
    setTimeout(() => { if (!ready && P && !P.gone) { ready = true; onReady(); } }, 9000);
  }
  function onMessage(path, text) {
    if (!P || P.gone) return;
    const [id, sub] = path.split("/");
    if (id === "meta" && !sub) {
      if (!text) return;
      let m; try { m = JSON.parse(text); } catch (e) { return; }
      if (!m || !Array.isArray(m.seats)) return;
      if (P.role === "host" && m.host === P.pid) return;          // my own echo
      P.meta = m; changed(); return;
    }
    if (!/^[a-z0-9]{12}$/.test(id) || id === P.pid) return;
    const p = P.peers.get(id) || { on: "1" };
    if (sub === "on") p.on = text;
    else if (!sub) { if (!text) { P.peers.delete(id); changed(); return; } try { Object.assign(p, JSON.parse(text)); } catch (e) { return; } }
    else return;
    P.peers.set(id, p); changed();
  }

  function host() {
    const list = crateList();
    P = freshParty(newCode(), "host");
    P.meta = { v: 1, host: P.pid, mode: B.mode, list, seats: [P.pid].concat(Array(seatsOf(B.mode) - 1).fill(null)), phase: "lobby", n: 1, names: {} };
    P.n = 1; P.ok = true; newSecret();
    B.view = "lobby"; lobby();
    connect(() => { hostTick(); if (B.view === "lobby") lobby(); });
  }
  async function join(code) {
    const btn = root.querySelector("#cb-join button"); if (btn) { btn.disabled = true; btn.textContent = "Checking…"; }
    P = freshParty(code, "guest");
    try { await connect(() => admit(true)); } catch (e) { P = null; B.err = "Couldn't reach the party server. Check your internet connection and try again."; menu(); }
  }
  // a guest is let in as soon as the host's open battle shows up; `final` once the relays have sent everything they hold
  function admit(final) {
    if (!P || P.gone || P.ok) return;
    const m = P.meta, hostOn = m && (P.peers.get(m.host) || {}).on === "1";
    if (m && hostOn && m.phase === "lobby") { P.ok = true; P.n = m.n; newSecret(); B.view = "lobby"; lobby(); return; }
    if (!final) return;
    if (!net || !net.live()) { leave(false); B.err = "Couldn't reach the party server. Check your internet connection and try again."; menu(); return; }
    if (!m || !hostOn || m.phase === "closed") { leave(true); B.err = "Incorrect code. There's no battle with that code right now."; menu(); return; }
    leave(true); B.err = "That battle has already started."; menu();
  }
  function newSecret() {
    const mine = P, secret = randHex(32);
    P.secret = secret; P.revealed = false; P.commit = "";
    K.sha256hex(secret).then(h => { if (P === mine && P.secret === secret) { P.commit = h; if (net) net.state(); if (B.view === "lobby") lobby(); } });
  }
  function leave(remove) { if (P) { P.gone = true; if (net) net.close(remove); } net = null; P = null; }

  // the host keeps the seating up to date and runs the battle's steps
  function hostTick() {
    if (!P || P.role !== "host" || !net) return;
    const m = P.meta;
    let dirty = false;
    if (m.phase === "lobby") {
      const live = id => id === P.pid || ((P.peers.get(id) || {}).on === "1" && (P.peers.get(id) || {}).name);
      m.seats = m.seats.map(s => s && s !== "bot" && !live(s) ? (dirty = true, null) : s);
      const seated = new Set(m.seats);
      const waiting = [...P.peers.entries()].filter(([id, p]) => p.on === "1" && p.name && !seated.has(id)).sort((a, b) => a[1].j - b[1].j);
      for (const [id, p] of waiting) {
        let at = Number.isInteger(p.want) && m.seats[p.want] === null ? p.want : m.seats.indexOf(null);
        if (at >= 0) { m.seats[at] = id; dirty = true; }
      }
      // a seated player asking to move to an empty seat
      m.seats.forEach((id, i) => { const p = P.peers.get(id); if (p && Number.isInteger(p.want) && p.want !== i && m.seats[p.want] === null) { m.seats[p.want] = id; m.seats[i] = null; dirty = true; } });
      const names = {}; m.seats.forEach(id => { if (id && id !== "bot") names[id] = id === P.pid ? nick() || "Host" : (P.peers.get(id) || {}).name || "Player"; });
      if (JSON.stringify(names) !== JSON.stringify(m.names)) { m.names = names; dirty = true; }
    } else if (m.phase === "reveal") {
      const humans = m.seats.filter(s => s !== "bot");
      const reveals = {};
      for (const id of humans) {
        const r = id === P.pid ? (P.revealed ? P.secret : "") : (P.peers.get(id) || {}).reveal;
        if (!r || (P.peers.get(id) || {}).n !== undefined && id !== P.pid && (P.peers.get(id) || {}).n !== m.n) break;
        reveals[id] = r;
      }
      if (Object.keys(reveals).length === humans.length) {
        Promise.all(humans.map(id => K.sha256hex(reveals[id]))).then(hs => {
          if (P.meta.phase !== "reveal") return;
          if (hs.every((h, i) => h === m.commits[humans[i]])) { m.phase = "battle"; m.reveals = reveals; m.startAt = Date.now() + 1200; }
          else m.phase = "cancelled";
          net.meta(m); changed();
        });
      } else if (Date.now() > m.revealBy) { m.phase = "cancelled"; dirty = true; }
    }
    if (dirty) { net.meta(m); }
  }
  function hostStart() {
    const m = P.meta;
    const humans = m.seats.filter(s => s !== "bot");
    const commits = {};
    for (const id of humans) {
      const c = id === P.pid ? P.commit : (P.peers.get(id) || {}).commit;
      if (!c) return;
      commits[id] = c;
    }
    m.phase = "reveal"; m.commits = commits; m.revealBy = Date.now() + 20000;
    net.meta(m); changed();
    setTimeout(() => { if (P && P.meta === m && m.phase === "reveal") changed(); }, 20500);
  }

  // something changed in the party: move each player through the battle's steps
  function changed() {
    if (!P) return;
    if (!P.ok) return admit(false);
    if (P.role === "host") hostTick();
    const m = P.meta;
    if (!m) return;
    const key = P.code + ":" + m.n;
    const mySeat = m.seats.indexOf(P.pid);
    if (P.role === "guest" && m.phase === "closed") { leave(false); B.err = "The host closed this battle."; menu(); return; }
    if (P.role === "guest" && (P.peers.get(m.host) || {}).on === "0" && m.phase !== "battle") { leave(false); B.err = "The host left, so the battle is off."; menu(); return; }
    if (m.n !== P.n) {                                          // the next battle: a fresh secret for it
      const old = ledger(P.code + ":" + P.n);                    // (and coins back if the last one was called off while I was away)
      if (old.paid && !old.refunded && !old.settled && m.prev && m.prev.n === P.n && m.prev.cancelled) { C.add(old.paid); setLedger(P.code + ":" + P.n, Object.assign(old, { refunded: 1 })); P.note = CALLED_OFF; }
      P.n = m.n; newSecret();
    }
    if (m.phase !== "lobby") P.note = m.phase === "cancelled" ? P.note : "";
    if (m.phase === "reveal" && mySeat >= 0 && !P.revealed) {
      if (m.commits[P.pid] !== P.commit) return;
      const L = ledger(key), cost = K.price(m.list);
      if (!L.paid && coinsCount()) {
        if (C.get() < cost) { lobby("You don't have enough coins for this battle any more."); return; }
        C.add(-cost); setLedger(key, { paid: cost, t: Date.now() });
      }
      P.revealed = true; net.state();
      if (P.role === "host") setTimeout(hostTick, 0);           // the host doesn't hear its own messages
    }
    if (m.phase === "cancelled") {
      const L = ledger(key);
      if (L.paid && !L.refunded && !L.settled) { C.add(L.paid); setLedger(key, Object.assign(L, { refunded: 1 })); }
      if (P.shown !== "cancel:" + m.n) {
        P.shown = "cancel:" + m.n; P.note = CALLED_OFF; lobby();
        // the host opens the lobby again for another try, with fresh secrets all round
        if (P.role === "host") setTimeout(() => {
          if (!P || P.meta !== m || m.phase !== "cancelled") return;
          Object.assign(m, { phase: "lobby", n: m.n + 1, commits: null, reveals: null, prev: { n: m.n, cancelled: 1 } });
          P.n = m.n; newSecret(); net.meta(m); P.shown = ""; lobby();
        }, 1500);
      }
      return;
    }
    if (m.phase === "battle" && P.shown !== "battle:" + m.n) { P.shown = "battle:" + m.n; runParty(m, key, mySeat); return; }
    if (m.phase === "lobby" && (B.view !== "arena" || P.shown === "battle:" + (m.n - 1))) { P.shown = ""; lobby(); }
  }
  async function runParty(m, key, mySeat) {
    // check every secret against the fingerprint its owner published, then make the seed from all of them
    const humans = m.seats.filter(s => s !== "bot");
    for (const id of humans) {
      const own = id === P.pid ? P.commit : (P.peers.get(id) || {}).commit;
      if ((await K.sha256hex(m.reveals[id] || "")) !== (own || m.commits[id])) { lobby("This battle's results didn't check out, so it was called off."); return; }
    }
    const seed = await K.sha256hex(m.seats.map(s => s === "bot" ? "bot" : m.reveals[s]).join("|") + "|" + P.code + "|" + m.n);
    const res = await K.play(seed, m.mode, m.list);
    const cost = K.price(m.list), purse = C.get() - (ledger(key).won || 0);
    if (mySeat >= 0) settle(key, res, mySeat, cost);
    const wait = Math.max(0, (m.startAt || 0) - Date.now());
    setTimeout(() => {
      if (!P) return;
      arena({ purse, seats: m.seats.map((s, i) => s === "bot" ? { name: botName(i), bot: true } : { name: (m.names || {})[s] || "Player", me: s === P.pid }), list: m.list, res, cost, me: mySeat,
              again: P.role === "host" ? () => { P.meta = Object.assign(P.meta, { phase: "lobby", n: m.n + 1, commits: null, reveals: null, prev: { n: m.n } }); P.n = m.n + 1; newSecret(); net.meta(P.meta); P.shown = ""; lobby(); } : null,
              leave: () => { leave(P.role === "guest"); menu(); } });
    }, Math.min(wait, 2000));
  }

  // ---------------------------------------------------------------- the lobby
  function lobby(note) {
    if (!P) return menu();
    B.view = "lobby";
    const m = P.meta; B.arena = 0;
    if (!m) { root.innerHTML = `<p class="muted">Connecting…</p>`; return; }
    const isHost = P.role === "host", mySeat = m.seats.indexOf(P.pid), cost = K.price(m.list);
    const teams = K.TEAMS[m.mode];
    const nameOf = id => id === P.pid ? (nick() || "You") : (m.names || {})[id] || (P.peers.get(id) || {}).name || "Player";
    const pays = id => id === "bot" || (id === P.pid ? !coinsCount() || P.revealed || C.get() >= cost : (P.peers.get(id) || {}).canPay !== false);
    const ready = id => id === "bot" || !!((id === P.pid ? P.commit : (P.peers.get(id) || {}).commit) && pays(id));
    const seat = i => {
      const id = m.seats[i];
      if (id === "bot") return `<div class="cb-seat bot"><span>🤖 ${esc(botName(i))}</span>${isHost && m.phase === "lobby" ? `<button class="btn" data-unbot="${i}">Remove</button>` : ""}</div>`;
      if (id) return `<div class="cb-seat${id === P.pid ? " me" : ""}"><span>${esc(nameOf(id))}${id === P.pid ? " (you)" : ""}${id === m.host ? ' <span class="muted small">host</span>' : ""}</span>${ready(id) ? "" : pays(id) ? '<span class="muted small">…</span>' : '<span class="muted small cb-broke">needs coins</span>'}</div>`;
      return `<div class="cb-seat empty"><span class="muted">Empty seat</span><span class="row">${mySeat !== i && m.phase === "lobby" ? `<button class="btn" data-sit="${i}">Sit here</button>` : ""}${isHost && m.phase === "lobby" ? `<button class="btn" data-bot="${i}">Add bot</button>` : ""}</span></div>`;
    };
    const full = m.seats.every(Boolean), allReady = m.seats.every(ready);
    const canStart = isHost && m.phase === "lobby" && full && allReady;
    root.innerHTML = `
      <div class="panel-head"><h3>Crate Battle · ${esc(m.mode)}</h3><span class="purse" id="cb-coins">${fmt(C.get())}</span></div>
      <div class="cb-code"><span class="muted small">Battle code</span><b id="cb-codev">${esc(P.code)}</b><button class="btn" id="cb-copy">Copy</button></div>
      <p class="muted small" style="margin:0">Friends open the Spend coins page, choose Crate Battles and type this code, or type it on the home page.</p>
      <div class="cb-teams ${m.mode}">${teams.map((t, ti) => `<div class="cb-team t${ti}">${teams.length > 1 ? `<span class="cb-tl">${m.mode === "2v2" ? "Team " + "AB"[ti] : ti ? "Side 2" : "Side 1"}</span>` : ""}${t.map(seat).join("")}</div>`).join('<span class="cb-vs">VS</span>')}</div>
      <p class="cb-list">${m.list.map(id => `<span title="${esc(K.BY_ID[id].name)}">${K.BY_ID[id].icon}</span>`).join("")}<b>${fmt(cost)} coins each</b></p>
      ${mySeat >= 0 && m.phase === "lobby" && !pays(P.pid) ? `<p class="bj-mode small">This battle costs ${fmt(cost)} coins and you have ${fmt(C.get())}. Win more in any quiz, then come back.</p>` : ""}
      ${mySeat < 0 && m.phase === "lobby" && m.seats.every(Boolean) ? `<p class="bj-mode small">This battle is full. You can watch, or leave and start your own.</p>` : ""}
      <p class="err small" id="cb-err" role="alert">${esc(note || P.note || "")}</p>
      <div class="cb-choices">${isHost ? `<button class="btn gold" id="cb-start" ${canStart ? "" : "disabled"}>${m.phase === "reveal" ? "Locking in…" : full ? (allReady ? "Start battle" : "Waiting for players…") : "Fill every seat to start"}</button>` :
        `<span class="muted small">${m.phase === "reveal" ? "Locking in…" : "Waiting for the host to start…"}</span>`}<button class="btn" id="cb-leave">Leave</button></div>`;
    $("#cb-copy").onclick = () => { try { navigator.clipboard.writeText(P.code); $("#cb-copy").textContent = "Copied"; } catch (e) {} };
    $("#cb-leave").onclick = () => {
      if (isHost && (P.meta.phase === "lobby" || P.meta.phase === "cancelled")) { P.meta.phase = "closed"; net.meta(P.meta); }
      leave(true); menu();
    };
    root.querySelectorAll("[data-bot]").forEach(b => b.onclick = () => { m.seats[+b.dataset.bot] = "bot"; net.meta(m); S.play("chip"); lobby(); });
    root.querySelectorAll("[data-unbot]").forEach(b => b.onclick = () => { m.seats[+b.dataset.unbot] = null; hostTick(); net.meta(m); lobby(); });
    root.querySelectorAll("[data-sit]").forEach(b => b.onclick = () => {
      const i = +b.dataset.sit;
      if (isHost) { const at = m.seats.indexOf(P.pid); m.seats[i] = P.pid; if (at >= 0) m.seats[at] = null; net.meta(m); lobby(); }
      else { P.want = i; net.state(); }
    });
    const st = $("#cb-start"); if (st) st.onclick = () => { if (canStart) { S.wake(); S.play("chip"); hostStart(); } };
  }

  // ---------------------------------------------------------------- the arena: every seat's reel spins for each crate
  function arena({ purse, seats, list, res, cost, me, again, rematch, leave: onLeave }) {
    B.view = "arena";
    const token = B.arena = Math.random(), alive = () => B.arena === token && B.view === "arena";
    const teams = res.teams, totals = seats.map(() => 0);
    root.innerHTML = `
      <div class="panel-head"><h3>Crate Battle</h3><span class="purse" id="cb-coins">${fmt(purse ?? C.get())}</span></div>
      <p class="cb-round" id="cb-round">Get ready…</p>
      <div class="cb-arena n${seats.length}">${teams.map((t, ti) => `<div class="cb-side t${ti}">${t.map(s => `
        <div class="cb-col${seats[s].me ? " me" : ""}" id="cb-col${s}">
          <div class="cb-who">${seats[s].bot ? "🤖 " : ""}${esc(seats[s].name)}</div>
          <div class="cb-total" id="cb-tot${s}">0</div>
          <div class="cb-reel"><div class="cb-strip" id="cb-strip${s}"></div></div>
          <ul class="cb-got" id="cb-got${s}"></ul>
        </div>`).join("")}</div>`).join('<span class="cb-vs">VS</span>')}</div>
      <p class="cb-result" id="cb-result" role="status" aria-live="polite"></p>
      <div class="cb-choices" id="cb-after"></div>`;
    const ITEM_H = 64, STOP = 26;
    let r = 0;
    const spin = () => {
      if (!alive()) return;
      if (r >= list.length) return finish();
      const c = K.BY_ID[list[r]];
      $("#cb-round").innerHTML = `Crate ${r + 1} of ${list.length} · ${c.icon} <b>${esc(c.name)}</b>`;
      const dur = calm() ? 250 : 2300;
      seats.forEach((_, s) => {
        const strip = $("#cb-strip" + s), got = res.pulls[r][s];
        const cells = [];
        for (let k = 0; k < STOP + 3; k++) {
          const i = k === STOP ? got.i : K.pick(c, Math.random());
          cells.push(`<div class="cb-cell t-${K.tier(c, c.items[i][2])}"><span>${c.items[i][0]}</span></div>`);
        }
        strip.style.transition = "none"; strip.style.transform = "translateY(0)";
        strip.innerHTML = cells.join("");
        void strip.offsetWidth;
        strip.style.transition = `transform ${dur + s * 120}ms cubic-bezier(.12, .7, .14, 1)`;
        strip.style.transform = `translateY(${-(STOP * ITEM_H - ITEM_H * 0.5)}px)`;
      });
      if (!calm()) { let t = 0; const tick = () => { if (t > dur - 300) return; S.play("tick"); t += 70 + t / 9; setTimeout(tick, 70 + t / 9); }; tick(); }
      setTimeout(() => {
        if (!alive()) return;
        let best = 0;
        seats.forEach((_, s) => {
          const got = res.pulls[r][s], it = c.items[got.i];
          totals[s] += got.v;
          $("#cb-tot" + s).textContent = fmt(totals[s]);
          const tierName = K.tier(c, it[2]);
          $("#cb-got" + s).insertAdjacentHTML("beforeend", `<li class="t-${tierName}" title="${esc(it[1])}"><span>${it[0]}</span>${fmt(it[2])}</li>`);
          if (tierName === "legendary") { best = 2; $("#cb-col" + s).classList.add("flash"); setTimeout(() => $("#cb-col" + s) && $("#cb-col" + s).classList.remove("flash"), 900); }
          else if (tierName === "epic") best = Math.max(best, 1);
        });
        S.play(best === 2 ? "blackjack" : best === 1 ? "win" : "flip");
        leadGlow();
        r++;
        setTimeout(spin, calm() ? 200 : 900);
      }, dur + seats.length * 120);
    };
    const leadGlow = () => {
      const tt = teams.map(t => t.reduce((n, s) => n + totals[s], 0)), top = Math.max(...tt);
      teams.forEach((t, ti) => t.forEach(s => $("#cb-col" + s).classList.toggle("lead", tt[ti] === top && top > 0 && tt.filter(v => v === top).length === 1)));
    };
    const finish = () => {
      const myTeam = me >= 0 ? teams.findIndex(t => t.includes(me)) : -1, won = myTeam === res.win;
      teams.forEach((t, ti) => t.forEach(s => { const col = $("#cb-col" + s); col.classList.remove("lead"); col.classList.add(ti === res.win ? "won" : "lost"); }));
      const who = teams[res.win].map(s => seats[s].name).join(" and ");
      const tie = res.tie ? " It was a tie, settled by the shared random seed." : "";
      let msg;
      if (me < 0) msg = `${who} win${teams[res.win].length > 1 ? "" : "s"} ${fmt(res.pot)} coins' worth.${tie}`;
      else if (!coinsCount()) msg = (won ? "You win! " : `${who} win${teams[res.win].length > 1 ? "" : "s"}. `) + "Just for fun: no coins changed." + tie;
      else if (won) msg = `You win ${fmt(res.share)} coins! You paid ${fmt(cost)}, so that's ${res.share - cost >= 0 ? "+" : ""}${fmt(res.share - cost)}.${tie}`;
      else msg = `${who} win${teams[res.win].length > 1 ? "" : "s"}. You lose ${fmt(cost)} coins.${tie}`;
      $("#cb-result").className = "cb-result " + (me < 0 ? "" : won ? "win" : "lose");
      $("#cb-result").textContent = msg;
      $("#cb-round").textContent = `Total opened: ${fmt(res.pot)} coins' worth`;
      $("#cb-coins").textContent = fmt(C.get());
      S.play(me < 0 ? "push" : won ? "blackjack" : "lose");
      const after = $("#cb-after");
      after.innerHTML = (rematch ? `<button class="btn gold" id="cb-re">Battle again (${fmt(cost)} coins)</button><button class="btn" id="cb-change">Change crates</button>` :
        again ? `<button class="btn gold" id="cb-re">Battle again</button>` : `<span class="muted small">The host can start another battle.</span>`) +
        `<button class="btn" id="cb-out">${onLeave ? "Leave" : "Back"}</button>`;
      const re = $("#cb-re"); if (re) re.onclick = () => { S.wake(); (rematch || again)(); };
      const ch = $("#cb-change"); if (ch) ch.onclick = () => again();
      $("#cb-out").onclick = () => onLeave ? onLeave() : menu();
    };
    setTimeout(spin, calm() ? 100 : 700);
  }

  // coins changing elsewhere (another tab, a quiz)
  C.on(() => {
    const el = $("#cb-coins"); if (el && B.view !== "arena") el.textContent = fmt(C.get());
    if (P && net && P.meta && P.meta.phase === "lobby" && B.view === "lobby") { net.state(); lobby(); }
  });
  window.addEventListener("pagehide", () => { if (P) leave(P.role === "guest" && P.meta && P.meta.phase === "lobby"); });
  try { Object.keys(localStorage).filter(k => k.startsWith("ot-cb:")).forEach(k => { const v = ledger(k.slice(6)); if (!v.t || v.t < Date.now() - 7 * 864e5) localStorage.removeItem(k); }); } catch (e) {}
  window.CrateBattles = { join: code => { join(normCode(code)); }, menu };
  menu();
})();
