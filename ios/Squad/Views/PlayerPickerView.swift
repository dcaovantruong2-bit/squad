import SwiftUI

struct PlayerPickerView: View {
    let slot: SlotSpec
    let squad: [PlayerCard]
    let fatigue: [String: Double]
    let usedPlayerIds: Set<String>
    let currentField: [(PlayerCard, String)]
    let synergies: [SynergyCard]
    let onSelect: (PlayerCard, String) -> Void
    
    @Environment(\.dismiss) var dismiss
    
    var eligiblePlayers: [PlayerCard] {
        squad.filter { player in
            !usedPlayerIds.contains(player.id) && isEligible(player, slot: slot)
        }
    }
    
    var body: some View {
        VStack(spacing: 0) {
            // Header
            VStack(spacing: 8) {
                Text("SELECT PLAYER")
                    .font(.system(size: 18, weight: .bold, design: .monospaced))
                    .foregroundColor(.green)
                
                Text("For: \(slotLabel(slot))")
                    .font(.system(size: 12, design: .monospaced))
                    .foregroundColor(.yellow)
            }
            .padding()
            .background(Color.black.opacity(0.3))
            
            // Player list
            ScrollView {
                LazyVStack(spacing: 8) {
                    if eligiblePlayers.isEmpty {
                        Text("No eligible players")
                            .font(.system(size: 14, design: .monospaced))
                            .foregroundColor(.gray)
                            .padding()
                    } else {
                        ForEach(eligiblePlayers) { player in
                            PlayerOptionRow(
                                player: player,
                                slot: slot,
                                fatigue: fatigue[player.id] ?? 1.0,
                                currentField: currentField,
                                synergies: synergies
                            ) {
                                let position = determinePosition(for: player, slot: slot)
                                onSelect(player, position)
                            }
                        }
                    }
                }
                .padding()
            }
            
            // Cancel button
            Button(action: { dismiss() }) {
                Text("CANCEL")
                    .font(.system(size: 14, design: .monospaced))
                    .foregroundColor(.gray)
                    .padding()
            }
        }
        .background(
            LinearGradient(
                colors: [Color(red: 0.05, green: 0.08, blue: 0.12),
                         Color(red: 0.08, green: 0.12, blue: 0.18)],
                startPoint: .top,
                endPoint: .bottom
            )
            .ignoresSafeArea()
        )
    }
    
    func isEligible(_ player: PlayerCard, slot: SlotSpec) -> Bool {
        switch slot {
        case .position(let pos):
            return player.position == pos
        case .positions(let positions):
            return positions.contains(player.position)
        case .statBased(_, let minAtk, let minPac, let minPas, let minDef, let minSpc, let trait):
            if let v = minAtk, player.atk < v { return false }
            if let v = minPac, player.pac < v { return false }
            if let v = minPas, player.pas < v { return false }
            if let v = minDef, player.def < v { return false }
            if let v = minSpc, player.spc < v { return false }
            if let t = trait, !player.traits.contains(t) { return false }
            return true
        }
    }
    
    func determinePosition(for player: PlayerCard, slot: SlotSpec) -> String {
        switch slot {
        case .position(let pos):
            return pos
        case .positions(let positions):
            return positions.first ?? player.position
        case .statBased(let asPos, _, _, _, _, _, _):
            return asPos
        }
    }
    
    func slotLabel(_ slot: SlotSpec) -> String {
        switch slot {
        case .position(let pos):
            return pos
        case .positions(let positions):
            return positions.joined(separator: "/")
        case .statBased(let asPos, let minAtk, let minPac, let minPas, let minDef, let minSpc, let trait):
            var parts = ["→\(asPos)"]
            if let v = minAtk { parts.append("ATK≥\(v)") }
            if let v = minPac { parts.append("PAC≥\(v)") }
            if let v = minPas { parts.append("PAS≥\(v)") }
            if let v = minDef { parts.append("DEF≥\(v)") }
            if let v = minSpc { parts.append("SPC≥\(v)") }
            if let t = trait { parts.append(t) }
            return parts.joined(separator: " ")
        }
    }
}

struct PlayerOptionRow: View {
    let player: PlayerCard
    let slot: SlotSpec
    let fatigue: Double
    let currentField: [(PlayerCard, String)]
    let synergies: [SynergyCard]
    let onSelect: () -> Void
    
    var body: some View {
        Button(action: onSelect) {
            VStack(alignment: .leading, spacing: 8) {
                HStack {
                    Text(player.name)
                        .font(.system(size: 14, weight: .bold, design: .monospaced))
                        .foregroundColor(.white)
                    
                    Spacer()
                    
                    // Fatigue indicator
                    if fatigue < 1.0 {
                        Text("\(Int(fatigue * 100))%")
                            .font(.system(size: 10, weight: .bold, design: .monospaced))
                            .foregroundColor(fatigue >= 0.7 ? .yellow : .red)
                            .padding(.horizontal, 6)
                            .padding(.vertical, 2)
                            .background((fatigue >= 0.7 ? Color.yellow : Color.red).opacity(0.2))
                            .cornerRadius(3)
                    }
                }
                
                // Stats
                HStack(spacing: 12) {
                    StatBadge(label: "ATK", value: player.atk, color: .red)
                    StatBadge(label: "PAC", value: player.pac, color: .cyan)
                    StatBadge(label: "PAS", value: player.pas, color: .green)
                    StatBadge(label: "DEF", value: player.def, color: .blue)
                    StatBadge(label: "SPC", value: player.spc, color: .purple)
                }
                
                // Traits
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
                
                // Synergy preview
                let position = determinePosition()
                let newSynergies = ScoringEngine.computeSynergyPreview(
                    player: player,
                    fieldPosition: position,
                    currentField: currentField,
                    synergies: synergies
                )
                
                if !newSynergies.isEmpty {
                    HStack(spacing: 4) {
                        Text("⚡")
                            .font(.system(size: 10))
                        Text(newSynergies.joined(separator: ", "))
                            .font(.system(size: 9, design: .monospaced))
                            .foregroundColor(.yellow)
                    }
                    .padding(6)
                    .background(Color.yellow.opacity(0.1))
                    .cornerRadius(4)
                }
            }
            .padding(12)
            .background(Color.white.opacity(0.05))
            .cornerRadius(6)
            .overlay(
                RoundedRectangle(cornerRadius: 6)
                    .stroke(Color.green.opacity(0.3), lineWidth: 1)
            )
        }
    }
    
    func determinePosition() -> String {
        switch slot {
        case .position(let pos):
            return pos
        case .positions(let positions):
            return positions.first ?? player.position
        case .statBased(let asPos, _, _, _, _, _, _):
            return asPos
        }
    }
}

#Preview {
    PlayerPickerView(
        slot: .position("CB"),
        squad: [],
        fatigue: [:],
        usedPlayerIds: [],
        currentField: [],
        synergies: [],
        onSelect: { _, _ in }
    )
}
