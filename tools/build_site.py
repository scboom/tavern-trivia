"""Build the Obscure Trivia site: a hub page plus one themed page per quiz, sharing one engine."""
import sys, os, json, shutil, datetime, html, hashlib

SRC, OUT = sys.argv[1], sys.argv[2]
SITE = os.environ.get("SITE_URL", "https://scboom.github.io/obscure-trivia/")
QUESTIONS_PER_GAME = 20   # what every quiz tile advertises
VERIFY = "WFhPSjzH6ULlMofAm5JW4QaXPHvu2l7NRQUrSs7A3Ho"
TEX = json.load(open(os.path.join(SRC, "textures.json")))
E = html.escape

QUIZZES = [
    {
        "id": "hearthstone", "dir": "hearthstone", "bank_src": "hs_questions.json", "extra": [("hs-emblem.svg", "emblem.svg")],
        "title": "Hearthstone Battlegrounds Quiz – Obscure Trivia",
        "desc": "A free Hearthstone Battlegrounds quiz: 20 random questions per game on minion tiers and stats, hero armor in Solo and Duos, Hero Powers, Buddies, quests, trinkets and anomalies. Play solo or in party mode with up to 6 players.",
        "fonts": "family=Bree+Serif&family=Figtree:wght@400;500;600;700",
        "theme_color": "#1d1512",
        "favicon": "emblem.svg",
        "config": {
            "id": "hearthstone", "letter": "H", "short": "Battlegrounds", "icon": "",
            "namePh": "e.g. Pogo Fan", "eyebrow": "Hearthstone Battlegrounds quiz", "headline": "How well do you really know Bob's Tavern?",
            "topics": "minion tiers and stats, hero armor in Solo and Duos, Hero Powers, Buddies, quest rewards, trinkets, Tavern spells and anomalies",
            "foot": "Card data from the Hearthstone client files, build of 3 November 2026. Fan-made quiz, not affiliated with Blizzard.",
            "seed": "tavern-trivia-v1:", "topic": "tavern-trivia/v1/", "recentKey": "tt-recent-v1", "sessionKey": "tt-game",
            "bank": "questions.json", "hub": "../", "others": {"M": "../minecraft/"},
            "groups": {"tier": "Minion", "stats": "Minion", "type": "Minion", "effect": "Minion", "whois": "Minion", "golden": "Minion",
                       "oldstats": "Minion", "oldeffect": "Minion", "duos": "Minion", "armor": "Hero", "duoarmor": "Hero", "health": "Hero",
                       "hpname": "Hero", "hpwho": "Hero", "hpeffect": "Hero", "hpcost": "Hero", "buddy": "Hero", "buddywho": "Hero",
                       "quest": "Quest", "questwho": "Quest", "trinket": "Trinket", "trinketcost": "Trinket", "trinketkind": "Trinket",
                       "spell": "Tavern spell", "spellcost": "Tavern spell", "spelltier": "Tavern spell", "anomaly": "Anomaly", "anomalywho": "Anomaly"},
            "caps": {"Minion": 9, "Hero": 7, "Quest": 3, "Trinket": 3, "Tavern spell": 3, "Anomaly": 3},
            "verdicts": [[18, "Tavern legend."], [14, "Top four, easily."], [10, "Solid lobby. Bob approves."], [6, "You held on to your Armor."], [0, "Bob says: keep practising."]],
        },
        "theme": """
:root {
  --bg: #1d1512;
  --bg-art: repeating-linear-gradient(90deg, rgba(255,255,255,0.012) 0 2px, transparent 2px 9px), radial-gradient(ellipse at 50% -10%, #3a2618 0%, transparent 60%);
  --panel: #2a1f1a; --panel-fill: linear-gradient(180deg, #2a1f1a 0%, #251b16 100%); --panel-2: #37291f;
  --panel-shadow: 0 10px 30px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.04);
  --line: #4a382c; --line-hover: #6a5140; --ink: #f4eadf; --muted: #b8a391; --faint: #8a7666; --placeholder: #7d6a5b;
  --accent: #e8b450; --accent-ink: #2a1b08; --accent-text: #e8b450; --accent-hover: #f0c063; --accent-edge: #f5cf7f; --accent-shadow: 0 2px 0 #9b6a1c;
  --chip-bg: rgba(232,180,80,0.1); --chip-line: rgba(232,180,80,0.25); --chip-ink: #f2cf8a;
  --pal: #6fc6d8; --pal-ink: #062026; --pal-bg: rgba(111,198,216,0.1); --pal-line: rgba(111,198,216,0.3);
  --good: #86d16f; --good-ink: #10200a; --good-bg: rgba(134,209,111,0.12); --bad: #e9725f; --bad-ink: #2a0b06; --bad-bg: rgba(233,114,95,0.12);
  --inset: #1a1210; --opt: #231a15; --tile: #221914;
  --card-bg: #f1e4cc; --card-ink: #2b1f14; --card-line: #c9b48f; --card-inner: #e6d5b5; --card-strong: #1a120b;
  --f-display: "Bree Serif", Georgia, "Times New Roman", serif; --f-body: "Figtree", system-ui, -apple-system, "Segoe UI", sans-serif;
  --r: 10px; --r-panel: 14px; --r-pill: 999px; --r-key: 7px;
  color-scheme: dark;
}
.coin {
  width: 32px; height: 32px; border-radius: 50%; flex: none; display: block;
  background: url("emblem.svg") center / 100% 100%; filter: drop-shadow(0 2px 3px rgba(0,0,0,0.45));
}
""",
        "tile": {"cls": "hs", "title": "Hearthstone Battlegrounds", "art": "",
                 "blurb": "Minion tiers and stats, hero armor in Solo and Duos, Hero Powers, quests, trinkets and anomalies."},
        "intro": ("Hearthstone Battlegrounds quiz", "How well do you really know Bob's Tavern?",
                  "A free Hearthstone Battlegrounds quiz, 20 questions per game: minion tiers and stats, hero armor in Solo and Duos, Hero Powers, Buddies, quest rewards, trinkets, Tavern spells and anomalies. Play on your own, or start a party of up to 6 players with a 5-letter code."),
    },
    {
        "id": "minecraft", "dir": "minecraft", "bank_src": "mc_questions.json",
        "title": "Minecraft Bedrock Quiz – Obscure Trivia",
        "desc": "A free Minecraft: Bedrock Edition quiz: 20 random questions per game on crafting recipes, blocks, tools, mobs, enchanting, brewing and biomes. Play solo or in party mode with up to 6 players.",
        "fonts": "family=Noto+Sans:wght@400;600;700",
        "theme_color": "#1b1c1e",
        "favicon": "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 8 8' shape-rendering='crispEdges'%3E%3Crect width='8' height='8' fill='%23866043'/%3E%3Crect width='8' height='3' fill='%235f9f35'/%3E%3Crect y='3' width='2' height='1' fill='%235f9f35'/%3E%3Crect x='5' y='3' width='1' height='1' fill='%235f9f35'/%3E%3Crect x='3' y='5' width='1' height='1' fill='%23694b33'/%3E%3Crect x='6' y='6' width='1' height='1' fill='%23694b33'/%3E%3C/svg%3E",
        "extra": [("fonts/Monocraft.woff2", "Monocraft.woff2"), ("fonts/Monocraft-OFL.txt", "Monocraft-OFL.txt"), ("mc-sheep.png", "sheep.png")],
        "config": {
            "id": "minecraft", "letter": "M", "short": "Minecraft", "icon": "",
            "eyebrow": "Minecraft: Bedrock Edition quiz", "headline": "Think you know every block, mob and recipe?",
            "topics": "crafting recipes, blocks and ores, tools, mobs, enchanting, brewing, biomes and villagers, all for the current Bedrock Edition",
            "foot": "All questions are about the current Minecraft: Bedrock Edition. Block, item and recipe data comes from the Bedrock game files (late 2026). Fan-made quiz, not affiliated with Mojang or Microsoft.",
            "seed": "obscure-trivia-minecraft-v1:", "topic": "obscure-trivia/minecraft/v1/", "recentKey": "ot-recent-minecraft-v1", "sessionKey": "ot-game-minecraft",
            "bank": "questions.json", "hub": "../", "others": {"H": "../hearthstone/"},
            "groups": {"recipe": "Crafting", "recipewhat": "Crafting", "recipecount": "Crafting", "smelt": "Crafting",
                       "notblock": "Blocks", "isblock": "Blocks", "light": "Blocks", "lightwhich": "Blocks", "tier": "Blocks", "blast": "Blocks", "hardness": "Blocks",
                       "stack": "Items", "food": "Items", "health": "Mobs", "hostile": "Mobs", "drops": "Mobs", "breed": "Mobs", "villager": "Mobs",
                       "enchlevel": "Enchanting", "treasure": "Enchanting", "treasure2": "Enchanting", "curse": "Enchanting", "enchslot": "Enchanting",
                       "enchclash": "Enchanting", "biome": "World", "fact": "World"},
            "caps": {"Crafting": 7, "Blocks": 5, "Items": 3, "Mobs": 5, "Enchanting": 4, "World": 4},
            "verdicts": [[19, "Netherite tier."], [16, "Diamond tier."], [12, "Iron tier. Solid gear."], [8, "Stone tier. Keep mining."], [0, "Wooden pickaxe energy. Try again!"]],
        },
        "theme": """
:root {
  --bg: #17181a;
  --bg-art: linear-gradient(rgba(12,12,14,0.62), rgba(12,12,14,0.78)), url(%(deep)s) 0 0 / 64px 64px;
  --panel: #313233; --panel-fill: #313233; --panel-2: #48494a;
  --panel-shadow: inset 0 3px 0 rgba(255,255,255,0.07), inset 0 -3px 0 rgba(0,0,0,0.25), 0 6px 0 rgba(0,0,0,0.35);
  --line: #0f0f10; --line-hover: #8c8d90; --ink: #ffffff; --muted: #b9babd; --faint: #8c8d90; --placeholder: #77787b;
  --accent: #3c8527; --accent-ink: #ffffff; --accent-text: #7ad155; --accent-hover: #4a9a32; --accent-edge: #1e4d12;
  --accent-shadow: inset 0 -4px 0 #1d4d13, inset 0 3px 0 rgba(255,255,255,0.22);
  --chip-bg: rgba(108,195,73,0.12); --chip-line: rgba(108,195,73,0.4); --chip-ink: #95e06f;
  --pal: #5fb7ee; --pal-ink: #04223a; --pal-bg: rgba(95,183,238,0.12); --pal-line: rgba(95,183,238,0.4);
  --good: #6cc349; --good-ink: #0d2a05; --good-bg: rgba(108,195,73,0.16); --bad: #ef5a45; --bad-ink: #2b0702; --bad-bg: rgba(239,90,69,0.16);
  --inset: #1e1e1f; --opt: #3a3b3c; --tile: #262728;
  --card-bg: #c6c6c6; --card-ink: #3a3a3a; --card-line: #000000; --card-inner: #8b8b8b; --card-strong: #1a1a1a;
  --f-display: "Monocraft", ui-monospace, "Courier New", monospace; --f-body: "Noto Sans", system-ui, -apple-system, "Segoe UI", sans-serif;
  --r: 0px; --r-panel: 0px; --r-pill: 0px; --r-key: 0px;
  color-scheme: dark;
}
@font-face { font-family: "Monocraft"; src: url("Monocraft.woff2") format("woff2"); font-display: swap; }
body { image-rendering: pixelated; }
.qtext { font-size: clamp(1.1rem, 3.9vw, 1.4rem); line-height: 1.35; }
.opt .lbl.big { font-size: 1.05rem; }
.board { border-width: 2px; }
.btn { border-width: 2px; border-color: #0f0f10; box-shadow: inset 0 -4px 0 rgba(0,0,0,0.3), inset 0 3px 0 rgba(255,255,255,0.12); }
.btn:active { transform: translateY(2px); box-shadow: inset 0 -2px 0 rgba(0,0,0,0.3); }
.btn.gold { border-color: #0f0f10; }
.opt { border-width: 2px; }
.opt .key { border-width: 2px; }
.pip { border-radius: 0; }
.chip, .tag { border-radius: 0; }
.coin {
  width: 30px; height: 30px; flex: none; display: block;
  background: url(%(grass_side)s) 0 0 / 100%% 100%%; image-rendering: pixelated;
  box-shadow: inset 0 0 0 2px rgba(0,0,0,0.35), 0 2px 0 rgba(0,0,0,0.45);
}
.qtext { letter-spacing: 0.01em; }
.cardtext { box-shadow: inset 2px 2px 0 #ffffff, inset -2px -2px 0 #555555; border-width: 2px; font-weight: 600; }
""" % {"deep": TEX["deep"], "grass_side": TEX["grass_side"]},
        "tile": {"cls": "mc", "title": "Minecraft", "art": "",
                 "blurb": "Bedrock Edition: crafting recipes, blocks, tools, mobs, enchanting, brewing and biomes."},
        "intro": ("Minecraft: Bedrock Edition quiz", "Think you know every block, mob and recipe?",
                  "A free Minecraft: Bedrock Edition quiz, 20 questions per game: crafting recipes, blocks and ores, tools, mobs, enchanting, brewing, biomes and villagers. Play on your own, or start a party of up to 6 players with a 5-letter code."),
    },
    {
        "id": "world", "dir": "general-knowledge", "bank_src": "world_questions.json",
        "title": "General Knowledge Quiz – Obscure Trivia",
        "desc": "A free general knowledge quiz: 20 random questions per game on space, animals, the human body, countries and flags, geography, history, science and culture. Play solo or in party mode with up to 6 players.",
        "fonts": "family=Outfit:wght@500;600;700;800&family=Atkinson+Hyperlegible:wght@400;700",
        "theme_color": "#050a18",
        "favicon": "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Ccircle cx='32' cy='32' r='29' fill='%232f7fd0'/%3E%3Cpath d='M18 18c6-4 12-2 14 3s-3 8 1 12 9 1 10 7-6 10-10 9' fill='none' stroke='%2366b45a' stroke-width='7' stroke-linecap='round'/%3E%3Ccircle cx='32' cy='32' r='29' fill='none' stroke='%23bfe3ff' stroke-width='3'/%3E%3C/svg%3E",
        "extra": [("world/earth-bg.jpg", "earth-bg.jpg"), ("world/earth-tile.jpg", "earth-tile.jpg"), ("world/flags", "flags")],
        "config": {
            "id": "world", "letter": "W", "short": "General Knowledge", "icon": "",
            "eyebrow": "General knowledge quiz", "headline": "How much do you know about our world?",
            "topics": "space, animals, the human body, countries and flags, geography, history and inventions, science, food, sport and culture",
            "foot": "Country facts from the open mledoze/countries dataset (ODbL) and flags from flag-icons (MIT). The Earth picture is drawn from Natural Earth map data. Fan-made quiz.",
            "seed": "obscure-trivia-world-v1:", "topic": "obscure-trivia/world/v1/", "recentKey": "ot-recent-world-v1", "sessionKey": "ot-game-world",
            "bank": "questions.json", "hub": "../",
            "groups": {"space": "Space", "animals": "Animals", "body": "Human body", "geo": "Geography", "history": "History", "science": "Science",
                       "culture": "Culture", "capital": "Countries", "capitalwho": "Countries", "currency": "Countries", "currencywho": "Countries",
                       "language": "Countries", "continent": "Countries", "landlocked": "Countries", "bigger": "Countries", "flag": "Countries"},
            "caps": {"Countries": 7, "Space": 2, "Animals": 3, "Human body": 2, "Geography": 3, "History": 2, "Science": 2, "Culture": 3},
            "verdicts": [[19, "Walking encyclopedia."], [16, "World class!"], [12, "Well travelled."], [8, "Tourist. Keep exploring!"], [0, "Time to pack your bags and explore!"]],
        },
        "theme": """
:root {
  --bg: #050a18; --bg-art: none;
  --panel: rgba(12, 22, 48, 0.78); --panel-fill: linear-gradient(180deg, rgba(16, 30, 64, 0.82), rgba(9, 18, 42, 0.86)); --panel-2: rgba(38, 60, 110, 0.75);
  --panel-shadow: 0 18px 40px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.06);
  --line: rgba(150, 190, 255, 0.2); --line-hover: rgba(160, 210, 255, 0.55); --ink: #f2f7ff; --muted: #a9bbd8; --faint: #8296b8; --placeholder: #7186a8;
  --accent: #7dd3fc; --accent-ink: #04213a; --accent-text: #8edbff; --accent-hover: #a5e2ff; --accent-edge: #bfeaff; --accent-shadow: 0 6px 18px rgba(125, 211, 252, 0.28);
  --chip-bg: rgba(125, 211, 252, 0.1); --chip-line: rgba(125, 211, 252, 0.32); --chip-ink: #b9e8ff;
  --pal: #ff9b7a; --pal-ink: #3a1206; --pal-bg: rgba(255, 155, 122, 0.12); --pal-line: rgba(255, 155, 122, 0.4);
  --good: #5ee0a0; --good-ink: #03261a; --good-bg: rgba(94, 224, 160, 0.14); --bad: #ff7a85; --bad-ink: #3a060c; --bad-bg: rgba(255, 122, 133, 0.14);
  --inset: rgba(4, 10, 26, 0.7); --opt: rgba(20, 36, 74, 0.7); --tile: rgba(14, 26, 56, 0.75);
  --card-bg: #eef6ff; --card-ink: #0b1a33; --card-line: #bcd6f5; --card-inner: #dcebfd; --card-strong: #06122a;
  --f-display: "Outfit", "Segoe UI", system-ui, sans-serif; --f-body: "Atkinson Hyperlegible", "Segoe UI", system-ui, sans-serif;
  --r: 14px; --r-panel: 22px; --r-pill: 999px; --r-key: 10px;
  color-scheme: dark;
}
body::before { content: ""; position: fixed; inset: 0; z-index: -1; pointer-events: none;
  background: linear-gradient(180deg, rgba(5, 10, 24, 0.15) 0%, rgba(5, 10, 24, 0.35) 55%, rgba(5, 10, 24, 0.55) 100%), url(earth-bg.jpg) center bottom / cover no-repeat, #050a18; }
.board { backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); }
h1, h2, h3 { font-weight: 700; letter-spacing: -0.01em; }
.qtext { font-weight: 600; letter-spacing: -0.005em; }
.opt .lbl.big { font-weight: 600; }
.code-big { font-weight: 800; }
.coin {
  width: 30px; height: 30px; border-radius: 50%; flex: none; display: block;
  background: radial-gradient(circle at 70% 70%, transparent 46%, rgba(2, 8, 30, 0.55) 70%), radial-gradient(circle at 34% 38%, #6fbf5c 0 16%, transparent 17%),
    radial-gradient(circle at 62% 62%, #6fbf5c 0 13%, transparent 14%), radial-gradient(circle at 30% 30%, #8fd0ff, #2f7fd0 55%, #123f8a);
  box-shadow: 0 0 0 1px rgba(191, 227, 255, 0.5), 0 0 14px rgba(125, 211, 252, 0.45);
}
""",
        "tile": {"cls": "gk", "title": "General Knowledge", "art": "",
                 "blurb": "Space, animals, the human body, countries and flags, history, science and culture."},
        "intro": ("General knowledge quiz", "How much do you know about our world?",
                  "A free general knowledge quiz, 20 questions per game: space, animals, the human body, countries and flags, geography, history, science and culture. Play on your own, or start a party of up to 6 players with a 5-letter code."),
    },
    {
        "id": "football", "dir": "football", "bank_src": "football_questions.json",
        "title": "Football Quiz – Obscure Trivia",
        "desc": "A free football quiz: 20 random questions per game on the Premier League, the World Cup, the Champions League, players, stadiums, nicknames and rules. Play solo or in party mode with up to 6 players.",
        "fonts": "family=Oswald:wght@500;600;700&family=Barlow:wght@400;500;600;700",
        "theme_color": "#0d2a17",
        "favicon": "BALL",
        "extra": [],
        "config": {
            "id": "football", "letter": "F", "short": "Football", "icon": "",
            "eyebrow": "Football quiz", "headline": "Think you know your football?",
            "topics": "the Premier League, the World Cup, the Champions League and the Euros, legendary players, stadiums, nicknames, derbies and the rules",
            "foot": "Premier League and World Cup results from the openfootball project (public domain). Fan-made quiz, not affiliated with the Premier League, FIFA or UEFA.",
            "seed": "obscure-trivia-football-v1:", "topic": "obscure-trivia/football/v1/", "recentKey": "ot-recent-football-v1", "sessionKey": "ot-game-football",
            "bank": "questions.json", "hub": "../",
            "groups": {"plchamp": "Premier League", "plsecond": "Premier League", "plthird": "Premier League", "plfourth": "Premier League", "plpoints": "Premier League",
                       "plbottom": "Premier League", "pllowest": "Premier League", "pldown": "Premier League", "plup": "Premier League", "plhigher": "Premier League",
                       "plstreak": "Premier League", "plseasons": "Premier League", "plfirst": "Premier League", "plfounder": "Premier League", "plever": "Premier League",
                       "pltitles": "Premier League", "plrecord": "Premier League",
                       "wcwin": "World Cup", "wcfinal": "World Cup", "wchost": "World Cup", "wccount": "World Cup", "wclast": "World Cup", "wcpens": "World Cup", "wc": "World Cup",
                       "ucl": "Europe", "euro": "Europe", "player": "Players", "stadium": "Grounds", "city": "Grounds", "nickname": "Clubs", "derby": "Clubs",
                       "rules": "Rules", "fa": "English football"},
            "caps": {"Premier League": 7, "World Cup": 3, "Players": 3, "Europe": 2, "Grounds": 2, "Clubs": 2, "Rules": 2, "English football": 2},
            "verdicts": [[19, "Ballon d'Or material."], [16, "World class."], [12, "Premier League quality."], [8, "Championship level. Keep training!"], [0, "Sunday league. Back to training!"]],
        },
        "theme": """
:root {
  --bg: #0b2414;
  --bg-art: none;
  --panel: rgba(8, 24, 14, 0.86); --panel-fill: linear-gradient(180deg, rgba(10, 30, 18, 0.9), rgba(6, 20, 12, 0.92)); --panel-2: rgba(30, 70, 42, 0.85);
  --panel-shadow: 0 16px 34px rgba(0, 0, 0, 0.5), inset 0 0 0 1px rgba(255, 255, 255, 0.06);
  --line: rgba(255, 255, 255, 0.22); --line-hover: rgba(255, 255, 255, 0.6); --ink: #ffffff; --muted: #bfd6c6; --faint: #95b39f; --placeholder: #7f9d89;
  --accent: #ffd84a; --accent-ink: #1d1600; --accent-text: #ffe066; --accent-hover: #ffe27a; --accent-edge: #fff0a8; --accent-shadow: 0 3px 0 #b8911a;
  --chip-bg: rgba(255, 255, 255, 0.08); --chip-line: rgba(255, 255, 255, 0.3); --chip-ink: #ffffff;
  --pal: #5ab4ff; --pal-ink: #03203a; --pal-bg: rgba(90, 180, 255, 0.12); --pal-line: rgba(90, 180, 255, 0.4);
  --good: #6ee07a; --good-ink: #062b0b; --good-bg: rgba(110, 224, 122, 0.15); --bad: #ff6b6b; --bad-ink: #3a0606; --bad-bg: rgba(255, 107, 107, 0.16);
  --inset: rgba(0, 0, 0, 0.35); --opt: rgba(16, 44, 26, 0.85); --tile: rgba(12, 34, 20, 0.88);
  --card-bg: #f4f7f2; --card-ink: #0f2416; --card-line: #c9d9cc; --card-inner: #e5eee6; --card-strong: #061409;
  --f-display: "Oswald", "Arial Narrow", Impact, sans-serif; --f-body: "Barlow", "Segoe UI", system-ui, sans-serif;
  --r: 8px; --r-panel: 12px; --r-pill: 999px; --r-key: 6px;
  color-scheme: dark;
}
/* a floodlit pitch: mowing stripes, chalk centre circle, dark edges */
body::before { content: ""; position: fixed; inset: 0; z-index: -1; pointer-events: none;
  background:
    radial-gradient(ellipse at 50% 0%, rgba(255, 255, 230, 0.16), transparent 55%),
    radial-gradient(circle at 50% 46%, transparent 0 118px, rgba(255, 255, 255, 0.16) 119px 122px, transparent 123px),
    linear-gradient(180deg, transparent calc(46% - 1.5px), rgba(255, 255, 255, 0.16) calc(46% - 1.5px) calc(46% + 1.5px), transparent calc(46% + 1.5px)),
    radial-gradient(ellipse at 50% 50%, transparent 40%, rgba(0, 0, 0, 0.55) 100%),
    repeating-linear-gradient(180deg, #1d6a35 0 70px, #22783c 70px 140px); }
h1, h2, h3, .qtext, .code-big, .bigmsg, .verdict { text-transform: uppercase; letter-spacing: 0.02em; }
h1, h2, h3 { font-weight: 700; }
.qtext { font-weight: 600; text-transform: none; letter-spacing: 0; }
.opt .lbl.big { font-family: var(--f-body); font-weight: 600; font-size: 1.1rem; }
.coin {
  width: 30px; height: 30px; border-radius: 50%; flex: none; display: block;
  background: url("BALL") center / 100% 100%; box-shadow: 0 2px 6px rgba(0, 0, 0, 0.5);
}
""".replace("BALL", "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Ccircle cx='32' cy='32' r='29' fill='%23fff' stroke='%23111' stroke-width='3'/%3E%3Cpath d='M32 20l10 7-4 12H26l-4-12z' fill='%23111'/%3E%3Cpath d='M32 20V8M42 27l11-4M38 39l7 10M26 39l-7 10M22 27l-11-4' stroke='%23111' stroke-width='3'/%3E%3C/svg%3E"),
        "tile": {"cls": "fb", "title": "Football", "art": "",
                 "blurb": "The Premier League, the World Cup, the Champions League, legendary players, stadiums, nicknames and rules."},
        "intro": ("Football quiz", "Think you know your football?",
                  "A free football quiz, 20 questions per game: the Premier League, the World Cup, the Champions League, legendary players, stadiums, nicknames and the rules. Play on your own, or start a party of up to 6 players with a 5-letter code."),
    },
    {
        "id": "cars", "dir": "cars", "bank_src": "cars_questions.json",
        "title": "Car Quiz – Obscure Trivia",
        "desc": "A free car quiz: 20 random questions per game on horsepower, top speeds, prices, car makers, badges, engines and famous film cars. Play solo or in party mode with up to 6 players.",
        "fonts": "family=Chakra+Petch:ital,wght@0,600;0,700;1,700&family=Titillium+Web:wght@400;600;700",
        "theme_color": "#0d0e10",
        "favicon": "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Ccircle cx='32' cy='32' r='29' fill='%2316171b' stroke='%23e10600' stroke-width='3'/%3E%3Cpath d='M14 42a20 20 0 1 1 36 0' fill='none' stroke='%23f3f4f6' stroke-width='5' stroke-dasharray='2 5.3'/%3E%3Cpath d='M32 36L45 21' stroke='%23e10600' stroke-width='4' stroke-linecap='round'/%3E%3Ccircle cx='32' cy='36' r='4.5' fill='%23f3f4f6'/%3E%3C/svg%3E",
        "extra": [],
        "config": {
            "id": "cars", "letter": "C", "short": "Cars", "icon": "",
            "eyebrow": "Car quiz", "headline": "From hatchbacks to hypercars: how well do you know cars?",
            "topics": "horsepower, top speeds, prices, car makers and who owns them, founding dates, engines, badges, famous film cars and the rules of the road",
            "foot": "Horsepower and top speeds are the makers' own figures, and prices are rough UK prices when new. A question only compares cars when one is clearly ahead, because figures vary a little between model years and countries. Fan-made quiz, not affiliated with any car maker.",
            "seed": "obscure-trivia-cars-v1:", "topic": "obscure-trivia/cars/v1/", "recentKey": "ot-recent-cars-v1", "sessionKey": "ot-game-cars",
            "bank": "questions.json", "hub": "../",
            "groups": {"power": "Power", "model": "Makers", "country": "Makers", "owner": "Makers", "notby": "Makers", "decade": "History", "founded": "History", "hist": "History", "price": "Prices", "auction": "Prices", "pricefact": "Prices", "speed": "Speed", "speedfact": "Speed", "cyl": "Tech", "ev": "Tech", "tech": "Tech", "logo": "Badges", "name": "Badges", "screen": "Film & TV", "drive": "On the road", "road": "On the road"},
            "caps": {"Power": 2, "Makers": 3, "History": 5, "Prices": 2, "Speed": 2, "Tech": 2, "Badges": 2, "Film & TV": 2, "On the road": 1},
            "verdicts": [[19, "Pole position."], [16, "Podium finish."], [12, "Points finish."], [8, "Still on the grid. Keep practising."], [0, "Stalled on the line. Try again!"]],
        },
        "theme": """
:root {
  --bg: #0d0e10;
  --bg-art: linear-gradient(45deg, #121316 25%, transparent 25%, transparent 75%, #121316 75%) 0 0 / 10px 10px,
    linear-gradient(45deg, #121316 25%, transparent 25%, transparent 75%, #121316 75%) 5px 5px / 10px 10px,
    linear-gradient(#18191d, #141518);
  --panel: #17181c; --panel-fill: linear-gradient(180deg, rgba(30, 31, 36, 0.97), rgba(20, 21, 25, 0.97)); --panel-2: #24262c;
  --panel-shadow: 0 14px 34px rgba(0, 0, 0, 0.55), inset 0 1px 0 rgba(255, 255, 255, 0.06);
  --line: #33353c; --line-hover: #6b6f7a; --ink: #f3f4f6; --muted: #a6abb6; --faint: #81868f; --placeholder: #6f747d;
  --accent: #e10600; --accent-ink: #ffffff; --accent-text: #ff5a4d; --accent-hover: #f5170f; --accent-edge: #ff6a5c; --accent-shadow: 0 3px 0 #7a0300;
  --chip-bg: rgba(255, 255, 255, 0.06); --chip-line: rgba(255, 255, 255, 0.2); --chip-ink: #e5e7eb;
  --pal: #38bdf8; --pal-ink: #03202e; --pal-bg: rgba(56, 189, 248, 0.12); --pal-line: rgba(56, 189, 248, 0.4);
  --good: #34d399; --good-ink: #022c1d; --good-bg: rgba(52, 211, 153, 0.13); --bad: #f87171; --bad-ink: #300808; --bad-bg: rgba(248, 113, 113, 0.14);
  --inset: #0b0c0e; --opt: #1b1c21; --tile: #15161a;
  --card-bg: #f3f4f6; --card-ink: #111214; --card-line: #c9ccd2; --card-inner: #e4e6ea; --card-strong: #000000;
  --f-display: "Chakra Petch", "Arial Narrow", system-ui, sans-serif; --f-body: "Titillium Web", system-ui, -apple-system, "Segoe UI", sans-serif;
  --r: 6px; --r-panel: 10px; --r-pill: 999px; --r-key: 4px;
  color-scheme: dark;
}
/* carbon fibre under a red glow, like brake lights at the top of the screen */
body::before { content: ""; position: fixed; inset: 0; z-index: -1; pointer-events: none;
  background: radial-gradient(ellipse at 50% -15%, rgba(225, 6, 0, 0.32), transparent 55%), radial-gradient(ellipse at 50% 50%, transparent 45%, rgba(0, 0, 0, 0.6) 100%); }
h1, h2, h3, .bigmsg, .verdict, .code-big { font-weight: 700; font-style: italic; letter-spacing: 0.01em; }
.hero h2 { text-transform: uppercase; }
.qtext { font-weight: 700; }
.opt .lbl.big { font-family: var(--f-display); font-weight: 600; font-size: 1.12rem; }
.opt .key { font-family: var(--f-display); }
.opt:hover:not([disabled]) { border-color: var(--accent); }
/* a red and white stripe on each panel */
.board { position: relative; }
.board::before { content: ""; position: absolute; top: -1px; left: 22px; width: 64px; height: 4px; border-radius: 0 0 2px 2px;
  background: linear-gradient(90deg, var(--accent) 0 58%, transparent 58% 70%, #f3f4f6 70% 100%); }
.btn.gold { font-family: var(--f-display); font-style: italic; letter-spacing: 0.02em; }
.coin { width: 32px; height: 32px; flex: none; display: block; background: url("GAUGE") center / 100% 100%; }
""".replace("GAUGE", "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Ccircle cx='32' cy='32' r='29' fill='%2316171b' stroke='%23e10600' stroke-width='3'/%3E%3Cpath d='M14 42a20 20 0 1 1 36 0' fill='none' stroke='%23f3f4f6' stroke-width='5' stroke-dasharray='2 5.3'/%3E%3Cpath d='M32 36L45 21' stroke='%23e10600' stroke-width='4' stroke-linecap='round'/%3E%3Ccircle cx='32' cy='36' r='4.5' fill='%23f3f4f6'/%3E%3C/svg%3E"),
        "tile": {"cls": "cr", "title": "Cars", "art": "",
                 "blurb": "Horsepower, top speeds, prices, badges, car makers and their history, and famous film cars."},
        "intro": ("Car quiz", "From hatchbacks to hypercars: how well do you know cars?",
                  "A free car quiz, 20 questions per game: horsepower, top speeds, prices, car makers and their owners, founding dates, engines, badges, famous film cars and the rules of the road. Play on your own, or start a party of up to 6 players with a 5-letter code."),
    },
    {
        "id": "music", "dir": "music", "bank_src": "music_questions.json", "extra": [("vinyl.svg", "vinyl.svg")],
        "title": "Music Quiz – Obscure Trivia",
        "desc": "A free music quiz: 20 random questions per game on the world's biggest songs and records, chart hits from the 1960s to now, albums, artists and bands, Eurovision and film songs. Play solo or in party mode with up to 6 players.",
        "fonts": "family=Unbounded:wght@600;700&family=DM+Sans:wght@400;500;700",
        "theme_color": "#0e0a1c",
        "favicon": "vinyl.svg",
        "config": {
            "id": "music", "letter": "S", "short": "Music", "icon": "",
            "eyebrow": "Music quiz", "headline": "From the 60s to now: how well do you know your music?",
            "topics": "the world's biggest songs and records, chart hits from the 1960s to now, albums, artists and bands, Eurovision, film songs and music facts",
            "foot": "US chart questions are worked out from every Billboard Hot 100 since 1958. Streaming and sales records are as of 2026. No lyrics are used. Fan-made quiz, not affiliated with any artist or record label.",
            "seed": "obscure-trivia-music-v1:", "topic": "obscure-trivia/music/v1/", "recentKey": "ot-recent-music-v1", "sessionKey": "ot-game-music",
            "bank": "questions.json", "hub": "../",
            "groups": {"usno1": "US charts", "usfirst": "US charts", "usdecade": "US charts", "usweeks": "Records", "record": "Records", "song": "Songs", "songby": "Songs", "songdecade": "Songs", "songfirst": "Songs", "album": "Albums", "albumfirst": "Albums", "realname": "Artists", "band": "Artists", "from": "Artists", "euro": "Eurovision", "film": "Film & TV", "music": "Music facts"},
            "caps": {"US charts": 4, "Songs": 5, "Albums": 2, "Artists": 3, "Records": 2, "Eurovision": 1, "Film & TV": 2, "Music facts": 2},
            "verdicts": [[19, "Headliner."], [16, "Platinum record."], [12, "Top 10 hit."], [8, "One-hit wonder."], [0, "Still in the garage band. Keep practising!"]],
        },
        "theme": """
:root {
  --bg: #0e0a1c;
  --bg-art: radial-gradient(circle, rgba(255, 255, 255, 0.05) 1px, transparent 1.4px) 0 0 / 22px 22px;
  --panel: #1a1230; --panel-fill: linear-gradient(180deg, rgba(34, 22, 62, 0.92), rgba(22, 14, 42, 0.94)); --panel-2: #2b1e4d;
  --panel-shadow: 0 16px 40px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.07);
  --line: rgba(255, 255, 255, 0.13); --line-hover: rgba(255, 122, 192, 0.6); --ink: #f6f0ff; --muted: #b8acd6; --faint: #8f83ad; --placeholder: #7d7299;
  --accent: #ff4fa3; --accent-ink: #1d0012; --accent-text: #ff8ac6; --accent-hover: #ff6fb4; --accent-edge: #ffa6d3; --accent-shadow: 0 0 0 1px #ff4fa3, 0 6px 22px rgba(255, 79, 163, 0.45);
  --chip-bg: rgba(255, 255, 255, 0.07); --chip-line: rgba(255, 255, 255, 0.18); --chip-ink: #eadfff;
  --pal: #4de3ff; --pal-ink: #00222b; --pal-bg: rgba(77, 227, 255, 0.12); --pal-line: rgba(77, 227, 255, 0.45);
  --good: #5cf2a5; --good-ink: #00281a; --good-bg: rgba(92, 242, 165, 0.13); --bad: #ff6b7d; --bad-ink: #2e0007; --bad-bg: rgba(255, 107, 125, 0.14);
  --inset: #0b0717; --opt: rgba(30, 20, 56, 0.9); --tile: rgba(24, 16, 46, 0.9);
  --card-bg: #f6f0ff; --card-ink: #1a1230; --card-line: #cfc2ee; --card-inner: #e9e0fb; --card-strong: #000000;
  --f-display: "Unbounded", "Arial Black", system-ui, sans-serif; --f-body: "DM Sans", system-ui, -apple-system, "Segoe UI", sans-serif;
  --r: 12px; --r-panel: 18px; --r-pill: 999px; --r-key: 8px;
  color-scheme: dark;
}
/* concert lights: a pink spotlight and a blue one over a dark stage */
body::before { content: ""; position: fixed; inset: 0; z-index: -1; pointer-events: none;
  background: radial-gradient(ellipse 60% 70% at 12% -12%, rgba(255, 79, 163, 0.32), transparent 60%),
    radial-gradient(ellipse 60% 70% at 90% -12%, rgba(77, 227, 255, 0.24), transparent 60%),
    radial-gradient(ellipse at 50% 120%, rgba(140, 80, 255, 0.22), transparent 55%); }
h1, h2, h3, .bigmsg, .verdict, .code-big { font-weight: 700; letter-spacing: -0.01em; }
.qtext { font-weight: 600; font-size: clamp(1.15rem, 4vw, 1.45rem); line-height: 1.3; }
.opt .lbl.big { font-family: var(--f-body); font-weight: 700; font-size: 1.08rem; }
.board { backdrop-filter: blur(6px); }
.btn.gold { font-family: var(--f-display); font-weight: 600; font-size: 0.95rem; }
.coin { width: 32px; height: 32px; flex: none; display: block; border-radius: 50%; background: url("vinyl.svg") center / 100% 100%;
  box-shadow: 0 0 14px rgba(255, 79, 163, 0.45); }
@media (prefers-reduced-motion: no-preference) { .brand .coin { animation: spin 6s linear infinite; } }
""",
        "tile": {"cls": "mu", "title": "Music", "art": "",
                 "blurb": "The world's biggest songs and records, chart hits from the 60s to now, artists, albums and Eurovision."},
        "intro": ("Music quiz", "From the 60s to now: how well do you know your music?",
                  "A free music quiz, 20 questions per game: the world's biggest songs and records, chart hits from the 1960s to now, albums, artists and bands, Eurovision, film songs and music facts. Play on your own, or start a party of up to 6 players with a 5-letter code."),
    },
    {
        "id": "fortnite", "dir": "fortnite", "bank_src": "fortnite_questions.json", "extra": [("fn-peely.png", "peely.png"), ("fn-peely-head.png", "peely-head.png")],
        "title": "OG Fortnite Quiz (Chapter 1) – Obscure Trivia",
        "desc": "A free OG Fortnite quiz on Chapter 1 only, from the Pre-Season to Season X: 20 random questions per game on outfits, Battle Passes, the big moments of every season, the map and its named locations, live events, items and the game's history. Play solo or in party mode with up to 6 players.",
        "fonts": "family=Anton&family=Nunito:wght@600;700;800",
        "theme_color": "#2a6cf0",
        "favicon": "peely-head.png",
        "config": {
            "id": "fortnite", "letter": "N", "short": "OG Fortnite", "icon": "", "namePh": "e.g. Jonesy",
            "eyebrow": "OG Fortnite quiz · Chapter 1", "headline": "Think you know the OG island? Drop in and prove it.",
            "topics": "Chapter 1 only, from the Pre-Season to Season X: outfits and the seasons they arrived in, Battle Passes, the big moments of every season, the map and its named locations, live events, items and the game's history",
            "foot": "OG Fortnite only: Chapter 1, from the Pre-Season to Season X, and nothing later. Outfit and emote seasons come from the Fortnite-API cosmetics database. Seasons, named locations and live events come from the Fortnite Wiki, and map questions count the main Battle Royale island only. Fan-made quiz, not affiliated with Epic Games.",
            "seed": "obscure-trivia-fortnite-ch1-v3:", "topic": "obscure-trivia/fortnite/v3/", "recentKey": "ot-recent-fortnite-v3", "sessionKey": "ot-game-fortnite-v3",
            "bank": "questions.json", "hub": "../",
            "groups": {"outseason": "Outfits", "outfirst": "Outfits", "outseries": "Outfits", "emote": "Outfits", "outbp": "Outfits", "seasonname": "Seasons", "seasontheme": "Seasons", "seasonstart": "Seasons", "season": "Seasons", "bigmoment": "Big moments", "locreplaced": "Map", "locadded": "Map", "loclast": "Map", "loccount": "Map", "locseason": "Map", "map": "Map", "event": "Live events", "item": "Items", "fact": "Fortnite facts"},
            "caps": {"Outfits": 5, "Seasons": 3, "Big moments": 2, "Map": 5, "Live events": 2, "Items": 2, "Fortnite facts": 2},
            "verdicts": [[19, "Victory Royale!"], [16, "Top 3. So close!"], [12, "Top 10 finish."], [8, "Caught in the storm."], [0, "Back to the lobby. Try again!"]],
        },
        "theme": """
:root {
  --bg: #1d4fc4;
  --bg-art: linear-gradient(180deg, #3e8cff 0%, #2a6cf0 45%, #3b2bb8 100%);
  --panel: #13235e; --panel-fill: linear-gradient(180deg, rgba(20, 38, 104, 0.94), rgba(14, 26, 76, 0.95)); --panel-2: #22367f;
  --panel-shadow: 0 14px 34px rgba(8, 10, 50, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.1);
  --line: rgba(255, 255, 255, 0.18); --line-hover: rgba(255, 226, 58, 0.75); --ink: #ffffff; --muted: #c3cdf2; --faint: #9aa8dc; --placeholder: #8796cf;
  --accent: #ffe23a; --accent-ink: #1d1600; --accent-text: #ffe766; --accent-hover: #fff06a; --accent-edge: #fff3a3; --accent-shadow: 0 4px 0 #b39400;
  --chip-bg: rgba(255, 255, 255, 0.1); --chip-line: rgba(255, 255, 255, 0.28); --chip-ink: #ffffff;
  --pal: #ff8ae2; --pal-ink: #2b0022; --pal-bg: rgba(255, 138, 226, 0.14); --pal-line: rgba(255, 138, 226, 0.5);
  --good: #5ef08d; --good-ink: #022b10; --good-bg: rgba(94, 240, 141, 0.15); --bad: #ff6b6b; --bad-ink: #3a0606; --bad-bg: rgba(255, 107, 107, 0.16);
  --inset: #0b1648; --opt: rgba(22, 40, 108, 0.92); --tile: rgba(16, 30, 86, 0.92);
  --card-bg: #ffffff; --card-ink: #13235e; --card-line: #c5d0f5; --card-inner: #e8edfd; --card-strong: #000000;
  --f-display: "Anton", "Impact", "Arial Narrow", sans-serif; --f-body: "Nunito", system-ui, -apple-system, "Segoe UI", sans-serif;
  --r: 10px; --r-panel: 14px; --r-pill: 999px; --r-key: 6px;
  color-scheme: dark;
}
/* blue sky, with the purple storm closing in around the edges */
body { background-attachment: fixed; }
body::before { content: ""; position: fixed; inset: 0; z-index: -1; pointer-events: none;
  background: radial-gradient(circle at 50% 42%, transparent 52%, rgba(136, 52, 240, 0.35) 66%, rgba(98, 26, 200, 0.8) 84%, rgba(70, 14, 160, 0.95) 100%); }
h1, h2, h3, .bigmsg, .verdict, .code-big, .btn.gold { font-family: var(--f-display); font-weight: 400; text-transform: uppercase; letter-spacing: 0.02em; }
.hero h2 { font-size: clamp(2.2rem, 8vw, 3.2rem); line-height: 1.02; text-shadow: 0 3px 0 rgba(10, 16, 70, 0.6); }
.qtext { font-family: var(--f-body); font-weight: 800; font-size: clamp(1.15rem, 4vw, 1.4rem); line-height: 1.3; }
.opt .lbl.big { font-family: var(--f-body); font-weight: 800; font-size: 1.08rem; }
.btn.gold { font-size: 1.1rem; }
@media (max-width: 430px) { .brand { gap: 8px; } .brand h1 { font-size: 1.12rem; letter-spacing: 0; } }
.coin { width: 34px; height: 34px; flex: none; display: block; border-radius: 50%; background: url("peely-head.png") center 20% / 115% auto, #ffe23a;
  box-shadow: 0 0 0 2px #ffe23a, 0 3px 8px rgba(0, 0, 0, 0.35); }
""",
        "tile": {"cls": "fn", "title": "OG Fortnite", "art": "",
                 "blurb": "Chapter 1 only, Season 1 to Season X: outfits, Battle Passes, the big moments, the map, live events and items."},
        "intro": ("OG Fortnite quiz", "Think you know the OG island? Drop in and prove it.",
                  "A free OG Fortnite quiz on Chapter 1, 20 questions per game: outfits and the seasons they arrived in, Battle Passes, the big moments of every season from the Pre-Season to Season X, the map and its named locations, live events, items and the game's history. Play on your own, or start a party of up to 6 players with a 5-letter code."),
    },
    {
        "id": "royale", "dir": "clash-royale", "bank_src": "royale_questions.json", "extra": [("cr-crown.svg", "crown.svg")],
        "title": "Clash Royale Quiz – Obscure Trivia",
        "desc": "A free Clash Royale quiz: 20 random questions per game on every card's Elixir cost, rarity and arena, card descriptions, stats, Evolutions, Heroes, Champions, arenas and game mechanics. Play solo or in party mode with up to 6 players.",
        "fonts": "family=Titan+One&family=Baloo+2:wght@500;600;700;800",
        "theme_color": "#123488",
        "favicon": "crown.svg",
        "config": {
            "id": "royale", "letter": "R", "short": "Clash Royale", "icon": "", "namePh": "e.g. King",
            "eyebrow": "Clash Royale quiz", "headline": "Think you know every card? Go for three crowns.",
            "topics": "every card's Elixir cost, rarity and unlock arena, in-game card descriptions, stats, Evolutions, Heroes and Champions, Trophy Road arenas, card history and game mechanics",
            "foot": "Card facts come from the Clash Royale Wiki (card pages, stat tables, the Arenas, Card Evolution and Heroes pages), up to date as of November 2026. Stats are checked against each card's change history, and stats at the same card level are shown at level 11. Game facts are written by hand. Fan-made quiz, not affiliated with Supercell.",
            "seed": "obscure-trivia-royale-v1:", "topic": "obscure-trivia/royale/v1/", "recentKey": "ot-recent-royale-v1", "sessionKey": "ot-game-royale",
            "bank": "questions.json", "hub": "../",
            "groups": {"cost": "Elixir", "costmost": "Elixir", "costleast": "Elixir", "costone": "Elixir", "rarity": "Rarity", "champpick": "Rarity", "rarpick": "Rarity", "arena": "Arenas", "arenanum": "Arenas", "arenatro": "Arenas", "arenanext": "Arenas", "arenafact": "Arenas", "camp": "Arenas", "quote": "Card descriptions", "speed": "Stats", "target": "Stats", "count": "Stats", "range": "Stats", "hitspeed": "Stats", "hp": "Stats", "dmg": "Stats", "air": "Stats", "spellground": "Stats", "radius": "Stats", "life": "Stats", "deploy": "Stats", "type": "Stats", "spelltime": "Stats", "spellhit": "Stats", "mech": "Mechanics", "spawn": "Mechanics", "spawncount": "Mechanics", "jump": "Mechanics", "evoquote": "Evolutions", "evocycles": "Evolutions", "evohas": "Evolutions", "evoyear": "Evolutions", "evofirst": "Evolutions", "evodesc": "Evolutions", "evofact": "Evolutions", "heroab": "Heroes & Champions", "herodesc": "Heroes & Champions", "herohas": "Heroes & Champions", "heroquote": "Heroes & Champions", "herocost": "Heroes & Champions", "champab": "Heroes & Champions", "champdesc": "Heroes & Champions", "champcost": "Heroes & Champions", "herofact": "Heroes & Champions", "year": "History", "launch": "History", "first": "History", "newest": "History", "fact": "Game facts", "tower": "Game facts"},
            "caps": {"Elixir": 3, "Rarity": 2, "Arenas": 3, "Card descriptions": 3, "Stats": 4, "Mechanics": 2, "Evolutions": 2, "Heroes & Champions": 2, "History": 2, "Game facts": 2},
            "verdicts": [[19, "Three-crown win!"], [16, "Two crowns. So close!"], [12, "One crown. Not bad!"], [8, "It's a draw..."], [0, "Defeat. Back to the Training Camp!"]],
        },
        "theme": """
:root {
  --bg: #123488;
  --bg-art: radial-gradient(ellipse at 50% -8%, rgba(255, 201, 40, 0.28), transparent 46%),
    radial-gradient(ellipse at 0% 100%, rgba(230, 74, 216, 0.2), transparent 45%), radial-gradient(ellipse at 100% 100%, rgba(255, 77, 94, 0.16), transparent 45%),
    linear-gradient(180deg, #1e4cb8 0%, #123488 45%, #0b1f5c 100%);
  --panel: #10296e; --panel-fill: linear-gradient(180deg, rgba(22, 54, 140, 0.95), rgba(13, 34, 96, 0.96)); --panel-2: #1c3f99;
  --panel-shadow: 0 14px 34px rgba(4, 10, 40, 0.5), inset 0 0 0 2px rgba(255, 201, 40, 0.28), inset 0 1px 0 rgba(255, 255, 255, 0.12);
  --line: rgba(255, 255, 255, 0.18); --line-hover: rgba(255, 201, 40, 0.8); --ink: #ffffff; --muted: #c8d5fa; --faint: #9db0e6; --placeholder: #8aa0dc;
  --accent: #ffc928; --accent-ink: #2b1a00; --accent-text: #ffd552; --accent-hover: #ffd94f; --accent-edge: #ffe48a; --accent-shadow: 0 4px 0 #b37b00;
  --chip-bg: rgba(255, 255, 255, 0.1); --chip-line: rgba(255, 255, 255, 0.28); --chip-ink: #ffffff;
  --pal: #f06be6; --pal-ink: #2e0029; --pal-bg: rgba(240, 107, 230, 0.15); --pal-line: rgba(240, 107, 230, 0.5);
  --good: #47e08c; --good-ink: #02290f; --good-bg: rgba(71, 224, 140, 0.15); --bad: #ff5a68; --bad-ink: #3a0610; --bad-bg: rgba(255, 90, 104, 0.16);
  --inset: #0a1c52; --opt: rgba(20, 48, 128, 0.94); --tile: rgba(16, 40, 108, 0.94);
  --card-bg: #ffffff; --card-ink: #10296e; --card-line: #c7d4f7; --card-inner: #e9eefc; --card-strong: #000000;
  --f-display: "Titan One", "Baloo 2", system-ui, sans-serif; --f-body: "Baloo 2", system-ui, -apple-system, "Segoe UI", sans-serif;
  --r: 12px; --r-panel: 16px; --r-pill: 999px; --r-key: 8px;
  color-scheme: dark;
}
body { background-attachment: fixed; }
h1, h2, h3, .bigmsg, .verdict, .code-big, .btn.gold { font-family: var(--f-display); font-weight: 400; letter-spacing: 0.01em; }
.hero h2 { font-size: clamp(2rem, 7.2vw, 2.9rem); line-height: 1.08; text-shadow: 0 3px 0 rgba(6, 16, 60, 0.6); }
.qtext { font-family: var(--f-body); font-weight: 800; font-size: clamp(1.15rem, 4vw, 1.4rem); line-height: 1.28; }
.opt .lbl.big { font-family: var(--f-body); font-weight: 700; font-size: 1.08rem; }
.btn.gold { font-size: 1.1rem; text-shadow: 0 1px 0 rgba(255, 255, 255, 0.35); }
@media (max-width: 430px) { .brand { gap: 8px; } .brand h1 { font-size: 1.12rem; } }
.coin { width: 34px; height: 34px; flex: none; display: block; border-radius: 10px; background: url("crown.svg") center 55% / 84% auto no-repeat, linear-gradient(180deg, #2a5fd6, #163d99);
  box-shadow: 0 0 0 2px #ffc928, 0 3px 8px rgba(0, 0, 0, 0.35); }
""",
        "tile": {"cls": "roy", "title": "Clash Royale", "art": "",
                 "blurb": "Every card's Elixir, rarity and arena, plus Evolutions, Heroes, Champions, stats and mechanics."},
        "intro": ("Clash Royale quiz", "Think you know every card? Go for three crowns.",
                  "A free Clash Royale quiz, 20 questions per game: every card's Elixir cost, rarity and unlock arena, in-game card descriptions, stats, Evolutions, Heroes and Champions, Trophy Road arenas, card history and game mechanics. Play on your own, or start a party of up to 6 players with a 5-letter code."),
    },
    {
        "id": "dbd", "dir": "dead-by-daylight", "bank_src": "dbd_questions.json", "extra": [("dbd-hook.svg", "hook.svg")],
        "title": "Dead by Daylight Quiz – Obscure Trivia",
        "desc": "A free Dead by Daylight quiz: 20 random questions per game on every Killer and Survivor, their perks, powers and lore, realms and maps, Chapters, add-ons and how the Trials work. Play solo or in party mode with up to 6 players.",
        "fonts": "family=Eater&family=Spectral:ital,wght@0,400;0,600;0,700;1,400",
        "theme_color": "#0e0b0d",
        "favicon": "hook.svg",
        "config": {
            "id": "dbd", "letter": "D", "short": "Dead by Daylight", "icon": "", "namePh": "e.g. Dwight",
            "eyebrow": "Dead by Daylight quiz", "headline": "The Entity is watching. Do you know the Fog?",
            "topics": "every Killer and Survivor, their perks, powers and real names, a little lore, realms and maps, Chapters, add-ons, offerings and how the Trials work",
            "foot": "Facts come from the Dead by Daylight Wiki (deadbydaylight.wiki.gg): its data tables, the Perks page and every Killer and Survivor page, up to date as of the Terrifier Chapter (24 November 2026). Lore and game-fact questions are written from those pages. Fan-made quiz, not affiliated with Behaviour Interactive.",
            "seed": "obscure-trivia-dbd-v1:", "topic": "obscure-trivia/dbd/v1/", "recentKey": "ot-recent-dbd-v1", "sessionKey": "ot-game-dbd",
            "bank": "questions.json", "hub": "../",
            "groups": {"ksurname": "Killers", "ktitle": "Killers", "ssurname": "Survivors", "krealname": "Killers", "kname": "Killers", "kpower": "Killers", "kpowerof": "Killers", "kweapon": "Killers", "kspeed": "Killers", "kslow": "Killers", "kradius": "Killers", "kdiff": "Killers", "korigin": "Killers", "kchapter": "Killers", "kyear": "Killers", "kfrom": "Killers", "korder": "Killers", "kcount": "Killers", "srole": "Survivors", "srolename": "Survivors", "sorigin": "Survivors", "schapter": "Survivors", "syear": "Survivors", "sfrom": "Survivors", "sorder": "Survivors", "swith": "Survivors", "powner": "Perks", "pdesc": "Perks", "pquote": "Perks", "ppick": "Perks", "pnotmine": "Perks", "pgeneral": "Perks", "pformer": "Perks", "lore": "Lore", "mrealm": "Realms & Maps", "mlandmark": "Realms & Maps", "mchapter": "Realms & Maps", "rloc": "Realms & Maps", "rmaps": "Realms & Maps", "chkiller": "Chapters", "chsurv": "Chapters", "chyear": "Chapters", "chorder": "Chapters", "chfact": "Chapters", "akiller": "Add-ons & Offerings", "aitem": "Add-ons & Offerings", "orealm": "Add-ons & Offerings", "fact": "Game facts"},
            "caps": {"Killers": 5, "Survivors": 4, "Perks": 5, "Lore": 3, "Realms & Maps": 2, "Chapters": 2, "Add-ons & Offerings": 2, "Game facts": 2},
            "verdicts": [[19, "You escaped. The Entity is displeased."], [16, "Out through the hatch!"], [12, "Hooked twice, but you made it out."], [8, "Sacrificed to the Entity..."], [0, "Mori'd at the first hook. Back to the campfire!"]],
        },
        "theme": """
:root {
  --bg: #0e0b0d;
  --bg-art: radial-gradient(ellipse 90% 55% at 50% -12%, rgba(178, 18, 28, 0.34), transparent 60%),
    linear-gradient(180deg, #1a1114 0%, #0f0c0e 46%, #0b0a0c 100%);
  --panel: #1a1215; --panel-fill: linear-gradient(180deg, rgba(32, 22, 26, 0.95), rgba(19, 14, 16, 0.96)); --panel-2: #271b1f;
  --panel-shadow: 0 14px 34px rgba(0, 0, 0, 0.6), inset 0 0 0 1px rgba(200, 22, 30, 0.26), inset 0 1px 0 rgba(255, 255, 255, 0.05);
  --line: rgba(236, 230, 221, 0.15); --line-hover: rgba(222, 36, 44, 0.8); --ink: #ece6dd; --muted: #bcb1a7; --faint: #91857b; --placeholder: #7d7169;
  --accent: #c8161e; --accent-ink: #fff5f0; --accent-text: #ff6166; --accent-hover: #de2129; --accent-edge: #ff8084; --accent-shadow: 0 4px 0 #620a0e, 0 0 22px rgba(200, 22, 30, 0.32);
  --chip-bg: rgba(255, 255, 255, 0.06); --chip-line: rgba(255, 255, 255, 0.2); --chip-ink: #ece6dd;
  --pal: #9fd8d0; --pal-ink: #03211d; --pal-bg: rgba(159, 216, 208, 0.12); --pal-line: rgba(159, 216, 208, 0.45);
  --good: #63d690; --good-ink: #03240f; --good-bg: rgba(99, 214, 144, 0.13); --bad: #ff5b61; --bad-ink: #2e0306; --bad-bg: rgba(255, 91, 97, 0.14);
  --inset: #0a0809; --opt: rgba(30, 21, 24, 0.94); --tile: rgba(25, 18, 21, 0.94);
  --card-bg: #ece6dd; --card-ink: #1a1215; --card-line: #cfc4b8; --card-inner: #e2d9cd; --card-strong: #000000;
  --f-display: "Eater", "Creepster", Georgia, serif; --f-body: "Spectral", Georgia, "Times New Roman", serif;
  --r: 10px; --r-panel: 14px; --r-pill: 999px; --r-key: 6px;
  color-scheme: dark;
}
body { background-attachment: fixed; }
/* the Fog: two slow banks of mist along the bottom, and the Entity's red glow above */
body::before, body::after { content: ""; position: fixed; left: -10%; right: -10%; bottom: -6%; height: 62%; z-index: -1; pointer-events: none;
  background: radial-gradient(ellipse 38% 55% at 20% 100%, rgba(190, 196, 204, 0.16), transparent 70%),
    radial-gradient(ellipse 34% 48% at 62% 100%, rgba(190, 196, 204, 0.12), transparent 70%),
    radial-gradient(ellipse 30% 42% at 92% 100%, rgba(190, 196, 204, 0.14), transparent 70%); }
body::after { height: 44%; opacity: 0.8;
  background: radial-gradient(ellipse 30% 50% at 38% 100%, rgba(170, 178, 188, 0.13), transparent 70%),
    radial-gradient(ellipse 36% 46% at 80% 100%, rgba(170, 178, 188, 0.1), transparent 70%),
    radial-gradient(ellipse 26% 40% at 4% 100%, rgba(170, 178, 188, 0.12), transparent 70%); }
@media (prefers-reduced-motion: no-preference) {
  body::before { animation: fog-a 38s ease-in-out infinite alternate; }
  body::after { animation: fog-b 52s ease-in-out infinite alternate; }
}
@keyframes fog-a { from { transform: translateX(-4%); } to { transform: translateX(4%); } }
@keyframes fog-b { from { transform: translateX(5%); } to { transform: translateX(-5%); } }
.brand h1, .hero h2, .bigmsg, .verdict, .code-big { font-family: var(--f-display); font-weight: 400; letter-spacing: 0.03em; }
.hero h2 { font-size: clamp(2.1rem, 7.6vw, 3.1rem); line-height: 1.08; color: #f1ebe2; text-shadow: 0 0 22px rgba(200, 22, 30, 0.45), 0 3px 0 rgba(0, 0, 0, 0.6); }
.verdict { color: #f1ebe2; text-shadow: 0 0 18px rgba(200, 22, 30, 0.5); }
h2, h3 { font-family: var(--f-body); font-weight: 700; letter-spacing: 0.01em; }
.qtext { font-family: var(--f-body); font-weight: 700; font-size: clamp(1.15rem, 4vw, 1.42rem); line-height: 1.3; }
.opt .lbl.big { font-family: var(--f-body); font-weight: 700; font-size: 1.08rem; }
.btn.gold { font-family: var(--f-body); font-weight: 700; font-size: 1.08rem; letter-spacing: 0.04em; text-transform: uppercase; }
.why { font-style: normal; font-family: var(--f-body); font-size: 0.98rem; }
@media (max-width: 430px) { .brand { gap: 8px; } .brand h1 { font-size: 1.05rem; letter-spacing: 0.01em; } }
.coin { width: 34px; height: 34px; flex: none; display: block; border-radius: 50%;
  background: url("hook.svg") 46% 50% / 84% auto no-repeat, radial-gradient(circle at 50% 35%, #3a1418, #120a0c);
  box-shadow: 0 0 0 2px #b3141b, 0 0 14px rgba(200, 22, 30, 0.45); }
""",
        "tile": {"cls": "dbd", "title": "Dead by Daylight", "art": "",
                 "blurb": "Killers, Survivors, perks, powers, a little lore, realms and maps. The Entity is watching."},
        "intro": ("Dead by Daylight quiz", "The Entity is watching. Do you know the Fog?",
                  "A free Dead by Daylight quiz, 20 questions per game: every Killer and Survivor, their perks, powers and real names, a little lore, realms and maps, Chapters, add-ons, offerings and how the Trials work. Play on your own, or start a party of up to 6 players with a 5-letter code."),
    },
    {
        "id": "animals", "dir": "animals", "bank_src": "animals_questions.json", "extra": [("an-paw.svg", "paw.svg")],
        "title": "Animals Quiz – Obscure Trivia",
        "desc": "A free animals quiz: 20 random questions per game on baby animal names, what groups of animals are called, records, amazing bodies and behaviour, habitats, diets, classification, dog and cat breeds, endangered species and national animals. Play solo or in party mode with up to 6 players.",
        "fonts": "family=Fredoka:wght@500;600;700&family=Lexend:wght@400;500;600;700",
        "theme_color": "#0f2a1f",
        "favicon": "paw.svg",
        "config": {
            "id": "animals", "letter": "A", "short": "Animals", "icon": "", "namePh": "e.g. Koala",
            "eyebrow": "Animals quiz", "headline": "From joeys to giant squid: how wild is your animal knowledge?",
            "topics": "baby animal names, what groups of animals are called, records, amazing bodies and behaviour, habitats, diets, classification, dog and cat breeds, endangered species and national animals",
            "foot": "Facts come from English Wikipedia: the List of animal names, the List of national animals and each animal's own article (class and conservation status from its taxonomy box), with dog and cat breeds from Wikidata. Records, bodies, behaviour, habitat and diet questions are written from Wikipedia articles, each checked against the article's text.",
            "seed": "obscure-trivia-animals-v1:", "topic": "obscure-trivia/animals/v1/", "recentKey": "ot-recent-animals-v1", "sessionKey": "ot-game-animals",
            "bank": "questions.json", "hub": "../",
            "groups": {"young": "Baby animals", "younghard": "Baby animals", "group": "Animal groups", "male": "Males & females", "female": "Males & females", "adj": "Animal words", "adjrev": "Animal words", "cls": "Classification", "clspick": "Classification", "clsnot": "Classification", "legs": "Classification", "iucn": "Endangered", "iucnpick": "Endangered", "dog": "Dogs & cats", "dogpick": "Dogs & cats", "cat": "Dogs & cats", "nat": "National animals", "natrev": "National animals", "records": "Records", "bodies": "Bodies", "behaviour": "Behaviour", "habitats": "Habitats", "diet": "Diet", "dietpick": "Diet"},
            "caps": {"Baby animals": 2, "Animal groups": 2, "Males & females": 1, "Animal words": 1, "Classification": 3, "Endangered": 1, "Dogs & cats": 2, "National animals": 2, "Records": 2, "Bodies": 2, "Behaviour": 2, "Habitats": 1, "Diet": 2},
            "verdicts": [[19, "Top of the food chain!"], [16, "King of the jungle!"], [12, "Wise old owl."], [8, "Still a cub. Keep learning!"], [0, "Lost in the jungle. Try again!"]],
        },
        "theme": """
:root {
  --bg: #0f2a1f;
  --bg-art: radial-gradient(ellipse 70% 50% at 0% 0%, rgba(120, 200, 90, 0.22), transparent 60%), radial-gradient(ellipse 60% 50% at 100% 10%, rgba(255, 190, 70, 0.16), transparent 60%),
    linear-gradient(180deg, #17432f 0%, #0f2a1f 55%, #0b2018 100%);
  --panel: #133524; --panel-fill: linear-gradient(180deg, rgba(24, 66, 45, 0.95), rgba(16, 46, 32, 0.96)); --panel-2: #1c4a33;
  --panel-shadow: 0 14px 34px rgba(2, 14, 8, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.08);
  --line: rgba(240, 236, 220, 0.16); --line-hover: rgba(255, 178, 56, 0.8); --ink: #f4f1e6; --muted: #c4d4c0; --faint: #97ad94; --placeholder: #86a083;
  --accent: #ffb238; --accent-ink: #2b1600; --accent-text: #ffc861; --accent-hover: #ffc252; --accent-edge: #ffd98f; --accent-shadow: 0 4px 0 #b06d10;
  --chip-bg: rgba(255, 255, 255, 0.08); --chip-line: rgba(255, 255, 255, 0.22); --chip-ink: #f4f1e6;
  --pal: #7fd4ff; --pal-ink: #00222e; --pal-bg: rgba(127, 212, 255, 0.13); --pal-line: rgba(127, 212, 255, 0.45);
  --good: #8be07a; --good-ink: #0c2a05; --good-bg: rgba(139, 224, 122, 0.15); --bad: #ff7a6b; --bad-ink: #3a0904; --bad-bg: rgba(255, 122, 107, 0.15);
  --inset: #0a1e15; --opt: rgba(20, 56, 38, 0.94); --tile: rgba(17, 48, 33, 0.94);
  --card-bg: #f4f1e6; --card-ink: #133524; --card-line: #cfd9c6; --card-inner: #e6eedf; --card-strong: #000000;
  --f-display: "Fredoka", "Nunito", system-ui, sans-serif; --f-body: "Lexend", system-ui, -apple-system, "Segoe UI", sans-serif;
  --r: 14px; --r-panel: 18px; --r-pill: 999px; --r-key: 9px;
  color-scheme: dark;
}
body { background-attachment: fixed; }
/* a trail of faint paw prints across the page */
body::before { content: ""; position: fixed; inset: 0; z-index: -1; pointer-events: none; background: url("PAW_BG") 0 0 / 120px 120px; }
h1, h2, h3, .bigmsg, .verdict, .code-big, .btn.gold { font-family: var(--f-display); font-weight: 700; letter-spacing: 0; }
.hero h2 { font-size: clamp(2rem, 7vw, 2.9rem); line-height: 1.08; }
.qtext { font-family: var(--f-body); font-weight: 600; font-size: clamp(1.12rem, 4vw, 1.38rem); line-height: 1.32; }
.opt .lbl.big { font-family: var(--f-display); font-weight: 600; font-size: 1.12rem; }
.btn.gold { font-size: 1.1rem; }
.coin { width: 34px; height: 34px; flex: none; display: block; border-radius: 50%; background: url("paw.svg") center / 70% auto no-repeat, #1c4a33;
  box-shadow: 0 0 0 2px #ffb238, 0 3px 8px rgba(0, 0, 0, 0.35); }
""".replace("PAW_BG", "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='120' viewBox='0 0 64 64'%3E%3Cg fill='%23ffffff' fill-opacity='0.045' transform='rotate(-20 32 32) translate(16 16) scale(0.5)'%3E%3Cellipse cx='32' cy='43' rx='14.5' ry='12.5'/%3E%3Cellipse cx='14.5' cy='28' rx='6' ry='7.6'/%3E%3Cellipse cx='25.5' cy='16.5' rx='6' ry='8'/%3E%3Cellipse cx='38.5' cy='16.5' rx='6' ry='8'/%3E%3Cellipse cx='49.5' cy='28' rx='6' ry='7.6'/%3E%3C/g%3E%3C/svg%3E"),
        "tile": {"cls": "an", "title": "Animals", "art": "",
                 "blurb": "Baby animal names, groups, record breakers, amazing bodies, habitats, breeds and national animals."},
        "intro": ("Animals quiz", "From joeys to giant squid: how wild is your animal knowledge?",
                  "A free animals quiz, 20 questions per game: baby animal names, what groups of animals are called, records, amazing bodies and behaviour, habitats, diets, classification, dog and cat breeds, endangered species and national animals. Play on your own, or start a party of up to 6 players with a 5-letter code."),
    },
    {
        "id": "odd", "dir": "odd-one-out", "bank_src": "odd_questions.json", "section": "games", "extra": [("odd-icon.svg", "icon.svg")],
        "title": "Odd One Out – Spot What Doesn't Belong – Obscure Trivia",
        "desc": "Odd One Out is a free puzzle game: four things, three of them share something, and you pick the one that doesn't belong. 20 rounds per game on animals, geography, numbers, science, food, music, sport, films, games and more. Play solo or in party mode with up to 6 players.",
        "fonts": "family=Bungee&family=Plus+Jakarta+Sans:wght@400;500;600;700;800",
        "theme_color": "#15132b",
        "favicon": "icon.svg",
        "config": {
            "id": "odd", "letter": "X", "short": "Odd One Out", "icon": "", "namePh": "e.g. Sam",
            "eyebrow": "Puzzle game", "headline": "Three of them belong together. Which one doesn't?",
            "topics": "animals, geography, numbers, science, space, food, music, sport, films, myths, brands, cars and games",
            "foot": "Every round is built from a table of things and their features, and only kept if no other feature would single out a different one of the four. Countries come from Wikidata, animals from Wikipedia, and games from the same checked data as this site's game quizzes; the rest is checked against Wikipedia.",
            "seed": "obscure-trivia-odd-v1:", "topic": "obscure-trivia/odd/v1/", "recentKey": "ot-recent-odd-v1", "sessionKey": "ot-game-odd",
            "bank": "questions.json", "hub": "../",
            "groups": {},
            "caps": {},
            "verdicts": [[19, "Eagle eye! Nothing gets past you."], [16, "Sharp spotter!"], [12, "You've got a good eye."], [8, "Some odd choices there..."], [0, "Were you the odd one out?"]],
        },
        "theme": """
:root {
  --bg: #15132b;
  --bg-art: radial-gradient(ellipse 70% 50% at 100% 0%, rgba(255, 107, 91, 0.2), transparent 60%), radial-gradient(ellipse 70% 60% at 0% 100%, rgba(55, 214, 195, 0.16), transparent 60%),
    linear-gradient(180deg, #1d1a3a 0%, #15132b 60%, #100e22 100%);
  --panel: #1f1c3f; --panel-fill: linear-gradient(180deg, rgba(36, 32, 72, 0.95), rgba(26, 23, 54, 0.96)); --panel-2: #2a2652;
  --panel-shadow: 0 14px 34px rgba(5, 4, 20, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.08);
  --line: rgba(243, 241, 255, 0.15); --line-hover: rgba(55, 214, 195, 0.8); --ink: #f3f1ff; --muted: #c4c0e6; --faint: #9a95c4; --placeholder: #8984b5;
  --accent: #ff6b5b; --accent-ink: #2a0500; --accent-text: #ff8c7f; --accent-hover: #ff8172; --accent-edge: #ffb3aa; --accent-shadow: 0 4px 0 #a8382b;
  --chip-bg: rgba(255, 255, 255, 0.08); --chip-line: rgba(255, 255, 255, 0.22); --chip-ink: #f3f1ff;
  --pal: #37d6c3; --pal-ink: #00241f; --pal-bg: rgba(55, 214, 195, 0.13); --pal-line: rgba(55, 214, 195, 0.5);
  --good: #5fe39a; --good-ink: #022812; --good-bg: rgba(95, 227, 154, 0.14); --bad: #ff6b7a; --bad-ink: #33040b; --bad-bg: rgba(255, 107, 122, 0.15);
  --inset: #100e24; --opt: rgba(34, 30, 68, 0.95); --tile: rgba(28, 25, 58, 0.95);
  --card-bg: #f3f1ff; --card-ink: #1f1c3f; --card-line: #cfcbea; --card-inner: #e6e3fa; --card-strong: #000000;
  --f-display: "Bungee", "Arial Black", system-ui, sans-serif; --f-body: "Plus Jakarta Sans", system-ui, -apple-system, "Segoe UI", sans-serif;
  --r: 14px; --r-panel: 18px; --r-pill: 999px; --r-key: 8px;
  color-scheme: dark;
}
body { background-attachment: fixed; }
h1, h2, h3, .bigmsg, .verdict, .code-big { font-family: var(--f-display); font-weight: 400; letter-spacing: 0.01em; }
.hero h2 { font-size: clamp(1.8rem, 6.4vw, 2.6rem); line-height: 1.12; }
.qtext { font-family: var(--f-body); font-weight: 800; font-size: clamp(1.15rem, 4vw, 1.4rem); line-height: 1.3; }
.btn.gold { font-family: var(--f-display); font-weight: 400; font-size: 1.05rem; letter-spacing: 0.02em; }
/* the four things sit in a 2 by 2 grid, like cards on a table */
.opts:not(.duel) { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
.opts:not(.duel) .opt { position: relative; flex-direction: column; align-items: center; justify-content: center; text-align: center; min-height: 108px; padding: 30px 10px 16px; }
.opts:not(.duel) .opt .key { position: absolute; top: 9px; left: 9px; }
.opts:not(.duel) .opt .lbl { flex: none; padding: 0; text-wrap: balance; font-family: var(--f-body); font-weight: 800; font-size: clamp(1rem, 3.6vw, 1.15rem); line-height: 1.25; }
.opts:not(.duel) .opt .marks { position: absolute; top: 9px; right: 9px; }
.opts:not(.duel) .opt:nth-child(4n+1) { border-color: rgba(55, 214, 195, 0.35); } .opts:not(.duel) .opt:nth-child(4n+2) { border-color: rgba(255, 199, 89, 0.35); }
.opts:not(.duel) .opt:nth-child(4n+3) { border-color: rgba(160, 140, 255, 0.4); } .opts:not(.duel) .opt:nth-child(4n+4) { border-color: rgba(255, 107, 91, 0.4); }
.opts:not(.duel) .opt.right { border-color: var(--good); } .opts:not(.duel) .opt.wrong { border-color: var(--bad); }
.coin { width: 34px; height: 34px; flex: none; display: block; background: url("icon.svg") center / 100% 100% no-repeat; }
""",
        "tile": {"cls": "odd", "title": "Odd One Out", "art": '<span class="odd-grid" aria-hidden="true"><i></i><i></i><i></i><b></b></span>',
                 "blurb": "Four things, three belong together. Spot the one that doesn't, from animals to Clash Royale cards."},
        "intro": ("Puzzle game", "Three of them belong together. Which one doesn't?",
                  "Odd One Out is a free puzzle game, 20 rounds per game: four things, three share something, and you pick the one that doesn't belong. Animals, geography, numbers, science, food, music, sport, films, games and more. Play on your own, or start a party of up to 6 players with a 5-letter code."),
    },
    {
        "id": "timeline", "dir": "timeline", "bank_src": "timeline_questions.json", "section": "games", "extra": [("tl-icon.svg", "icon.svg")],
        "title": "Timeline – What Came First? – Obscure Trivia",
        "desc": "Timeline is a free history game: which came first, which came last, put four events in order, and what year things happened. History, inventions, space, science, tech, films, music, sport and games. 20 rounds per game, solo or in party mode with up to 6 players.",
        "fonts": "family=Abril+Fatface&family=Libre+Franklin:wght@400;500;600;700;800",
        "theme_color": "#f3e9d2",
        "favicon": "icon.svg",
        "config": {
            "id": "timeline", "letter": "Y", "short": "Timeline", "icon": "", "namePh": "e.g. Sam",
            "eyebrow": "History game", "headline": "Which came first? Put history in order.",
            "topics": "history, inventions, space, science and medicine, internet and tech, films, music, sport, video games and landmarks",
            "foot": "Every date comes from English Wikipedia and is checked against the article's own words, apart from the Clash Royale, Dead by Daylight and football dates, which come from the same checked data as this site's quizzes. Events are only compared when their dates are clearly apart.",
            "seed": "obscure-trivia-timeline-v1:", "topic": "obscure-trivia/timeline/v1/", "recentKey": "ot-recent-timeline-v1", "sessionKey": "ot-game-timeline",
            "bank": "questions.json", "hub": "../",
            "groups": {}, "caps": {},
            "verdicts": [[19, "A walking history book!"], [16, "Time lord!"], [12, "Pretty good timing."], [8, "A bit out of order..."], [0, "Lost in time. Try again!"]],
        },
        "theme": """
:root {
  --bg: #f3e9d2;
  --bg-art: radial-gradient(ellipse 80% 60% at 50% -10%, rgba(255, 255, 255, 0.6), transparent 60%),
    repeating-linear-gradient(0deg, rgba(122, 74, 36, 0.035) 0 1px, transparent 1px 28px), linear-gradient(180deg, #f6eedb 0%, #f0e3c7 100%);
  --panel: #fffaf0; --panel-fill: #fffaf0; --panel-2: #f6ecd6;
  --panel-shadow: 0 1px 0 #d9c7a2, 0 12px 26px rgba(90, 60, 20, 0.14);
  --line: rgba(78, 52, 24, 0.22); --line-hover: #b5452b; --ink: #2e2414; --muted: #6d5a3d; --faint: #8c7856; --placeholder: #a39070;
  --accent: #b5452b; --accent-ink: #fff8ec; --accent-text: #9c3820; --accent-hover: #c65536; --accent-edge: #e08d70; --accent-shadow: 0 4px 0 #7a2c19;
  --chip-bg: #f6ecd6; --chip-line: rgba(78, 52, 24, 0.25); --chip-ink: #2e2414;
  --pal: #2f6f8f; --pal-ink: #ffffff; --pal-bg: rgba(47, 111, 143, 0.1); --pal-line: rgba(47, 111, 143, 0.5);
  --good: #2e7d46; --good-ink: #ffffff; --good-bg: #dff1e3; --bad: #b8323b; --bad-ink: #ffffff; --bad-bg: #f8e0e0;
  --inset: #fbf4e4; --opt: #fffaf0; --tile: #fffaf0;
  --card-bg: #fffdf6; --card-ink: #2e2414; --card-line: #d9c7a2; --card-inner: #f6ecd6; --card-strong: #000000;
  --f-display: "Abril Fatface", Georgia, serif; --f-body: "Libre Franklin", system-ui, -apple-system, "Segoe UI", sans-serif;
  --r: 10px; --r-panel: 14px; --r-pill: 999px; --r-key: 6px;
  color-scheme: light;
}
h1, h2, h3, .bigmsg, .verdict, .code-big { font-family: var(--f-display); font-weight: 400; letter-spacing: 0.01em; }
.hero h2 { font-size: clamp(2rem, 7vw, 2.9rem); line-height: 1.08; }
.qtext { font-family: var(--f-body); font-weight: 800; font-size: clamp(1.12rem, 4vw, 1.36rem); line-height: 1.3; }
.opt .lbl.big { font-family: var(--f-body); font-weight: 700; font-size: 1.06rem; }
.btn.gold { font-family: var(--f-body); font-weight: 800; letter-spacing: 0.04em; text-transform: uppercase; }
/* the events to put in order, pinned along a timeline */
.evlist { position: relative; padding-left: 14px; }
.evlist::before { content: ""; position: absolute; left: 4px; top: 8px; bottom: 8px; width: 3px; border-radius: 2px; background: linear-gradient(#b5452b, #e2a33a); }
.evlist li { box-shadow: 0 2px 0 #e4d4b2; }
.coin { width: 34px; height: 34px; flex: none; display: block; border-radius: 50%; background: url("icon.svg") center / 74% auto no-repeat, #fffaf0;
  box-shadow: 0 0 0 2px #b5452b; }
""",
        "tile": {"cls": "tl", "title": "Timeline", "art": '<span class="tl-line" aria-hidden="true"><i></i><i></i><i></i><i></i></span>',
                 "blurb": "Which came first? Put events in order, from the pyramids to the first iPhone."},
        "intro": ("History game", "Which came first? Put history in order.",
                  "Timeline is a free history game, 20 rounds per game: which came first, which came last, put four events in order, and what year things happened, across history, inventions, space, science, tech, films, music, sport and games. Play on your own, or start a party of up to 6 players with a 5-letter code."),
    },
    {
        "id": "bigger", "dir": "this-or-that", "bank_src": "bigger_questions.json", "section": "games",
        "aliases": ["B"], "old_dirs": ["which-is-bigger"],   # it was called Which Is Bigger? at first
        "title": "This or That – Higher or Lower Game – Obscure Trivia",
        "desc": "This or That is a free head-to-head numbers game: two things go up against each other and you pick the right one. 20 questions per game on heights, areas, populations, speeds, weights, dates, space, science, sport and food. Play solo or in party mode with up to 6 players.",
        "fonts": "family=Lilita+One&family=Rubik:wght@400;500;600;700",
        "theme_color": "#fff3dc",
        "favicon": "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect x='2' y='2' width='60' height='60' rx='16' fill='%231b1b2f'/%3E%3Crect x='13' y='30' width='15' height='22' rx='3' fill='%23ff6b57'/%3E%3Crect x='36' y='12' width='15' height='40' rx='3' fill='%233d7bff'/%3E%3C/svg%3E",
        "extra": [],
        "config": {
            "id": "bigger", "letter": "T", "short": "This or That", "icon": "",
            "eyebrow": "Head-to-head numbers game", "headline": "Two things go head to head. Which one is bigger?",
            "topics": "heights, areas, populations, lengths, weights, speeds, dates, space, science, sport and food",
            "foot": "Country populations come from the World Bank (2025), country areas from the world-countries dataset and Premier League seasons from openfootball. Everything else uses well-known published figures, and two things are only paired when the gap between them is clearly bigger than any disagreement between sources.",
            "seed": "obscure-trivia-bigger-v1:", "topic": "obscure-trivia/bigger/v1/", "recentKey": "ot-recent-bigger-v1", "sessionKey": "ot-game-bigger",
            "bank": "questions.json", "hub": "../",
            "groups": {"height": "Height", "area": "Area", "population": "Population", "length": "Length", "weight": "Weight", "speed": "Speed", "lifespan": "Lifespan", "dates": "Dates", "numbers": "Numbers", "diameter": "Space", "spin": "Space", "gravity": "Space", "heat": "Heat", "protons": "Science", "density": "Science", "melting": "Science", "stadium": "Sport", "ball": "Sport", "plseasons": "Sport", "calories": "Food", "chilli": "Food", "caffeine": "Food", "distance": "Distance"},
            "caps": {"Height": 2, "Area": 2, "Population": 2, "Length": 2, "Weight": 2, "Speed": 2, "Lifespan": 1, "Dates": 3, "Numbers": 3, "Space": 2, "Heat": 2, "Science": 2, "Sport": 2, "Food": 2, "Distance": 1},
            "verdicts": [[19, "Human measuring tape."], [16, "Brilliant sense of scale."], [12, "Bigger brain than most."], [8, "Size isn't everything."], [0, "Was it the other one?"]],
        },
        "theme": """
:root {
  --bg: #fff3dc;
  --bg-art: radial-gradient(circle, rgba(27, 27, 47, 0.09) 1.2px, transparent 1.7px) 0 0 / 18px 18px;
  --panel: #fffdf7; --panel-fill: #fffdf7; --panel-2: #fff0cc;
  --panel-shadow: 6px 6px 0 #1b1b2f;
  --line: #1b1b2f; --line-hover: #1b1b2f; --ink: #1b1b2f; --muted: #57546b; --faint: #75728a; --placeholder: #9895aa;
  --accent: #ffcd29; --accent-ink: #1b1b2f; --accent-text: #c2410c; --accent-hover: #ffd94f; --accent-edge: #1b1b2f; --accent-shadow: 3px 3px 0 #1b1b2f;
  --chip-bg: #fff0cc; --chip-line: #1b1b2f; --chip-ink: #1b1b2f;
  --pal: #2563eb; --pal-ink: #ffffff; --pal-bg: rgba(37, 99, 235, 0.1); --pal-line: #2563eb;
  --good: #15803d; --good-ink: #ffffff; --good-bg: #d7f5de; --bad: #dc2626; --bad-ink: #ffffff; --bad-bg: #fde3e3;
  --inset: #ffffff; --opt: #ffffff; --tile: #fff8e8;
  --card-bg: #ffffff; --card-ink: #1b1b2f; --card-line: #1b1b2f; --card-inner: #fff0cc; --card-strong: #000000;
  --f-display: "Lilita One", "Arial Rounded MT Bold", system-ui, sans-serif; --f-body: "Rubik", system-ui, -apple-system, "Segoe UI", sans-serif;
  --r: 14px; --r-panel: 18px; --r-pill: 999px; --r-key: 8px;
  --side-a: #ff6b57; --side-a-bg: #ffe2dc; --side-b: #3d7bff; --side-b-bg: #dfe9ff;
  color-scheme: light;
}
/* a warm side and a cool side, like a versus screen */
body::before { content: ""; position: fixed; inset: 0; z-index: -1; pointer-events: none;
  background: radial-gradient(circle, rgba(27, 27, 47, 0.1) 1.2px, transparent 1.7px) 0 0 / 18px 18px,
    linear-gradient(115deg, #ffdcd2 0 50%, #d9e6ff 50% 100%); }
.c2 { --pc: #7c3aed; --pc-ink: #ffffff; } .c3 { --pc: #db2777; --pc-ink: #ffffff; }
.c4 { --pc: #c2410c; --pc-ink: #ffffff; } .c5 { --pc: #047857; --pc-ink: #ffffff; }
.board { border-width: 2.5px; }
.btn { border-width: 2.5px; border-color: var(--line); background: #ffffff; box-shadow: 3px 3px 0 var(--line); }
.btn:active { transform: translate(2px, 2px); box-shadow: 1px 1px 0 var(--line); }
.btn.skip { box-shadow: none; }
.input { border-width: 2.5px; }
.chip { border-width: 1.5px; font-weight: 600; }
.pip { background: #eadcb8; }
.timer { background: #eadcb8; }
.divider::before, .divider::after { background: #d9c79c; }
.opt { border-width: 2.5px; box-shadow: 4px 4px 0 var(--line); transition: transform .1s ease, box-shadow .1s ease, background .12s ease; }
.opt:hover:not([disabled]) { background: var(--opt); transform: translate(-2px, -2px); box-shadow: 6px 6px 0 var(--line); }
.opt .key { border: 2px solid var(--line); background: #ffffff; color: var(--ink); }
.opt.card.side-a { background: var(--side-a-bg); }
.opt.card.side-b { background: var(--side-b-bg); }
.opt.card.side-a:hover:not([disabled]) { background: var(--side-a-bg); }
.opt.card.side-b:hover:not([disabled]) { background: var(--side-b-bg); }
.opt.card.side-a .key { background: var(--side-a); color: #ffffff; }
.opt.card.side-b .key { background: var(--side-b); color: #ffffff; }
.opt.card.right { background: var(--good-bg); border-color: var(--good); box-shadow: 4px 4px 0 var(--good); }
.opt.card.wrong { background: var(--bad-bg); border-color: var(--bad); box-shadow: 4px 4px 0 var(--bad); }
.opt.card.faded { opacity: 0.6; }
.opt.card .val { color: var(--ink); }
.opt.card.right .val { color: var(--good); }
.opts.duel .vs { background: var(--ink); color: var(--accent); width: 54px; height: 54px; font-size: 1.2rem; transform: rotate(-8deg);
  box-shadow: 3px 3px 0 var(--accent-text); }
.why { background: #ffffff; border: 2px dashed var(--line); }
.feed-btn, .feed-panel { border-width: 2px; border-color: var(--line); }
.feed-btn { background: #ffffff; color: var(--ink); }
.coin { width: 32px; height: 32px; flex: none; display: block; background: url("BARS") center / 100% 100%; }
""".replace("BARS", "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect x='2' y='2' width='60' height='60' rx='16' fill='%231b1b2f'/%3E%3Crect x='13' y='30' width='15' height='22' rx='3' fill='%23ff6b57'/%3E%3Crect x='36' y='12' width='15' height='40' rx='3' fill='%233d7bff'/%3E%3C/svg%3E"),
        "tile": {"cls": "wb", "title": "This or That", "art": '<span class="vs-badge" aria-hidden="true">VS</span>',
                 "blurb": "Two things go head to head. Taller, heavier, faster, older: can you pick the right one?"},
        "intro": ("Head-to-head numbers game", "Two things go head to head. Which one is bigger?",
                  "A free head-to-head numbers game, 20 questions per game: heights, areas, populations, lengths, weights, speeds, dates, space, science, sport and food. Play on your own, or start a party of up to 6 players with a 5-letter code."),
    },
]
# the order tiles appear in on the home page: games first, then everything else
# games whose topics come from their question banks: <id>_groups.json maps each question's c to its topic
for _q in QUIZZES:
    _gf = os.path.join(SRC, _q["id"] + "_groups.json")
    if _q["id"] in ("odd", "timeline") and os.path.exists(_gf):
        _groups = json.load(open(_gf))
        _q["config"]["groups"] = _groups
        _q["config"]["caps"] = {g: 3 for g in sorted(set(_groups.values()))}
