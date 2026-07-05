import SwiftUI

struct SquadBuilderView: View {
    @EnvironmentObject var gameState: GameState
    @State private var selectedTab = 0
    
    let positionOrder = ["GK", "CB", "FB", "CDM", "CM", "CAM", "LW", "RW", "ST"]
    let positionIcons = ["GK": "🧤", "CB": "🛡️", "FB": "↔️", "CDM": "🔧", "CM": "🔄", "CAM": "🎯", "LW": "⬅️", "RW": "➡️", "ST": "⚽"]
    
    var body: some View {
        VStack(spacing: 0) {
            // Header
            VStack(spacing: 8) {
                Text("BUILD YOUR SQUAD")
                    .font(.system(size: 20, weight: .bold, design: .monospaced))
                    .foregroundColor(.green)
                
                // Budget bar
                let spent = gameState.selectedSquad.reduce(0) { $0 + $1.cost }
                let remaining = gameState.budget - spent
                
                HStack {
                    Text("Budget:")
                        .font(.system(size: 12, design: .monospaced))
                        .foregroundColor(.gray)
                    Text("\(spent)/\(gameState.budget)")
                        .font(.system(size: 12, weight: .bold, design: .monospaced))
                        .foregroundColor(remaining >= 0 ? .green : .red)
                    Spacer()
                    Text("\(gameState.selectedSquad.count) players")
                        .font(.system(size: 12, design: .monospaced))
                        .foregroundColor(.gray)
                }
                .padding(.horizontal)
                
                // Progress bar
                GeometryReader { geo in
                    ZStack(alignment: .leading) {
                        Rectangle()
                            .fill(Color.gray.opacity(0.2))
                            .frame(height: 8)
                        Rectangle()
                            .fill(Color.green)
                            .frame(width: geo.size.width * CGFloat(Double(spent) / Double(gameState.budget)), height: 8)
                    }
                }
                .frame(height: 8)
                .padding(.horizontal)
            }
            .padding()
            .background(Color.black.opacity(0.3))
            
            // Tabs
            Picker("View", selection: $selectedTab) {
                Text("Available").tag(0)
                Text("Your Squad").tag(1)
            }
            .pickerStyle(.segmented)
            .padding(.horizontal)
            
            // Content
            if selectedTab == 0 {
                availablePlayersView
            } else {
                yourSquadView
            }
            
            // Footer
            footerView
        }
    }
    
    var availablePlayersView: some View {
        ScrollView {
            LazyVStack(alignment: .leading, spacing: 16) {
                ForEach(positionOrder, id: \.self) { pos in
                    let players = gameState.allPlayers.filter { $0.position == pos && !gameState.selectedSquad.contains($0) }
                    if !players.isEmpty {
                        VStack(alignment: .leading, spacing: 8) {
                            Text("\(positionIcons[pos] ?? "") \(pos)")
                                .font(.system(size: 14, weight: .bold, design: .monospaced))
                                .foregroundColor(.cyan)
                            
                            ForEach(players) { player in
                                PlayerCardRow(player: player, canAfford: canAfford(player)) {
                                    addPlayer(player)
                                }
                            }
                        }
                    }
                }
            }
            .padding()
        }
    }
    
    var yourSquadView: some View {
        ScrollView {
            LazyVStack(alignment: .leading, spacing: 8) {
                if gameState.selectedSquad.isEmpty {
                    Text("No players selected yet")
                        .font(.system(size: 14, design: .monospaced))
                        .foregroundColor(.gray)
                        .padding()
                } else {
                    ForEach(Array(gameState.selectedSquad.enumerated()), id: \.element.id) { index, player in
                        HStack {
                            Text("[\(player.position)]")
                                .font(.system(size: 12, weight: .bold, design: .monospaced))
                                .foregroundColor(.cyan)
                                .frame(width: 40, alignment: .leading)
                            
                            Text(player.name)
                                .font(.system(size: 14, design: .monospaced))
                                .foregroundColor(.white)
                            
                            Spacer()
                            
                            Text("\(player.cost)")
                                .font(.system(size: 12, design: .monospaced))
                                .foregroundColor(.yellow)
                            
                            Button(action: { removePlayer(index) }) {
                                Text("✕")
                                    .font(.system(size: 14, weight: .bold))
                                    .foregroundColor(.red)
                                    .padding(8)
                            }
                        }
                        .padding(8)
                        .background(Color.white.opacity(0.05))
                        .cornerRadius(4)
                    }
                }
            }
            .padding()
        }
    }
    
