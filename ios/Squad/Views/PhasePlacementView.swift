import SwiftUI

struct PhasePlacementView: View {
    let phase: Phase
    @ObservedObject var match: MatchState
    let onPhaseComplete: (ScoreResult) -> Void
    
    @State private var currentSlotIndex = 0
    @State private var showingPlayerPicker = false
    @State private var showingSynergies = false
    
    var body: some View {
        VStack(spacing: 0) {
            // Phase header
            phaseHeaderView
            
            // Field visualization
            fieldView
            
            // Slot requirements
            slotRequirementsView
            
            // Action buttons
            actionButtonsView
        }
    }
    
    var phaseHeaderView: some View {
        VStack(spacing: 8) {
            HStack {
                Text("Phase \(match.currentPhaseIdx + 1)/6")
                    .font(.system(size: 12, design: .monospaced))
                    .foregroundColor(.gray)
                
                Spacer()
                
                Text(phase.weight)
                    .font(.system(size: 10, weight: .bold, design: .monospaced))
                    .foregroundColor(.white)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(Color.blue.opacity(0.3))
                    .cornerRadius(4)
            }
            
            Text(phase.name)
                .font(.system(size: 20, weight: .bold, design: .monospaced))
                .foregroundColor(.yellow)
            
            Text(phase.description)
                .font(.system(size: 11, design: .monospaced))
                .foregroundColor(.gray)
                .multilineTextAlignment(.center)
        }
        .padding()
        .background(Color.black.opacity(0.2))
    }
    
    var fieldView: some View {
        VStack(spacing: 12) {
            if match.field.isEmpty {
                Text("No players placed")
                    .font(.system(size: 14, design: .monospaced))
                    .foregroundColor(.gray)
                    .padding()
            } else {
                ForEach(Array(match.field.enumerated()), id: \.offset) { index, playerPos in
                    let (player, pos) = playerPos
                    let fatigue = match.getFatigue(player.id)
                    let chips = ScoringEngine.calculateChips(player, position: pos)
                    
                    HStack {
                        Text(pos)
                            .font(.system(size: 12, weight: .bold, design: .monospaced))
                            .foregroundColor(.cyan)
                            .frame(width: 40, alignment: .leading)
                        
                        Text(player.name)
                            .font(.system(size: 13, design: .monospaced))
                            .foregroundColor(.white)
                        
                        Spacer()
                        
                        Text("\(chips)")
                            .font(.system(size: 12, weight: .bold, design: .monospaced))
                            .foregroundColor(.green)
                        
                        if fatigue < 1.0 {
                            Text("\(Int(fatigue * 100))%")
                                .font(.system(size: 10, design: .monospaced))
                                .foregroundColor(fatigue >= 0.7 ? .yellow : .red)
                        }
                    }
                    .padding(8)
                    .background(Color.green.opacity(0.1))
                    .cornerRadius(4)
                }
            }
        }
        .padding()
        .frame(maxWidth: .infinity)
        .background(Color.black.opacity(0.1))
    }
    
    var slotRequirementsView: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Slots to fill:")
                .font(.system(size: 12, weight: .bold, design: .monospaced))
                .foregroundColor(.gray)
            
            ForEach(Array(phase.slots.enumerated()), id: \.offset) { index, slot in
                HStack {
                    Circle()
                        .fill(index < match.field.count ? Color.green : Color.gray.opacity(0.3))
                        .frame(width: 8, height: 8)
                    
                    Text(slotLabel(slot))
                        .font(.system(size: 11, design: .monospaced))
                        .foregroundColor(index < match.field.count ? .green : .white)
                    
                    Spacer()
                    
                    if index == currentSlotIndex && index < phase.slots.count {
                        Text("← current")
                            .font(.system(size: 10, design: .monospaced))
                            .foregroundColor(.yellow)
                    }
                }
            }
        }
        .padding()
        .background(Color.black.opacity(0.2))
    }
    
    var actionButtonsView: some View {
        VStack(spacing: 12) {
            if currentSlotIndex < phase.slots.count {
                Button(action: { showingPlayerPicker = true }) {
                    Text("SELECT PLAYER")
                        .font(.system(size: 14, weight: .bold, design: .monospaced))
                        .foregroundColor(.black)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.green)
                        .cornerRadius(6)
                }
                .sheet(isPresented: $showingPlayerPicker) {
                    PlayerPickerView(
                        slot: phase.slots[currentSlotIndex],
                        squad: match.squad,
                        fatigue: match.fatigue,
                        usedPlayerIds: Set(match.field.map { $0.0.id }),
                        currentField: match.field,
                        synergies: match.synergies
                    ) { player, position in
                        match.field.append((player, position))
                        currentSlotIndex += 1
                        showingPlayerPicker = false
                        
                        if currentSlotIndex >= phase.slots.count {
                            resolvePhase()
                        }
                    }
                }
            } else {
                Button(action: { resolvePhase() }) {
                    Text("RESOLVE PHASE")
                        .font(.system(size: 14, weight: .bold, design: .monospaced))
                        .foregroundColor(.black)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.yellow)
                        .cornerRadius(6)
                }
            }
            
            Button(action: { showingSynergies = true }) {
                Text("VIEW SYNERGIES (\(match.synergies.count))")
                    .font(.system(size: 12, design: .monospaced))
                    .foregroundColor(.cyan)
            }
            .sheet(isPresented: $showingSynergies) {
                SynergyListView(synergies: match.synergies)
            }
        }
        .padding()
        .background(Color.black.opacity(0.3))
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
    
    func resolvePhase() {
        let result = ScoringEngine.calculateRoundScore(
            field: match.field,
            synergyCards: match.synergies,
            formation: match.formation,
            fatigue: match.fatigue,
            carryover: match.carryover,
            persistentBuffs: match.persistentBuffs
        )
        
        // Apply fatigue
        for (player, _) in match.field {
            match.applyFatigue(player.id)
        }
        
        match.carryover = result.nextCarryover
        match.roundScore += result.total
        match.phaseResults.append([
            "phase_name": phase.name,
            "total": result.total
        ])
        
        onPhaseComplete(result)
    }
}

#Preview {
    PhasePlacementView(
        phase: DataLoader.defaultPhases()[0],
        match: MatchState(squad: [], synergies: []),
        onPhaseComplete: { _ in }
    )
}