HUB_ORDER = ["world", "hearthstone", "minecraft", "fortnite", "royale", "dbd", "animals", "football", "cars", "music", "bigger", "odd", "timeline"]
QUIZZES.sort(key=lambda q: HUB_ORDER.index(q["id"]) if q["id"] in HUB_ORDER else len(HUB_ORDER))

BASE_CSS = """:root { padding-top: env(safe-area-inset-top, 0px); padding-bottom: env(safe-area-inset-bottom, 0px); }
body { margin: 0; }
img { max-width: 100%; }
[hidden] { display: none !important; }
.top-links { gap: 8px; }
.top-links a { text-decoration: none; color: inherit; }
"""


def head(title, desc, url, fonts, theme_color, favicon, extra_head="", image="social.png", ld=None):
    ld_tag = f'<script type="application/ld+json">{json.dumps(ld)}</script>' if ld else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{url}">
<meta name="google-site-verification" content="{VERIFY}">
<meta property="og:site_name" content="Obscure Trivia">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{url}{image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="{theme_color}">
<link rel="icon" href="{favicon}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?{fonts}&display=swap">
{ld_tag}
{extra_head}
</head>
<body>
"""


os.makedirs(os.path.join(OUT, "assets"), exist_ok=True)
shutil.copy(os.path.join(SRC, "quiz.css"), os.path.join(OUT, "assets", "quiz.css"))
with open(os.path.join(OUT, "assets", "quiz.css"), "a", encoding="utf-8") as f:
    f.write("\n" + BASE_CSS)
shutil.copy(os.path.join(SRC, "engine.js"), os.path.join(OUT, "assets", "quiz.js"))
# accounts: the Supabase project's address and public key (safe to publish). Empty until the project exists.
ACCOUNTS = {"url": os.environ.get("ACCOUNTS_URL", ""), "key": os.environ.get("ACCOUNTS_KEY", "")}
if not ACCOUNTS["url"] and os.path.exists(os.path.join(SRC, "accounts.json")):
    ACCOUNTS = json.load(open(os.path.join(SRC, "accounts.json")))
acc_js = open(os.path.join(SRC, "account.js"), encoding="utf-8").read()
a, b = acc_js.index("/*ACCOUNTS*/"), acc_js.index("/*END*/")
acc_js = acc_js[:a] + "/*ACCOUNTS*/" + json.dumps({"url": ACCOUNTS.get("url", ""), "key": ACCOUNTS.get("key", "")}) + acc_js[b:]
open(os.path.join(OUT, "assets", "account.js"), "w", encoding="utf-8").write(acc_js)

def stamp(path):
    return hashlib.sha1(open(path, "rb").read()).hexdigest()[:10]
V_CSS, V_JS = stamp(os.path.join(OUT, "assets", "quiz.css")), stamp(os.path.join(OUT, "assets", "quiz.js"))
V_ACC = stamp(os.path.join(OUT, "assets", "account.js"))
for qz in QUIZZES:
    qz["config"]["others"] = {l: "../" + o["dir"] + "/" for o in QUIZZES if o is not qz for l in [o["config"]["letter"]] + o.get("aliases", [])}
    # every quiz a host can move their party to (this one included)
    qz["config"]["catalog"] = [{"letter": o["config"]["letter"], "name": o["tile"]["title"], "url": "./" if o is qz else "../" + o["dir"] + "/"} for o in QUIZZES]
for qz in QUIZZES:
    d = os.path.join(OUT, qz["dir"])
    os.makedirs(d, exist_ok=True)
    shutil.copy(os.path.join(SRC, qz["bank_src"]), os.path.join(d, "questions.json"))
    for src, dst in qz.get("extra", []):
        sp, dp = os.path.join(SRC, src), os.path.join(d, dst)
        if os.path.isdir(sp):
            shutil.rmtree(dp, ignore_errors=True); shutil.copytree(sp, dp)
        else:
            shutil.copy(sp, dp)
    url = SITE + qz["dir"] + "/"
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "WebApplication", "name": qz["title"].split(" – ")[0], "url": url, "applicationCategory": "GameApplication",
         "operatingSystem": "Any", "description": qz["desc"], "isPartOf": {"@type": "WebSite", "name": "Obscure Trivia", "url": SITE},
         "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Obscure Trivia", "item": SITE},
            {"@type": "ListItem", "position": 2, "name": qz["title"].split(" – ")[0], "item": url}]}]}
    page = head(qz["title"], qz["desc"], url, qz["fonts"], qz["theme_color"], qz["favicon"],
                extra_head=f'<link rel="stylesheet" href="../assets/quiz.css?v={V_CSS}">\n<style>{qz["theme"]}</style>', ld=ld)
    eb, h2, p = qz["intro"]
    cfg = qz["config"]
    page += f"""<div class="wrap" id="app">
  <header class="top"><div class="brand"><span class="coin" aria-hidden="true">{E(cfg['icon'])}</span><h1>{E(cfg['short'])}</h1></div><a class="btn copy" href="../">All quizzes</a></header>
  <section class="hero">
    <span class="eyebrow">{E(eb)}</span>
    <h2>{E(h2)}</h2>
    <p>{E(p)}</p>
  </section>
  <div class="loading">Loading the questions…</div>
  <noscript><p class="center muted">This quiz needs JavaScript turned on.</p></noscript>
</div>
<script>window.QUIZ = {json.dumps(cfg)};</script>
<script src="../assets/account.js?v={V_ACC}"></script>
<script src="../assets/quiz.js?v={V_JS}"></script>
</body>
</html>
"""
    open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(page)
    for old in qz.get("old_dirs", []):
        od = os.path.join(OUT, old)
        os.makedirs(od, exist_ok=True)
        name = qz["title"].split(" – ")[0]
        open(os.path.join(od, "index.html"), "w", encoding="utf-8").write(f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(name)} – Obscure Trivia</title>
<meta name="robots" content="noindex">
<link rel="canonical" href="{url}">
<meta http-equiv="refresh" content="0; url=../{qz['dir']}/">
<script>location.replace("../{qz['dir']}/" + location.search + location.hash);</script>
<style>body{{margin:0;padding:40px 16px;font:16px/1.5 system-ui,sans-serif;background:{qz['theme_color']};color:#1b1b2f;text-align:center}}</style>
</head>
<body><p>This game is now called <a href="../{qz['dir']}/">{E(name)}</a>.</p></body>
</html>
""")

