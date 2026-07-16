# SQUAD — Web PWA

A football card roguelike with Championship Manager 01 aesthetics.

## Play Now

Open `game.html` in any modern browser (Chrome, Safari, Firefox). `index.html`
(109 bytes) just redirects to `game.html`.

### iPhone Installation

1. Open `game.html` in Safari on your iPhone
2. Tap the Share button (square with arrow)
3. Tap "Add to Home Screen"
4. Launch from your home screen — it runs as a standalone app!

### Local Testing (Recommended)

Run a simple HTTP server to test the PWA properly:

```bash
cd /home/hermes/games/squad/web
python3 -m http.server 8080
```

Then open `http://localhost:8080` in your browser.

For iPhone testing over Tailscale:
```bash
python3 -m http.server 8080 --bind 100.82.27.85
```

Then access from iPhone: `http://100.82.27.85:8080`

## Game Flow

1. **Squad Builder** — Pick 10+ players within 360 budget
   - Role requirements bar shows group progress (GK, Defenders, Midfielders, Attackers)
   - Your Squad section shows synergy tags per player (which persistent synergies they enable)
   - Available players grouped by position with player count
   - Tap to add, tap again to remove

2. **Formation Select** — Choose tactical shape with fit score
   - Each formation gets a **fit score** based on your squad composition
   - ⭐ Recommended badge for best fit
   - 📊 Fit reasons show why (e.g. "3 CMs PAS8+ → Tiki-Taka")
   - Position bonuses shown in green, penalties in red

3. **Round Start Briefing** — See all round synergies before first phase
   - Rarity-colored synergy cards (Common/Uncommon/Rare/Epic/Legendary)
   - Persistent synergies displayed with descriptions
   - Build your phase strategy based on available synergies

4. **Phase Placement** — Pitch-aligned slot cards
   - Slots arranged by pitch zone (ATTACK / MIDFIELD / DEFENSE)
   - Current slot glows yellow — tap to open player picker
   - Filled slots show player name + chips + fatigue
   - Skipped slots marked in red
   - Live running total with phase score preview
   - Progress dots (● green=done, ● red=skipped, ● yellow=current)

5. **Phase Result** — Full math breakdown table
   - Column-aligned breakdown (PLAYER | POS | BASE | +SYN | ×MULT | ×FAT | = SUB)
   - Global effects and formation multipliers
   - Synergy box with contributors + descriptions
   - Running total toward round target

6. **Round Result** — Bar chart visualization
   - █░ bars showing relative phase performance
   - Fatigue summary (fresh / at 70% / below 50%)
   - Match record with progress to 2 wins

7. **Campaign** — 5 escalating matches, win 2 of 3 rounds each
   - Persistent synergies shown at match start and match end
   - Game over screen shows active persistent synergies

## Aesthetic

- **CM01 Influence**: Dark tactical UI, monospace fonts, stat-heavy displays, functional layout
- **Balatro Influence**: Neon accents (green/cyan/yellow), glowing effects, synergy popups, multiplier reveals
- **No poker chips** — pure football manager vibes

## Features

✅ Full game logic ported from Python  
✅ 30 players across all positions  
✅ 6 formations with position bonuses  
✅ 11 phase types with stat-based slots  
✅ 21 synergies (17 phase-specific + 4 persistent)  
✅ Fatigue system with recovery  
✅ Campaign progression (5 matches)  
✅ PWA support (installable on iPhone)  
✅ Responsive design (optimized for mobile)  

## iOS Native App

The `ios/` directory contains complete Swift/SwiftUI source code for a native iOS app.

### To Build on Mac:

1. Copy the `ios/` folder to your Mac
2. Open `Squad.xcodeproj` in Xcode
3. Select your iPhone as the target device
4. Build and run (Cmd+R)

The native app has identical game logic and the same CM01 aesthetic.

## Tech Stack

**Web Version:**
- Pure HTML/CSS/JavaScript (no frameworks)
- Service Worker for offline support
- PWA manifest for installation

**iOS Version:**
- Swift 5.9+
- SwiftUI
- iOS 16+ target

## Credits

Game design: Football card roguelike inspired by Slay the Spire × Balatro × Championship Manager 01

Built with Hermes Agent
