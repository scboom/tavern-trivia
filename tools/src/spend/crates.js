// Crate Battles: the crates, and turning a shared random seed into what everyone pulls.
// Every player's browser works out the same results from the same seed, so nobody (not even the host) decides them.
// Each crate pays back about 97% of its price on average; the odds are shown on the page.
(function (root) {
  const CRATES = [
    { id: "fruit", name: "Fruit Crate", price: 10, icon: "🍒", items: [
      ["🍒", "Cherry", 2, 3345], ["🍋", "Lemon", 4, 2400], ["🍊", "Orange", 6, 1600], ["🍇", "Grapes", 10, 1150], ["🍉", "Watermelon", 17, 800], ["🍍", "Pineapple", 30, 400], ["🥭", "Golden Mango", 92, 200], ["🍓", "Giant Strawberry", 300, 50]] },
    { id: "space", name: "Space Crate", price: 25, icon: "🪐", items: [
      ["🌑", "Moon Rock", 6, 3310], ["🛰️", "Satellite", 11, 2400], ["☄️", "Comet", 18, 1700], ["🪐", "Ringed Planet", 30, 1200], ["🚀", "Rocket", 52, 800], ["👽", "Alien", 110, 400], ["🌌", "Whole Galaxy", 590, 70]] },
    { id: "gem", name: "Gem Crate", price: 50, icon: "💎", items: [
      ["🪨", "Pebble", 10, 3315], ["🪙", "Gold Coin", 22, 2500], ["🔮", "Crystal Ball", 36, 1800], ["💍", "Ring", 64, 1250], ["💎", "Diamond", 130, 800], ["👑", "Royal Crown", 360, 300], ["🔱", "Golden Trident", 1600, 25]] },
    { id: "pirate", name: "Pirate Chest", price: 100, icon: "💰", items: [
      ["🧭", "Compass", 22, 3245], ["🗺️", "Treasure Map", 44, 2400], ["⚓", "Anchor", 70, 1700], ["🗡️", "Cutlass", 120, 1200], ["🦜", "Parrot", 220, 800], ["💰", "Sack of Gold", 620, 330], ["🏆", "Golden Cup", 2700, 45]] },
    { id: "dragon", name: "Dragon Hoard", price: 250, icon: "🐉", items: [
      ["🥚", "Dragon Egg", 50, 3470], ["🛡️", "Dragon Shield", 100, 2500], ["⚔️", "Crossed Swords", 180, 1700], ["🔥", "Fire Stone", 320, 1150], ["🐲", "Baby Dragon", 670, 700], ["🐉", "Elder Dragon", 2500, 220], ["💎", "Heart of the Hoard", 10000, 25]] },
  ];
  const BY_ID = Object.fromEntries(CRATES.map(c => [c.id, c]));
  const total = c => c.items.reduce((n, it) => n + it[3], 0);
  const ev = c => c.items.reduce((n, it) => n + it[2] * it[3], 0) / total(c);
  const chance = (c, i) => c.items[i][3] / total(c);

  // a value's rarity, for colouring: compared with what the crate cost
  function tier(c, v) {
    const r = v / c.price;
    return r >= 6 ? "legendary" : r >= 2 ? "epic" : r >= 1 ? "rare" : "common";
  }

  async function sha256hex(text) {
    const data = new TextEncoder().encode(text);
    const subtle = (root.crypto && root.crypto.subtle) || require("crypto").webcrypto.subtle;
    const buf = await subtle.digest("SHA-256", data);
    return Array.from(new Uint8Array(buf), b => b.toString(16).padStart(2, "0")).join("");
  }
  // a number in [0, 1) for one crate and one seat, fixed by the seed
  async function roll(seed, round, seat) {
    const h = await sha256hex(seed + "|" + round + "|" + seat);
    return parseInt(h.slice(0, 13), 16) / 2 ** 52;
  }
  function pick(c, u) {
    let x = u * total(c);
    for (let i = 0; i < c.items.length; i++) { x -= c.items[i][3]; if (x < 0) return i; }
    return c.items.length - 1;
  }
  const TEAMS = { "1v1": [[0], [1]], "2v2": [[0, 1], [2, 3]] };
  // everything that happens in a battle: what each seat pulls from each crate, the totals, the winning side and each seat's share
  async function play(seed, mode, crateIds) {
    const teams = TEAMS[mode], seats = teams.flat().length;
    const pulls = [];
    for (let r = 0; r < crateIds.length; r++) {
      const c = BY_ID[crateIds[r]], row = [];
      for (let s = 0; s < seats; s++) { const i = pick(c, await roll(seed, r, s)); row.push({ i, v: c.items[i][2] }); }
      pulls.push(row);
    }
    const seatTotal = Array.from({ length: seats }, (_, s) => pulls.reduce((n, row) => n + row[s].v, 0));
    const teamTotal = teams.map(t => t.reduce((n, s) => n + seatTotal[s], 0));
    const best = Math.max(...teamTotal), tied = teamTotal.map((v, t) => v === best ? t : -1).filter(t => t >= 0);
    const win = tied.length === 1 ? tied[0] : tied[Math.floor((await roll(seed, "tie", 0)) * tied.length)];
    const pot = seatTotal.reduce((a, b) => a + b, 0);
    const share = Math.floor(pot / teams[win].length);
    return { pulls, seatTotal, teamTotal, win, tie: tied.length > 1, pot, share, teams, seats };
  }
  const price = ids => ids.reduce((n, id) => n + BY_ID[id].price, 0);
  const api = { CRATES, BY_ID, ev, chance, tier, sha256hex, roll, pick, play, price, TEAMS };
  if (typeof module !== "undefined" && module.exports) module.exports = api; else root.Crates = api;
})(typeof window !== "undefined" ? window : globalThis);