# ------------------------------------------------------------------ hub
# the Minecraft tile shows the real sheep, rendered from Mojang's own model and texture (bedrock-samples)

SECTIONS = [("quizzes", "Quizzes", "Pick a topic and answer 20 questions."),
            ("games", "Other games", "Something a bit different, with the same party codes, timer and top scores.")]
hub_desc = "Obscure Trivia: free quizzes for the details only real players know. 20 random questions per game on general knowledge, Hearthstone Battlegrounds, Minecraft: Bedrock Edition, OG Fortnite (Chapter 1), Clash Royale, Dead by Daylight, animals, football, cars and music, plus the This or That, Odd One Out and Timeline games. Play solo or in party mode with up to 6 players."
hub_ld = {"@context": "https://schema.org", "@type": "WebSite", "name": "Obscure Trivia", "alternateName": ["Tavern Trivia", "Obscure Trivia quizzes"], "url": SITE}
hub_fav = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect x='4' y='4' width='56' height='56' rx='14' fill='%23f2efe6'/%3E%3Ctext x='32' y='46' font-size='40' font-weight='800' text-anchor='middle' font-family='Arial,sans-serif' fill='%2315141a'%3E%3F%3C/text%3E%3C/svg%3E"
hub_css = """
/* Layout: a single column; brand bar, a short headline, the quiz shelf (one textured tile per quiz), and a join-by-code box. */
:root {
  --bg: #121117; --panel: #1c1b23; --line: #2e2c39; --ink: #f2efe6; --muted: #a7a3b5; --faint: #7a7689;
  --hs-ink: #f6e7cf; --hs-gold: #e8b450; --mc-ink: #ffffff; --mc-green: #7ad155; --focus: #f2efe6;
  --f-display: "Bricolage Grotesque", "Arial Black", system-ui, sans-serif; --f-body: "Inter", system-ui, -apple-system, "Segoe UI", sans-serif;
  color-scheme: dark;
  padding-top: env(safe-area-inset-top, 0px); padding-bottom: env(safe-area-inset-bottom, 0px);
}
* { box-sizing: border-box; }
body { margin: 0; background: radial-gradient(ellipse at 20% -10%, #2a2636 0%, transparent 55%), var(--bg); color: var(--ink); font-family: var(--f-body); font-size: 16px; line-height: 1.5;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); padding-block: 22px 48px; }
.wrap { max-width: 1000px; margin: 0 auto; display: flex; flex-direction: column; gap: 28px; }
a { color: inherit; }
:focus-visible { outline: 2px solid var(--focus); outline-offset: 3px; }
.top { display: flex; align-items: center; gap: 12px; }
/* coins: the same purse the quiz pages show */
.wallet-wrap { position: relative; margin-left: auto; }
.wallet { display: inline-flex; align-items: center; gap: 6px; padding: 5px 13px 5px 6px; border-radius: 999px; border: 1px solid var(--line); background: var(--panel);
  color: var(--ink); font: inherit; font-weight: 800; font-size: 0.98rem; line-height: 1.2; font-variant-numeric: tabular-nums; cursor: pointer; }
.wallet:hover, .wallet[aria-expanded="true"] { border-color: #f7c02b; }
.coin-ico { width: 22px; height: 22px; flex: none; display: block; }
.wallet-pop { position: absolute; z-index: 30; right: 0; top: calc(100% + 8px); width: min(260px, calc(100vw - 32px)); padding: 10px 12px; border-radius: 12px;
  border: 1px solid var(--line); background: var(--panel); color: var(--muted); box-shadow: 0 14px 32px rgba(0,0,0,0.5); display: flex; flex-direction: column; gap: 4px;
  font-size: 0.88rem; line-height: 1.4; }
.wallet-pop[hidden] { display: none; }
.wallet-pop b { color: var(--ink); font-size: 0.95rem; }
.wallet-pop a { color: #f7c02b; font-weight: 700; }
.acct-link { display: inline-flex; align-items: center; gap: 6px; padding: 6px 13px 6px 10px; border-radius: 999px; border: 1px solid var(--line); color: var(--ink);
  text-decoration: none; font-weight: 700; font-size: 0.92rem; white-space: nowrap; }
.acct-link span { max-width: 12ch; overflow: hidden; text-overflow: ellipsis; }
.acct-link[hidden] { display: none; }
.acct-link.in svg { color: #7ad155; }
.acct-link:hover { border-color: var(--muted); }
.top .brand { white-space: nowrap; }
@media (max-width: 460px) { .acct-link { padding: 0; width: 36px; height: 36px; justify-content: center; } .acct-link span { display: none; } }
.mark { width: 34px; height: 34px; border-radius: 9px; background: var(--ink); color: var(--bg); display: grid; place-items: center; font-family: var(--f-display); font-weight: 800; font-size: 1.3rem; transform: rotate(-6deg); }
.brand { font-family: var(--f-display); font-weight: 800; font-size: 1.35rem; letter-spacing: -0.01em; margin: 0; }
.hero { display: flex; flex-direction: column; gap: 12px; }
.hero h2 { font-family: var(--f-display); font-weight: 800; font-size: clamp(2.1rem, 7vw, 3.4rem); line-height: 1.02; letter-spacing: -0.025em; margin: 0; text-wrap: balance; max-width: 16ch; }
.hero p { margin: 0; color: var(--muted); max-width: 56ch; font-size: 1.05rem; }
.eyebrow { font-size: 0.74rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: var(--muted); }
.shelf { display: grid; grid-template-columns: repeat(2, 1fr); gap: 18px; }
.shelf .quiz:last-child:nth-child(odd) { grid-column: 1 / -1; }
@media (max-width: 900px) { .shelf { grid-template-columns: 1fr 1fr; } }
@media (max-width: 620px) { .shelf { grid-template-columns: 1fr; } }
/* globe tile: a lit Earth in space, clean sans titles */
.gk { border-radius: 22px; color: #f2f7ff;
  background: linear-gradient(180deg, rgba(5,10,24,0) 25%, rgba(5,10,24,0.82) 80%), url(general-knowledge/earth-tile.jpg) 62% 40% / cover;
  box-shadow: 0 12px 30px rgba(0,0,0,0.45), inset 0 0 0 1px rgba(150,190,255,0.3); }
.gk:hover { box-shadow: 0 16px 36px rgba(0,0,0,0.55), 0 0 0 2px #7dd3fc, inset 0 0 0 1px rgba(150,190,255,0.3); }
.gk h3 { font-family: "Outfit", system-ui, sans-serif; font-weight: 800; font-size: clamp(1.7rem, 4.4vw, 2.2rem); letter-spacing: -0.015em; }
.gk p { color: #cfe0f5; font-family: "Atkinson Hyperlegible", system-ui, sans-serif; }
.gk .pill { border-radius: 999px; background: rgba(125,211,252,0.16); border: 1px solid rgba(125,211,252,0.45); color: #c4ecff; }
.gk .play { color: #8edbff; }
/* pitch tile: mowing stripes, a chalk centre circle and condensed sports type */
.fb { border-radius: 14px; color: #fff;
  background: linear-gradient(180deg, rgba(0,0,0,0) 25%, rgba(4,18,9,0.85) 82%),
    radial-gradient(circle at 70% 38%, transparent 0 46px, rgba(255,255,255,0.55) 47px 49px, transparent 50px),
    linear-gradient(90deg, transparent calc(70% - 1px), rgba(255,255,255,0.55) calc(70% - 1px) calc(70% + 1px), transparent calc(70% + 1px)),
    repeating-linear-gradient(90deg, #1d6a35 0 34px, #22783c 34px 68px);
  box-shadow: 0 12px 30px rgba(0,0,0,0.45), inset 0 0 0 3px rgba(255,255,255,0.55); }
.fb:hover { box-shadow: 0 16px 36px rgba(0,0,0,0.55), inset 0 0 0 3px #ffd84a; }
.fb h3 { font-family: "Oswald", "Arial Narrow", sans-serif; font-weight: 700; font-size: clamp(1.9rem, 5vw, 2.5rem); text-transform: uppercase; letter-spacing: 0.02em; }
.fb p { color: #dcebdf; font-family: "Barlow", system-ui, sans-serif; }
.fb .pill { border-radius: 999px; background: rgba(0,0,0,0.35); border: 1px solid rgba(255,255,255,0.45); color: #fff; }
.fb .play { color: #ffd84a; }
.quiz { position: relative; display: flex; flex-direction: column; justify-content: flex-end; gap: 10px; min-height: 260px; padding: 22px; text-decoration: none; overflow: hidden; min-width: 0;
  transition: transform .15s ease, box-shadow .15s ease; }
.quiz:hover { transform: translateY(-3px); }
.quiz h3 { margin: 0; line-height: 1.05; text-wrap: balance; }
.quiz p { margin: 0; font-size: 0.95rem; max-width: 36ch; }
.quiz .meta { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
.quiz .pill { font-size: 0.78rem; font-weight: 700; padding: 4px 10px; }
.quiz .play { margin-left: auto; font-weight: 800; }
@font-face { font-family: "Monocraft"; src: url("minecraft/Monocraft.woff2") format("woff2"); font-display: swap; }
/* tavern tile: oak planks, a gold coin and a serif title */
.hs { border-radius: 16px; color: var(--hs-ink);
  background: url(hearthstone/emblem.svg) right 26px top 16px / auto 54% no-repeat,
    radial-gradient(circle at 84% 30%, rgba(255, 170, 70, 0.55) 0, rgba(255, 150, 50, 0.18) 22%, transparent 46%),
    radial-gradient(ellipse at 10% 110%, rgba(255, 120, 40, 0.22), transparent 55%),
    repeating-linear-gradient(180deg, transparent 0 51px, rgba(0, 0, 0, 0.22) 51px 53px, rgba(255, 210, 150, 0.04) 53px 54px),
    linear-gradient(180deg, #4b2e19 0%, #301d10 55%, #1b100a 100%);
  box-shadow: 0 12px 30px rgba(0,0,0,0.45), inset 0 0 0 1px rgba(232,180,80,0.5), inset 0 0 0 5px rgba(20, 12, 7, 0.35); }
.hs:hover { box-shadow: 0 16px 36px rgba(0,0,0,0.55), inset 0 0 0 2px var(--hs-gold); }
.hs h3 { font-family: "Bree Serif", Georgia, serif; font-weight: 400; font-size: clamp(1.7rem, 4.6vw, 2.2rem); max-width: 62%; }
.hs p { color: #e3cfb2; }
.hs .pill { border-radius: 999px; background: rgba(232,180,80,0.16); border: 1px solid rgba(232,180,80,0.45); color: #f6d58f; }
.hs .play { color: var(--hs-gold); }
.hs .coin { position: absolute; top: 22px; right: 26px; width: 64px; height: 64px; border-radius: 50%; display: grid; place-items: center;
  background: radial-gradient(circle at 35% 30%, #fff6d2 0 12%, #f0be5c 40%, #a8721f 100%); color: #2a1b08; font-family: "Bree Serif", Georgia, serif; font-size: 1.9rem;
  box-shadow: inset 0 -3px 0 rgba(0,0,0,0.25), inset 0 0 0 3px rgba(255, 240, 200, 0.35), 0 0 0 5px rgba(232, 180, 80, 0.16), 0 0 34px rgba(255, 180, 80, 0.55); }
/* block tile: pixel grass-and-dirt, square corners, a pixel title */
.mc { border-radius: 0; color: var(--mc-ink);
  background: linear-gradient(180deg, rgba(0,0,0,0) 52%, rgba(14,34,8,0.6) 100%),
    url(minecraft/sheep.png) right 30px top 18px / auto 50% no-repeat,
    repeating-conic-gradient(rgba(255,255,255,0.05) 0 25%, rgba(0,0,0,0) 0 50%) 0 0 / 26px 26px,
    linear-gradient(180deg, #70b540 0%, #5b9d32 60%, #4a8627 100%);
  box-shadow: inset 0 0 0 3px #0f0f10, inset 0 0 0 5px rgba(255,255,255,0.18), 0 10px 0 rgba(0,0,0,0.35); }
@media (max-width: 620px) { .hs { min-height: 340px; background-size: auto 40%, auto, auto, auto, auto; } }
@media (max-width: 620px) { .mc { min-height: 340px; background-size: auto, auto 40%, 26px 26px, auto; } }
.mc:hover { box-shadow: inset 0 0 0 3px #0f0f10, inset 0 0 0 5px var(--mc-green), 0 12px 0 rgba(0,0,0,0.35); }
.mc h3 { font-family: "Monocraft", ui-monospace, monospace; font-weight: 400; font-size: clamp(1.8rem, 5vw, 2.4rem); text-shadow: 3px 3px 0 #1f1f1f; }
.mc p { color: #e6e6e6; text-shadow: 1px 1px 0 #000; }
.mc .pill { background: #313233; border: 2px solid #0f0f10; color: #fff; box-shadow: inset 0 -3px 0 rgba(0,0,0,0.3); }
.mc .play { color: var(--mc-green); text-shadow: 2px 2px 0 #000; font-family: "Monocraft", ui-monospace, monospace; font-size: 1.1rem; }
/* car tile: carbon fibre, a red and white racing stripe and slanted motorsport type */
.cr { border-radius: 12px; color: #fff;
  background: linear-gradient(180deg, rgba(10, 10, 12, 0) 22%, rgba(10, 10, 12, 0.92) 80%),
    radial-gradient(ellipse at 25% 0%, rgba(225, 6, 0, 0.35), transparent 60%),
    linear-gradient(100deg, transparent 0 64%, #e10600 64% 71%, transparent 71% 73.5%, #f3f4f6 73.5% 76%, transparent 76%),
    linear-gradient(45deg, #111215 25%, transparent 25%, transparent 75%, #111215 75%) 0 0 / 12px 12px,
    linear-gradient(45deg, #111215 25%, transparent 25%, transparent 75%, #111215 75%) 6px 6px / 12px 12px,
    linear-gradient(#202227, #18191d);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.45), inset 0 0 0 1px rgba(255, 255, 255, 0.14); }
.cr:hover { box-shadow: 0 16px 36px rgba(0, 0, 0, 0.55), inset 0 0 0 2px #e10600; }
.cr h3 { font-family: "Chakra Petch", "Arial Narrow", sans-serif; font-weight: 700; font-style: italic; font-size: clamp(2rem, 5.4vw, 2.6rem); text-transform: uppercase; letter-spacing: 0.02em; }
.cr p { color: #d4d7dd; font-family: "Titillium Web", system-ui, sans-serif; }
.cr .pill { border-radius: 999px; background: rgba(0, 0, 0, 0.45); border: 1px solid rgba(255, 90, 77, 0.6); color: #fff; }
.cr .play { color: #ff5a4d; }
/* music tile: a dark stage, two spotlights and a vinyl record */
.mu { border-radius: 18px; color: #fff;
  background: url(music/vinyl.svg) right 26px top 18px / auto 54% no-repeat,
    radial-gradient(ellipse 70% 80% at 0% -10%, rgba(255, 79, 163, 0.5), transparent 60%),
    radial-gradient(ellipse 60% 80% at 100% 0%, rgba(77, 227, 255, 0.35), transparent 55%),
    linear-gradient(180deg, #2a1650 0%, #160d2c 60%, #0e0a1c 100%);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.45), inset 0 0 0 1px rgba(255, 122, 192, 0.35); }
.mu:hover { box-shadow: 0 16px 36px rgba(0, 0, 0, 0.55), 0 0 0 2px #ff4fa3, inset 0 0 0 1px rgba(255, 122, 192, 0.35); }
.mu h3 { font-family: "Unbounded", "Arial Black", sans-serif; font-weight: 700; font-size: clamp(1.8rem, 5vw, 2.3rem); letter-spacing: -0.01em; }
.mu p { color: #ddd2f5; font-family: "DM Sans", system-ui, sans-serif; }
.mu .pill { border-radius: 999px; background: rgba(255, 79, 163, 0.14); border: 1px solid rgba(255, 122, 192, 0.55); color: #ffd2e9; }
.mu .play { color: #ff8ac6; }
@media (max-width: 620px) { .mu { min-height: 340px; background-size: auto 40%, auto, auto, auto; } }
/* clash royale tile: royal blue with a gold border, a crown and a drop of Elixir */
.roy { border-radius: 18px; color: #fff;
  background: url(clash-royale/crown.svg) right 22px top 18px / auto 40% no-repeat,
    radial-gradient(circle at 86% 14%, rgba(255, 201, 40, 0.4), transparent 34%), radial-gradient(circle at 0% 100%, rgba(230, 74, 216, 0.28), transparent 40%),
    linear-gradient(180deg, #2a5fd6 0%, #163d99 55%, #0e2a74 100%);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.45), inset 0 0 0 3px rgba(255, 201, 40, 0.75), inset 0 0 0 6px rgba(10, 28, 82, 0.6); }
.roy:hover { box-shadow: 0 16px 36px rgba(0, 0, 0, 0.55), inset 0 0 0 4px #ffc928, inset 0 0 0 7px rgba(10, 28, 82, 0.6); }
.roy h3 { font-family: "Titan One", "Baloo 2", sans-serif; font-weight: 400; font-size: clamp(1.9rem, 5vw, 2.4rem); letter-spacing: 0.01em;
  text-shadow: 0 3px 0 rgba(6, 16, 60, 0.7); }
.roy p { color: #dce5ff; font-family: "Baloo 2", system-ui, sans-serif; font-weight: 600; max-width: 31ch; }
.roy .pill { border-radius: 999px; background: rgba(6, 16, 60, 0.4); border: 1px solid rgba(255, 201, 40, 0.6); color: #fff; }
.roy .play { color: #ffc928; font-family: "Titan One", sans-serif; font-weight: 400; }
@media (max-width: 620px) { .roy { min-height: 330px; background-size: auto 34%, auto, auto, auto; } }
/* dead by daylight tile: night, the Fog rolling in, the Entity's red glow and a meat hook */
.dbd { border-radius: 12px; color: #ece6dd;
  background: url(dead-by-daylight/hook.svg) right 18px top 12px / auto 52% no-repeat,
    radial-gradient(ellipse 60% 40% at 18% 108%, rgba(200, 205, 212, 0.26), transparent 70%),
    radial-gradient(ellipse 55% 36% at 78% 106%, rgba(200, 205, 212, 0.2), transparent 70%),
    radial-gradient(circle at 84% 22%, rgba(200, 22, 30, 0.5), transparent 42%),
    linear-gradient(180deg, #24151a 0%, #140e11 55%, #0c0a0b 100%);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.5), inset 0 0 0 1px rgba(222, 36, 44, 0.55), inset 0 0 40px rgba(0, 0, 0, 0.6); }
.dbd:hover { box-shadow: 0 16px 36px rgba(0, 0, 0, 0.6), inset 0 0 0 2px #de242c, inset 0 0 40px rgba(0, 0, 0, 0.6); }
.dbd h3 { font-family: "Eater", Georgia, serif; font-weight: 400; font-size: clamp(1.9rem, 5vw, 2.4rem); letter-spacing: 0.03em; max-width: 9ch; line-height: 1.12;
  text-shadow: 0 0 18px rgba(200, 22, 30, 0.6), 0 3px 0 rgba(0, 0, 0, 0.7); }
.dbd p { color: #cfc5bb; font-family: "Spectral", Georgia, serif; font-weight: 600; max-width: 31ch; }
.dbd .pill { border-radius: 999px; background: rgba(0, 0, 0, 0.4); border: 1px solid rgba(222, 36, 44, 0.6); color: #ece6dd; }
.dbd .play { color: #ff6166; font-family: "Spectral", Georgia, serif; font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase; }
@media (max-width: 620px) { .dbd { min-height: 330px; background-size: auto 38%, auto, auto, auto, auto; } }
/* animals tile: jungle green, sunlight through the leaves and an orange paw print */
.an { border-radius: 20px; color: #f4f1e6;
  background: url(animals/paw.svg) right 26px top 18px / auto 44% no-repeat,
    radial-gradient(ellipse 60% 70% at 0% 0%, rgba(140, 210, 100, 0.35), transparent 60%), radial-gradient(circle at 85% 20%, rgba(255, 190, 70, 0.32), transparent 45%),
    linear-gradient(180deg, #1d5139 0%, #143a29 55%, #0e2a1e 100%);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.45), inset 0 0 0 1px rgba(255, 178, 56, 0.4); }
.an:hover { box-shadow: 0 16px 36px rgba(0, 0, 0, 0.55), inset 0 0 0 2px #ffb238; }
.an h3 { font-family: "Fredoka", sans-serif; font-weight: 700; font-size: clamp(2rem, 5.4vw, 2.6rem); }
.an p { color: #d5e3d0; font-family: "Lexend", system-ui, sans-serif; max-width: 32ch; }
.an .pill { border-radius: 999px; background: rgba(0, 0, 0, 0.25); border: 1px solid rgba(255, 178, 56, 0.55); color: #fff3dc; }
.an .play { color: #ffc861; font-family: "Fredoka", sans-serif; font-weight: 700; }
@media (max-width: 620px) { .an { min-height: 320px; background-size: auto 34%, auto, auto, auto; } }
/* odd one out tile: deep indigo, three teal circles and one coral triangle */
.odd { border-radius: 18px; color: #f3f1ff;
  background: radial-gradient(ellipse 60% 60% at 100% 0%, rgba(255, 107, 91, 0.3), transparent 60%), radial-gradient(ellipse 60% 60% at 0% 100%, rgba(55, 214, 195, 0.25), transparent 60%),
    linear-gradient(180deg, #24204a 0%, #1a1738 60%, #131129 100%);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.45), inset 0 0 0 1px rgba(55, 214, 195, 0.4); }
.odd:hover { box-shadow: 0 16px 36px rgba(0, 0, 0, 0.55), inset 0 0 0 2px #37d6c3; }
.odd h3 { font-family: "Bungee", sans-serif; font-weight: 400; font-size: clamp(1.7rem, 4.6vw, 2.2rem); }
.odd p { color: #d6d2f5; font-family: "Plus Jakarta Sans", system-ui, sans-serif; max-width: 30ch; }
.odd .pill { border-radius: 999px; background: rgba(0, 0, 0, 0.25); border: 1px solid rgba(55, 214, 195, 0.5); color: #e6fffb; }
.odd .play { color: #ff8c7f; font-family: "Bungee", sans-serif; font-weight: 400; }
.odd-grid { position: absolute; top: 22px; right: 26px; display: grid; grid-template-columns: 44px 44px; gap: 10px; }
.odd-grid i { width: 44px; height: 44px; border-radius: 50%; background: #37d6c3; box-shadow: 0 0 18px rgba(55, 214, 195, 0.35); }
.odd-grid b { width: 0; height: 0; margin: 2px auto 0; border-left: 25px solid transparent; border-right: 25px solid transparent; border-bottom: 42px solid #ff6b5b;
  filter: drop-shadow(0 0 12px rgba(255, 107, 91, 0.45)); }
@media (prefers-reduced-motion: no-preference) { .odd:hover .odd-grid b { animation: odd-wiggle .5s ease-in-out 2; } }
@keyframes odd-wiggle { 0%, 100% { transform: rotate(0); } 25% { transform: rotate(-12deg); } 75% { transform: rotate(12deg); } }
@media (max-width: 620px) { .odd { min-height: 300px; } .odd-grid { grid-template-columns: 36px 36px; gap: 8px; } .odd-grid i { width: 36px; height: 36px; }
  .odd-grid b { border-left-width: 20px; border-right-width: 20px; border-bottom-width: 34px; } }
/* timeline tile: museum parchment, a rust-red timeline with four pins */
.tl { border-radius: 12px; color: #2e2414;
  background: repeating-linear-gradient(0deg, rgba(122, 74, 36, 0.05) 0 1px, transparent 1px 26px), linear-gradient(180deg, #f8f0dc, #efe1c2);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.4), inset 0 0 0 1px #d9c7a2, inset 0 0 0 6px rgba(255, 255, 255, 0.4); }
.tl:hover { box-shadow: 0 16px 36px rgba(0, 0, 0, 0.5), inset 0 0 0 2px #b5452b; }
.tl h3 { font-family: "Abril Fatface", Georgia, serif; font-weight: 400; font-size: clamp(2rem, 5.4vw, 2.6rem); }
.tl p { color: #5d4a2f; font-family: "Libre Franklin", system-ui, sans-serif; font-weight: 500; max-width: 30ch; }
.tl .pill { border-radius: 999px; background: #fffaf0; border: 1px solid #c9b48a; color: #2e2414; }
.tl .play { color: #9c3820; font-family: "Libre Franklin", sans-serif; font-weight: 800; letter-spacing: 0.04em; text-transform: uppercase; }
.tl-line { position: absolute; top: 34px; right: 26px; width: 170px; height: 4px; border-radius: 2px; background: linear-gradient(90deg, #b5452b, #e2a33a); display: flex;
  justify-content: space-between; align-items: center; }
.tl-line i { width: 16px; height: 16px; border-radius: 50%; background: #fffaf0; border: 3px solid #b5452b; }
.tl-line i:nth-child(2), .tl-line i:nth-child(4) { transform: translateY(-14px); }
@media (max-width: 620px) { .tl { min-height: 300px; } .tl-line { width: 130px; } }
/* fortnite tile: blue sky, the purple storm at the edges and Peely */
.fn { border-radius: 16px; color: #fff;
  background: url(fortnite/peely.png) right 34px top 14px / auto 62% no-repeat,
    radial-gradient(circle at 70% 38%, transparent 40%, rgba(136, 52, 240, 0.4) 62%, rgba(80, 20, 180, 0.9) 100%),
    linear-gradient(180deg, rgba(10, 20, 80, 0) 35%, rgba(10, 20, 80, 0.7) 100%),
    linear-gradient(180deg, #4b95ff 0%, #2a6cf0 55%, #3b2bb8 100%);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.45), inset 0 0 0 2px rgba(255, 226, 58, 0.55); }
.fn:hover { box-shadow: 0 16px 36px rgba(0, 0, 0, 0.55), inset 0 0 0 3px #ffe23a; }
.fn h3 { font-family: "Anton", "Impact", sans-serif; font-weight: 400; font-size: clamp(2.1rem, 5.6vw, 2.7rem); text-transform: uppercase; letter-spacing: 0.02em;
  text-shadow: 0 3px 0 rgba(10, 16, 70, 0.65); }
.fn p { color: #e6ecff; font-family: "Nunito", system-ui, sans-serif; font-weight: 600; max-width: 30ch; }
.fn .pill { border-radius: 999px; background: rgba(10, 20, 80, 0.45); border: 1px solid rgba(255, 226, 58, 0.6); color: #fff; }
.fn .play { color: #ffe23a; font-family: "Anton", sans-serif; font-weight: 400; text-transform: uppercase; font-size: 1.1rem; letter-spacing: 0.03em; }
@media (max-width: 620px) { .fn { min-height: 360px; background-size: auto 46%, auto, auto, auto; } }
/* two sections: the quizzes, then other games */
.sect { display: flex; flex-direction: column; gap: 14px; }
.sect-head { display: flex; align-items: baseline; justify-content: space-between; gap: 4px 16px; flex-wrap: wrap; padding-bottom: 10px; border-bottom: 1px solid var(--line); }
.sect-head h2 { margin: 0; font-family: var(--f-display); font-weight: 800; font-size: 1.55rem; letter-spacing: -0.015em; }
.sect-head p { margin: 0; color: var(--muted); font-size: 0.95rem; }
/* versus tile: a warm side, a cool side, a VS badge and chunky rounded type */
.wb { border-radius: 18px; color: #1b1b2f; border: 3px solid #1b1b2f;
  background: linear-gradient(180deg, rgba(255,246,226,0) 28%, rgba(255,246,226,0.97) 64%),
    radial-gradient(circle, rgba(27,27,47,0.14) 1.2px, transparent 1.7px) 0 0 / 16px 16px,
    linear-gradient(115deg, #ff8a78 0 50%, #6d9bff 50% 100%);
  box-shadow: 6px 6px 0 #000; }
.wb:hover { box-shadow: 9px 9px 0 #000; }
.wb h3 { font-family: "Lilita One", "Arial Rounded MT Bold", sans-serif; font-weight: 400; font-size: clamp(1.9rem, 5vw, 2.4rem); }
.wb p { color: #44415a; font-family: "Rubik", system-ui, sans-serif; }
.wb .pill { border-radius: 999px; background: #fff; border: 2px solid #1b1b2f; color: #1b1b2f; }
.wb .play { color: #c2410c; }
.wb .vs-badge { position: absolute; top: 26px; left: 50%; width: 64px; height: 64px; margin-left: -32px; border-radius: 50%; display: grid; place-items: center;
  background: #1b1b2f; color: #ffcd29; font-family: "Lilita One", sans-serif; font-size: 1.45rem; transform: rotate(-8deg); box-shadow: 4px 4px 0 #c2410c; }
:focus-visible.wb { outline-offset: 5px; }
.joinbox { background: var(--panel); border: 1px solid var(--line); border-radius: 14px; padding: 20px; display: flex; flex-direction: column; gap: 12px; }
.joinbox h3 { margin: 0; font-family: var(--f-display); font-weight: 800; font-size: 1.25rem; }
.joinbox p { margin: 0; color: var(--muted); font-size: 0.95rem; }
.row { display: flex; gap: 10px; flex-wrap: wrap; }
.input { flex: 1 1 160px; min-width: 0; background: var(--bg); border: 1px solid var(--line); border-radius: 10px; padding: 11px 12px; color: var(--ink); font: inherit;
  text-transform: uppercase; letter-spacing: 0.3em; text-align: center; font-weight: 700; }
.input::placeholder { color: var(--faint); }
.btn { border-radius: 10px; border: 0; padding: 12px 20px; font: inherit; font-weight: 800; background: var(--ink); color: var(--bg); cursor: pointer; }
.err { color: #f08a7c; font-size: 0.9rem; min-height: 1.3em; margin: 0; }
.foot { color: var(--faint); font-size: 0.82rem; text-align: center; margin: 0; }
.locked-link { display: inline-flex; align-items: center; gap: 6px; color: var(--muted); text-decoration: none; padding: 6px 12px; border-radius: 999px; border: 1px solid var(--line); }
.foot .locked-link + .locked-link { margin-left: 6px; }
.locked-link:hover { color: var(--ink); border-color: var(--muted); }
@media (prefers-reduced-motion: reduce) { * { transition: none !important; } }
""".replace("__WOOD__", TEX["wood"]).replace("__GRASS__", TEX["grass_side"])
hub = head("Obscure Trivia – General Knowledge, Hearthstone, Minecraft, Fortnite, Clash Royale, Dead by Daylight, Animals, Football, Car & Music Quizzes", hub_desc, SITE,
           "family=Bricolage+Grotesque:opsz,wght@12..96,700;12..96,800&family=Inter:wght@400;500;700&family=Bree+Serif&family=Outfit:wght@800&family=Atkinson+Hyperlegible&family=Oswald:wght@700&family=Barlow&family=Lilita+One&family=Rubik:wght@400;500&family=Chakra+Petch:ital,wght@1,700&family=Titillium+Web:wght@400;600&family=Unbounded:wght@700&family=DM+Sans:wght@400;500&family=Anton&family=Nunito:wght@600;800&family=Titan+One&family=Baloo+2:wght@600&family=Eater&family=Spectral:wght@600;700&family=Fredoka:wght@700&family=Lexend:wght@400&family=Bungee&family=Plus+Jakarta+Sans:wght@400;500&family=Abril+Fatface&family=Libre+Franklin:wght@500;800",
           "#121117", hub_fav, extra_head=f"<style>{hub_css}</style>", ld=hub_ld)
