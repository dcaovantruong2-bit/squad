# SQUAD — Web PWA

A football card roguelike with Championship Manager 01 aesthetics.

## Play Now

Open `index.html` in any modern browser (Chrome, Safari, Firefox).

### iPhone Installation

1. Open `index.html` in Safari on your iPhone
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
   - Must meet role requirements: 1 GK, 3+ defenders, 3+ midfielders, 2+ attackers
   
2. **Formation Select** — Choose tactical shape (4-4-2, 4-3-3, etc.)
   - Each formation has position bonuses/penalties
   
3. **Campaign** — 5 escalating matches
   - Each match: win 2 of 3 rounds
   - Each round: 6 random phases of play
   - Each phase: field players to meet slot requirements
   - Synergies fire based on player combinations
   - Fatigue system: players get tired (×0.7 per use)

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