    var footerView: some View {
        VStack(spacing: 12) {
            // Requirements
            let missing = checkMinimums()
            if !missing.isEmpty {
                VStack(alignment: .leading, spacing: 4) {
                    ForEach(missing, id: \.self) { req in
                        Text("✗ \(req)")
                            .font(.system(size: 11, design: .monospaced))
                            .foregroundColor(.red)
                    }
                }
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding(.horizontal)
            } else if gameState.selectedSquad.count >= gameState.minPlayers {
                Text("✓ Requirements met")
                    .font(.system(size: 11, design: .monospaced))
                    .foregroundColor(.green)
            }
            
            // Continue button
            Button(action: { gameState.finalizeSquad() }) {
                Text("CONTINUE")
                    .font(.system(size: 16, weight: .bold, design: .monospaced))
                    .foregroundColor(canContinue() ? .black : .gray)
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(canContinue() ? Color.green : Color.gray.opacity(0.3))
                    .cornerRadius(8)
            }
            .disabled(!canContinue())
            .padding(.horizontal)
        }
        .padding()
        .background(Color.black.opacity(0.3))
    }
    
    func canAfford(_ player: PlayerCard) -> Bool {
        let spent = gameState.selectedSquad.reduce(0) { $0 + $1.cost }
        return (gameState.budget - spent) >= player.cost
    }
    
    func addPlayer(_ player: PlayerCard) {
        if canAfford(player) {
            gameState.selectedSquad.append(player)
        }
    }
    
    func removePlayer(_ index: Int) {
        if index < gameState.selectedSquad.count {
            gameState.selectedSquad.remove(at: index)
        }
    }
    
    func checkMinimums() -> [String] {
        var missing: [String] = []
        let posCounts = Dictionary(grouping: gameState.selectedSquad, by: { $0.position }).mapValues { $0.count }
        
        let gkCount = posCounts["GK"] ?? 0
        if gkCount < 1 { missing.append("1 GK (have \(gkCount))") }
        
        let defCount = (posCounts["CB"] ?? 0) + (posCounts["FB"] ?? 0)
        if defCount < 3 { missing.append("3+ Defenders (have \(defCount))") }
        
        let midCount = (posCounts["CM"] ?? 0) + (posCounts["CDM"] ?? 0) + (posCounts["CAM"] ?? 0)
        if midCount < 3 { missing.append("3+ Midfielders (have \(midCount))") }
        
        let attCount = (posCounts["ST"] ?? 0) + (posCounts["LW"] ?? 0) + (posCounts["RW"] ?? 0)
        if attCount < 2 { missing.append("2+ Attackers (have \(attCount))") }
        
        if gameState.selectedSquad.count < gameState.minPlayers {
            missing.append("\(gameState.minPlayers) players minimum (have \(gameState.selectedSquad.count))")
        }
        
        return missing
    }
    
    func canContinue() -> Bool {
        checkMinimums().isEmpty
    }
}

struct PlayerCardRow: View {
    let player: PlayerCard
    let canAfford: Bool
    let onAdd: () -> Void
    
    var body: some View {
        Button(action: onAdd) {
            VStack(alignment: .leading, spacing: 6) {
                HStack {
                    Text(player.name)
                        .font(.system(size: 14, weight: .bold, design: .monospaced))
                        .foregroundColor(canAfford ? .white : .gray)
                    
                    Spacer()
                    
                    Text("\(player.cost)")
                        .font(.system(size: 12, weight: .bold, design: .monospaced))
                        .foregroundColor(canAfford ? .yellow : .red)
                }
                
                HStack(spacing: 12) {
                    StatBadge(label: "ATK", value: player.atk, color: .red)
                    StatBadge(label: "PAC", value: player.pac, color: .cyan)
                    StatBadge(label: "PAS", value: player.pas, color: .green)
                    StatBadge(label: "DEF", value: player.def, color: .blue)
                    StatBadge(label: "SPC", value: player.spc, color: .purple)
                }
                
                if !player.traits.isEmpty {
                    HStack(spacing: 4) {
                        ForEach(player.traits, id: \.self) { trait in
                            Text(trait)
                                .font(.system(size: 9, design: .monospaced))
                                .foregroundColor(.orange)
                                .padding(.horizontal, 6)
                                .padding(.vertical, 2)
                                .background(Color.orange.opacity(0.2))
                                .cornerRadius(3)
                        }
                    }
                }
            }
            .padding(10)
            .background(canAfford ? Color.white.opacity(0.05) : Color.red.opacity(0.05))
            .cornerRadius(6)
            .overlay(
                RoundedRectangle(cornerRadius: 6)
                    .stroke(canAfford ? Color.green.opacity(0.3) : Color.red.opacity(0.3), lineWidth: 1)
            )
        }
        .disabled(!canAfford)
    }
}

struct StatBadge: View {
    let label: String
    let value: Int
    let color: Color
    
    var body: some View {
        VStack(spacing: 2) {
            Text(label)
                .font(.system(size: 8, weight: .bold, design: .monospaced))
                .foregroundColor(color)
            Text("\(value)")
                .font(.system(size: 12, weight: .bold, design: .monospaced))
                .foregroundColor(.white)
        }
    }
}

#Preview {
    SquadBuilderView()
        .environmentObject(GameState())
}