hub += """<div class="wrap">
  <header class="top"><span class="mark" aria-hidden="true">?</span><h1 class="brand">Obscure Trivia</h1>
    <div class="wallet-wrap" id="wallet-wrap"><button class="wallet" id="wallet" aria-expanded="false" aria-controls="wallet-pop" aria-label="Your coins. What are coins?"><svg class="coin-ico" viewBox="0 0 20 20" aria-hidden="true"><circle cx="10" cy="10" r="9" fill="#f7c02b" stroke="#a96a00" stroke-width="1.6"/><circle cx="10" cy="10" r="5.7" fill="none" stroke="#fff1ad" stroke-width="1.5"/><path d="M6 6.6a5.4 5.4 0 0 1 3.2-2.1" stroke="#fff" stroke-width="1.4" stroke-linecap="round" fill="none" opacity=".85"/></svg><span class="wallet-n" id="wallet-n">0</span></button>
      <div class="wallet-pop" id="wallet-pop" role="note" hidden><b id="wallet-t">0 coins</b><span>You get 1 coin for every right answer, in every quiz and game here.</span><span id="wallet-acct"></span><a href="spend-coins/">Spend them on Blackjack</a></div></div>
    <a class="acct-link" id="acct-link" href="account/" hidden><svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path fill="currentColor" d="M12 12a5 5 0 1 0 0-10 5 5 0 0 0 0 10zm0 2c-4.4 0-8 2.2-8 5v3h16v-3c0-2.8-3.6-5-8-5z"/></svg><span id="acct-name">Sign in</span></a></header>
  <section class="hero">
    <span class="eyebrow">Free trivia quizzes</span>
    <h2>Trivia for the details only real players know.</h2>
    <p>Each quiz pulls 20 random questions from a bank of 1,000. Play on your own, or start a party of up to 6 players with a 5-letter code and see who wins.</p>
  </section>
""" + "".join(f"""  <section class="sect" aria-labelledby="h-{sid}">
    <div class="sect-head"><h2 id="h-{sid}">{E(stitle)}</h2><p>{E(sblurb)}</p></div>
    <div class="shelf {sid}">
""" + "".join(f"""      <a class="quiz {q['tile']['cls']}" href="{q['dir']}/">
        {q['tile']['art']}
        <h3>{E(q['tile']['title'])}</h3>
        <p>{E(q['tile']['blurb'])}</p>
        <div class="meta"><span class="pill">{QUESTIONS_PER_GAME} questions</span><span class="pill">Solo &amp; party</span><span class="play">Play →</span></div>
      </a>
""" for q in QUIZZES if q.get("section", "quizzes") == sid) + """    </div>
  </section>
""" for sid, stitle, sblurb in SECTIONS) + """
  <section class="joinbox">
    <h3>Got a code from a friend?</h3>
    <p>Type it in and you'll go straight to the right quiz.</p>
    <form class="row" id="join" autocomplete="off">
      <input class="input" id="code" maxlength="5" placeholder="CODE" aria-label="Game code">
      <button class="btn" type="submit">Join game</button>
    </form>
    <p class="err" id="err" role="alert"></p>
  </section>
  <p class="foot"><a class="locked-link" href="spend-coins/"><svg viewBox="0 0 24 24" width="14" height="14" aria-hidden="true"><circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="12" r="4.5" fill="none" stroke="currentColor" stroke-width="1.6"/></svg>Spend coins</a> <a class="locked-link" href="locked/"><svg viewBox="0 0 24 24" width="14" height="14" aria-hidden="true"><path fill="currentColor" d="M12 2a5 5 0 0 0-5 5v3H6a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8a2 2 0 0 0-2-2h-1V7a5 5 0 0 0-5-5zm-3 8V7a3 3 0 1 1 6 0v3H9z"/></svg>Locked area</a></p>
  <p class="foot">More quizzes on the way. Fan-made, not affiliated with Blizzard, Mojang, Microsoft, Epic Games, Supercell, the Premier League, FIFA, UEFA, any car maker or any record label.</p>
</div>
<script src="assets/account.js?v=""" + V_ACC + """"></script>
<script>
(() => {
  // coins: the same count the quiz pages keep, 1 for every right answer
  const wn = document.getElementById("wallet-n"), wt = document.getElementById("wallet-t"), wb = document.getElementById("wallet"), wp = document.getElementById("wallet-pop");
  const C = window.OTCoins, wa = document.getElementById("wallet-acct"), al = document.getElementById("acct-link");
  const esc = s => String(s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const showCoins = () => { const n = C.get(), u = C.user();
    wn.textContent = n.toLocaleString(); wt.textContent = n.toLocaleString() + (n === 1 ? " coin" : " coins"); wb.setAttribute("aria-label", wt.textContent + ". What are coins?");
    wa.innerHTML = u ? `Saved in your account, <b>${esc(u)}</b>. <a href="account/">Account</a>` : C.enabled ? `Saved in this browser only. <a href="account/">Make an account</a> to keep them safe.` : "Your coins are saved in this browser.";
    al.hidden = !C.enabled; document.getElementById("acct-name").textContent = u || "Sign in"; al.setAttribute("aria-label", u ? "Your account, " + u : "Sign in"); al.classList.toggle("in", !!u); };
  showCoins();
  C.on(showCoins);
  window.addEventListener("pageshow", showCoins);
  wb.addEventListener("click", e => { e.stopPropagation(); wp.hidden = !wp.hidden; wb.setAttribute("aria-expanded", String(!wp.hidden)); });
  document.addEventListener("click", e => { if (!wp.hidden && !e.target.closest("#wallet-wrap")) { wp.hidden = true; wb.setAttribute("aria-expanded", "false"); } });
  const routes = """ + json.dumps(dict({l: q["dir"] + "/" for q in QUIZZES for l in [q["config"]["letter"]] + q.get("aliases", [])}, K="spend-coins/")) + """;
  const ALPH = "ABCDEFGHJKMNPQRSTUVWXYZ23456789";
  document.getElementById("join").addEventListener("submit", e => {
    e.preventDefault();
    const c = String(document.getElementById("code").value || "").toUpperCase().replace(/[^A-Z0-9]/g, "").replace(/O/g, "0").replace(/[IL]/g, "1");
    const err = document.getElementById("err");
    if (c.length !== 5 || ![...c].every(ch => ALPH.includes(ch))) { err.textContent = "Codes are 5 letters or numbers, like M7QX2."; return; }
    const r = routes[c[0]];
    if (!r) { err.textContent = """ + json.dumps("That code doesn't match a game. Codes start with " + ", ".join(q["config"]["letter"] + " (" + q["tile"]["title"].rstrip("?") + ")" for q in QUIZZES) + " or K (Crate Battles).") + """; return; }
    location.href = r + "?join=" + c;
  });
})();
</script>
</body>
</html>
"""
open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(hub)

