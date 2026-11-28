// Table sounds for blackjack and crate battles, made on the fly with the Web Audio API (no sound files): a card flicked out of the shoe, a card
// turned over, cards slid apart, a knock on the felt, chips, and short win / lose cues. Muting is remembered in this browser.
window.BJSound = (() => {
  const KEY = "ot-bj-sound";
  let ctx = null, noiseBuf = null, master = null;
  let on = true;
  try { on = localStorage.getItem(KEY) !== "off"; } catch (e) {}

  function ac() {
    if (!ctx) {
      const A = window.AudioContext || window.webkitAudioContext;
      if (!A) return null;
      ctx = new A();
      master = ctx.createGain(); master.gain.value = 0.9; master.connect(ctx.destination);
      noiseBuf = ctx.createBuffer(1, ctx.sampleRate * 0.5, ctx.sampleRate);
      const d = noiseBuf.getChannelData(0);
      for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1;
    }
    if (ctx.state === "suspended") ctx.resume();
    return ctx;
  }
  // a burst of filtered noise: the papery part of every card sound
  function hiss(t0, dur, freq, q, gain, to) {
    const c = ctx, t = c.currentTime + t0;
    const src = c.createBufferSource(); src.buffer = noiseBuf;
    const f = c.createBiquadFilter(); f.type = "bandpass"; f.Q.value = q; f.frequency.setValueAtTime(freq, t);
    if (to) f.frequency.exponentialRampToValueAtTime(to, t + dur);
    const g = c.createGain();
    g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(gain, t + 0.006); g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    src.connect(f); f.connect(g); g.connect(master);
    src.start(t, Math.random() * 0.3); src.stop(t + dur + 0.02);
  }
  // a short pitched sound: knocks, chips and chimes
  function tone(t0, dur, freq, gain, type, to) {
    const c = ctx, t = c.currentTime + t0;
    const o = c.createOscillator(); o.type = type || "sine"; o.frequency.setValueAtTime(freq, t);
    if (to) o.frequency.exponentialRampToValueAtTime(to, t + dur);
    const g = c.createGain();
    g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(gain, t + 0.005); g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    o.connect(g); g.connect(master); o.start(t); o.stop(t + dur + 0.02);
  }
  const vary = (x, by) => x * (1 + (Math.random() - 0.5) * by);
  const FX = {
    // flicked out of the shoe, a swish, then the soft slap of landing on the felt
    deal() { hiss(0, 0.11, vary(5200, 0.15), 0.9, 0.22, 1700); hiss(0.085, 0.06, vary(1100, 0.2), 1.1, 0.42); tone(0.085, 0.05, vary(170, 0.1), 0.18, "sine", 90); },
    // turned over in place: a crisp snap
    flip() { hiss(0, 0.05, vary(3800, 0.1), 1.6, 0.4, 2600); hiss(0.03, 0.05, 1500, 1.2, 0.22); },
    // slid across the felt: standing tucks the cards, splitting slides one away
    slide() { hiss(0, 0.22, vary(2600, 0.1), 0.7, 0.16, 900); },
    // two knuckle taps on the table
    knock() { tone(0, 0.09, 150, 0.5, "sine", 80); hiss(0, 0.03, 700, 1, 0.2); tone(0.14, 0.09, 140, 0.42, "sine", 75); hiss(0.14, 0.03, 650, 1, 0.16); },
    // chips clicking together
    chip() { tone(0, 0.045, vary(4300, 0.08), 0.09, "triangle"); tone(0.04, 0.05, vary(5100, 0.08), 0.07, "triangle"); hiss(0, 0.04, 6000, 2, 0.08); },
    // a crate reel clicking past each item
    tick() { tone(0, 0.025, vary(2500, 0.1), 0.045, "square"); },
    win() { [0, 0.06, 0.12, 0.19, 0.27].forEach((t, i) => tone(t, 0.06, vary(4200 + i * 220, 0.05), 0.07, "triangle")); tone(0.05, 0.35, 660, 0.09); tone(0.13, 0.4, 990, 0.07); },
    blackjack() { FX.win(); tone(0.22, 0.5, 1320, 0.08); tone(0.32, 0.6, 1760, 0.05); },
    push() { tone(0, 0.18, 520, 0.08); tone(0.12, 0.22, 520, 0.06); },
    lose() { tone(0, 0.35, 220, 0.12, "sine", 150); tone(0.02, 0.3, 330, 0.05, "triangle", 200); },
  };
  return {
    play(name) {
      if (!on || !FX[name]) return;
      try { if (ac()) FX[name](); } catch (e) {}
    },
    // called on a tap or click, so the browser lets sound start
    wake() { if (on) try { ac(); } catch (e) {} },
    get on() { return on; },
    toggle() {
      on = !on;
      try { localStorage.setItem(KEY, on ? "on" : "off"); } catch (e) {}
      if (on) { try { ac(); FX.chip(); } catch (e) {} }
      return on;
    },
  };
})();