nf = head("Page not found – Obscure Trivia", "This page doesn't exist. Pick a quiz from Obscure Trivia instead.", SITE, "family=Bricolage+Grotesque:opsz,wght@12..96,800&family=Inter:wght@400;700",
          "#121117", hub_fav, extra_head=f"""<meta name="robots" content="noindex"><style>{hub_css}
.nf {{ min-height: 70vh; display: flex; flex-direction: column; justify-content: center; gap: 16px; }}
.nf ul {{ list-style: none; margin: 0; padding: 0; display: flex; flex-wrap: wrap; gap: 10px; }}
.nf a.btn {{ text-decoration: none; display: inline-block; }}</style>""")
nf += """<div class="wrap nf">
  <header class="top"><span class="mark" aria-hidden="true">?</span><span class="brand">Obscure Trivia</span></header>
  <section class="hero"><span class="eyebrow">Error 404</span><h2>That page doesn't exist.</h2>
    <p>The link might be mistyped or out of date. Pick a quiz instead:</p></section>
  <ul>""" + "".join(f'<li><a class="btn" href="{SITE}{q["dir"]}/">{E(q["tile"]["title"])}</a></li>' for q in QUIZZES) + f"""</ul>
  <p><a href="{SITE}">Go to the home page</a></p>
</div>
</body>
</html>
"""
open(os.path.join(OUT, "404.html"), "w", encoding="utf-8").write(nf)

COIN_SVG = '<svg class="coin-ico" viewBox="0 0 20 20" aria-hidden="true"><circle cx="10" cy="10" r="9" fill="#f7c02b" stroke="#a96a00" stroke-width="1.6"/><circle cx="10" cy="10" r="5.7" fill="none" stroke="#fff1ad" stroke-width="1.5"/><path d="M6 6.6a5.4 5.4 0 0 1 3.2-2.1" stroke="#fff" stroke-width="1.4" stroke-linecap="round" fill="none" opacity=".85"/></svg>'
acc_page = head("Your account – Obscure Trivia", "Make an Obscure Trivia account with a username and password, so your coins are never lost.", SITE + "account/",
                "family=Bricolage+Grotesque:opsz,wght@12..96,700;12..96,800&family=Inter:wght@400;500;700", "#121117", hub_fav,
                extra_head=f"""<meta name="robots" content="noindex"><style>{hub_css}
.acct {{ max-width: 520px; }}
.card {{ background: var(--panel); border: 1px solid var(--line); border-radius: 16px; padding: 22px; display: flex; flex-direction: column; gap: 14px; }}
.card p {{ margin: 0; }}
.tabs {{ display: grid; grid-template-columns: 1fr 1fr; gap: 6px; padding: 4px; background: var(--bg); border: 1px solid var(--line); border-radius: 12px; }}
.tabs button {{ border: 0; border-radius: 9px; padding: 10px; font: inherit; font-weight: 700; background: none; color: var(--muted); cursor: pointer; }}
.tabs button[aria-selected="true"] {{ background: var(--panel); color: var(--ink); box-shadow: 0 0 0 1px var(--line); }}
.field {{ display: flex; flex-direction: column; gap: 6px; font-weight: 700; font-size: 0.92rem; }}
.field .input, .pw .input {{ flex: 1 1 auto; font-weight: 400; }}
.field > .input {{ flex: none; }}
.pw {{ display: flex; gap: 8px; }}
.btn.ghost {{ background: var(--panel); color: var(--ink); border: 1px solid var(--line); }}
.btn:disabled {{ opacity: 0.6; cursor: default; }}
.hint {{ color: var(--muted); font-size: 0.86rem; }}
.note {{ color: #f7c02b; font-size: 0.92rem; font-weight: 600; }}
.big {{ display: flex; align-items: center; gap: 12px; font-family: var(--f-display); font-weight: 800; font-size: 2.6rem; line-height: 1; font-variant-numeric: tabular-nums; }}
.big .coin-ico {{ width: 44px; height: 44px; }}
.coin-ico {{ display: block; flex: none; }}
.ok {{ color: #7ad155; font-weight: 700; }}
.err {{ color: #f08a7c; font-size: 0.92rem; min-height: 1.3em; }}
[hidden] {{ display: none !important; }}</style>""")
acc_page += """<div class="wrap acct">
  <header class="top"><a class="mark" href="../" aria-hidden="true" tabindex="-1" style="text-decoration:none">?</a><a class="brand" href="../" style="text-decoration:none">Obscure Trivia</a></header>
  <section class="hero"><span class="eyebrow">Your account</span><h2 id="acct-h">Keep your coins safe</h2>
    <p id="acct-p">Make an account with just a username and a password. Your coins are saved in it, so you never lose them, and you can sign in on any device.</p></section>
  <section class="card" id="acct-off" hidden><p>Accounts aren't switched on yet. Until they are, your coins are saved in this browser.</p></section>
  <section class="card" id="acct-in" hidden>
    <span class="eyebrow">Signed in as <b id="acct-user" style="color:var(--ink)"></b></span>
    <div class="big">""" + COIN_SVG + """<span id="acct-coins">0</span></div>
    <p class="hint">Your coins are saved in your account. Sign in with the same username and password on another phone or computer to use them there.</p>
    <p class="ok" id="acct-moved" hidden></p>
    <p class="hint" id="acct-pending"></p>
    <div class="row"><a class="btn" href="../" style="text-decoration:none">Play a quiz</a><button class="btn ghost" id="signout">Sign out</button></div>
    <p class="err" id="out-err" role="alert"></p>
  </section>
  <section class="card" id="acct-out" hidden>
    <div class="tabs" role="tablist"><button role="tab" id="tab-new" aria-selected="true">Create account</button><button role="tab" id="tab-in" aria-selected="false">Sign in</button></div>
    <form id="acct-form" autocomplete="on" style="display:flex;flex-direction:column;gap:14px">
      <label class="field">Username<input class="input" id="u" name="username" autocomplete="username" maxlength="20" autocapitalize="off" spellcheck="false" required></label>
      <label class="field">Password<span class="pw"><input class="input" id="p" name="password" type="password" autocomplete="new-password" maxlength="72" required>
        <button class="btn ghost" type="button" id="peek" aria-pressed="false">Show</button></span></label>
      <p class="hint" id="hint">Usernames are 3 to 20 letters, numbers or underscores. Passwords need at least 8 characters.</p>
      <p class="note" id="move-note" hidden></p>
      <button class="btn" type="submit" id="submit">Create account</button>
      <p class="err" id="form-err" role="alert"></p>
    </form>
    <p class="hint">There's no email address, so a forgotten password can't be reset. Write it down somewhere safe.</p>
    <p class="hint">Your account's coins can only be won: 1 for every right quiz answer, and in blackjack. Nothing else can change them, which keeps them fair for everyone.</p>
  </section>
  <p class="foot"><a href="../">← All quizzes</a></p>
</div>
<script src="../assets/account.js?v=""" + V_ACC + """"></script>
<script>
(() => {
  const C = window.OTCoins, $ = id => document.getElementById(id);
  let mode = "new", busy = false;
  function show() {
    const u = C.user();
    $("acct-off").hidden = C.enabled; $("acct-in").hidden = !C.enabled || !u; $("acct-out").hidden = !C.enabled || !!u;
    $("acct-h").textContent = u ? "Your account" : "Keep your coins safe";
    $("acct-p").hidden = !!u;
    if (u) {
      $("acct-user").textContent = u; $("acct-coins").textContent = C.get().toLocaleString();
      const n = C.pending(); $("acct-pending").textContent = n ? `${n} coin change${n === 1 ? " is" : "s are"} waiting to reach your account.` : "";
    } else {
      const here = C.get(), moving = Math.min(here, 500);
      $("move-note").hidden = !here || mode !== "new";
      $("move-note").textContent = `The ${moving.toLocaleString()} coin${moving === 1 ? "" : "s"} in this browser will move into your new account` + (here > 500 ? " (up to 500 can move)." : ".");
    }
  }
  function setMode(m) {
    mode = m;
    $("tab-new").setAttribute("aria-selected", String(m === "new")); $("tab-in").setAttribute("aria-selected", String(m === "in"));
    $("submit").textContent = m === "new" ? "Create account" : "Sign in";
    $("p").autocomplete = m === "new" ? "new-password" : "current-password";
    $("hint").hidden = m !== "new"; $("form-err").textContent = ""; show();
  }
  $("tab-new").onclick = () => setMode("new");
  $("tab-in").onclick = () => setMode("in");
  $("peek").onclick = () => { const p = $("p"), on = p.type === "password"; p.type = on ? "text" : "password"; $("peek").textContent = on ? "Hide" : "Show"; $("peek").setAttribute("aria-pressed", String(on)); };
  $("acct-form").onsubmit = async e => {
    e.preventDefault();
    if (busy) return;
    const u = $("u").value.trim(), p = $("p").value;
    if (mode === "new" && !/^[A-Za-z0-9_]{3,20}$/.test(u)) { $("form-err").textContent = "Usernames are 3 to 20 letters, numbers or underscores."; return; }
    if (mode === "new" && (p.length < 8 || p.length > 72)) { $("form-err").textContent = "Passwords need 8 to 72 characters."; return; }
    busy = true; $("submit").disabled = true; $("form-err").textContent = "";
    const was = $("submit").textContent; $("submit").textContent = mode === "new" ? "Creating…" : "Signing in…";
    try {
      const r = mode === "new" ? await C.signUp(u, p) : await C.signIn(u, p);
      $("p").value = "";
      $("acct-moved").hidden = !r.moved;
      $("acct-moved").textContent = r.moved ? `${r.moved.toLocaleString()} coin${r.moved === 1 ? "" : "s"} from this browser moved into your account.` : "";
    } catch (err) { $("form-err").textContent = err.message; }
    busy = false; $("submit").disabled = false; $("submit").textContent = was;
    show();
  };
  $("signout").onclick = async () => {
    $("out-err").textContent = "";
    try { await C.signOut(); $("acct-moved").hidden = true; setMode("in"); } catch (err) { $("out-err").textContent = err.message; }
  };
  C.on(show);
  setMode("new");
})();
</script>
</body>
</html>
"""

# ------------------------------------------------------------------ the Spend coins page: Blackjack, open to everyone
SP = os.path.join(SRC, "spend")
os.makedirs(os.path.join(OUT, "spend-coins"), exist_ok=True)
for fn in ("bj-core.js", "bj-sound.js", "bj-ui.js", "bj.css", "crates.js", "battle.js"):
    shutil.copy(os.path.join(SP, fn), os.path.join(OUT, "spend-coins", fn))
V_SP = {fn: stamp(os.path.join(OUT, "spend-coins", fn)) for fn in ("bj-core.js", "bj-sound.js", "bj-ui.js", "bj.css", "crates.js", "battle.js")}
sp_page = head("Spend Coins: Blackjack – Obscure Trivia", "Spend the coins you win in Obscure Trivia's quizzes: play blackjack against the dealer. Win and your bet comes back doubled; a blackjack pays 3 to 2.",
               SITE + "spend-coins/", "family=Bricolage+Grotesque:opsz,wght@12..96,700;12..96,800&family=Inter:wght@400;500;700", "#121117", hub_fav,
               extra_head=f"""<style>{hub_css}
.spend {{ max-width: 760px; }}
.back-link {{ margin-left: auto; color: var(--muted); text-decoration: none; font-weight: 700; font-size: 0.92rem; padding: 6px 13px; border-radius: 999px; border: 1px solid var(--line); }}
.back-link:hover {{ color: var(--ink); border-color: var(--muted); }}
.spend-tabs {{ display: flex; align-items: center; gap: 8px; padding: 4px; border-radius: 14px; border: 1px solid var(--line); background: var(--bg); width: fit-content; max-width: 100%; }}
.spend-tabs [role="tab"] {{ border: 0; border-radius: 10px; padding: 9px 16px; font: inherit; font-weight: 800; background: none; color: var(--muted); cursor: pointer; }}
.spend-tabs [role="tab"][aria-selected="true"] {{ background: var(--panel); color: var(--ink); box-shadow: 0 0 0 1px var(--line); }}
.btn.gold {{ background: #f2c14e; color: #2b1d00; }}
.btn {{ border-radius: 10px; border: 1px solid var(--line); padding: 11px 16px; font: inherit; font-weight: 800; background: var(--panel); color: var(--ink); cursor: pointer; }}
.btn:disabled {{ opacity: 0.5; cursor: default; }}
.bj-deal {{ display: block; }}
</style><link rel="stylesheet" href="bj.css?v={V_SP['bj.css']}">""")
sp_page += """<div class="wrap spend">
  <header class="top"><a class="mark" href="../" aria-hidden="true" tabindex="-1" style="text-decoration:none">?</a><a class="brand" href="../" style="text-decoration:none">Obscure Trivia</a>
    <a class="back-link" href="../">All quizzes</a></header>
  <section class="hero"><span class="eyebrow">Spend coins</span><h2>Put your coins on the line.</h2>
    <p>Every right answer in any quiz wins you a coin. Spend them here.</p></section>
  <div class="spend-tabs" role="tablist" aria-label="Ways to spend coins"><button role="tab" id="tab-bj" aria-selected="true" aria-controls="bj">🃏 Blackjack</button><button role="tab" id="tab-battles" aria-selected="false" aria-controls="battles">📦 Crate Battles</button></div>
""" + open(os.path.join(SP, "bj.html"), encoding="utf-8").read() + f"""
  <section class="panel" id="battles" role="tabpanel" aria-labelledby="tab-battles" hidden></section>
  <p class="foot">Coins have no money value and can't be bought or cashed out. They're just for fun.</p>
</div>
<script src="../assets/account.js?v={V_ACC}"></script>
<script src="bj-core.js?v={V_SP['bj-core.js']}"></script>
<script src="bj-sound.js?v={V_SP['bj-sound.js']}"></script>
<script src="bj-ui.js?v={V_SP['bj-ui.js']}"></script>
<script src="crates.js?v={V_SP['crates.js']}"></script>
<script src="battle.js?v={V_SP['battle.js']}"></script>
<script>
(() => {{
  // two tabs: Blackjack and Crate Battles (also opened by #battles, or by a battle code from the home page)
  const tabs = {{ bj: document.getElementById("tab-bj"), battles: document.getElementById("tab-battles") }};
  const show = which => {{
    for (const [k, t] of Object.entries(tabs)) {{ const on = k === which; t.setAttribute("aria-selected", String(on)); document.getElementById(k).hidden = !on; }}
    try {{ history.replaceState(null, "", location.pathname + (which === "battles" ? "#battles" : "")); }} catch (e) {{}}
  }};
  tabs.bj.onclick = () => show("bj");
  tabs.battles.onclick = () => show("battles");
  const join = new URLSearchParams(location.search).get("join");
  if (join && /^K/i.test(join)) {{ show("battles"); window.CrateBattles && window.CrateBattles.join(join); }}
  else if (location.hash === "#battles") show("battles");
}})();
</script>
</body>
</html>
"""
open(os.path.join(OUT, "spend-coins", "index.html"), "w", encoding="utf-8").write(sp_page)
os.makedirs(os.path.join(OUT, "account"), exist_ok=True)
open(os.path.join(OUT, "account", "index.html"), "w", encoding="utf-8").write(acc_page)

today = datetime.date.today().isoformat()
urls = [SITE] + [SITE + q["dir"] + "/" for q in QUIZZES] + [SITE + "spend-coins/"]
open(os.path.join(OUT, "sitemap.xml"), "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + "".join(f"  <url><loc>{u}</loc><lastmod>{today}</lastmod></url>\n" for u in urls) + "</urlset>\n")
open(os.path.join(OUT, ".nojekyll"), "w").write("")
print("built", OUT, os.listdir(OUT))
