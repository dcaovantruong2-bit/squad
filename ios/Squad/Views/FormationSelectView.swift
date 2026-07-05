import SwiftUI

struct FormationSelectView: View {
    @EnvironmentObject var gameState: GameState
    @State private var selectedFormationIndex = 0
    
    var body: some View {
        VStack(spacing: 0) {
            // Header
            VStack(spacing: 8) {
                Text("CHOOSE FORMATION")
                    .font(.system(size: 20, weight: .bold, design: .monospaced))
                    .foregroundColor(.green)
                
                Text("Select your tactical shape")
                    .font(.system(size: 12, design: .monospaced))
                    .foregroundColor(.gray)
            }
            .padding()
            .background(Color.black.opacity(0.3))
            
            // Formation list
            ScrollView {
                LazyVStack(spacing: 12) {
                    ForEach(Array(gameState.allFormations.enumerated()), id: \.element.id) { index, formation in
                        FormationCard(
                            formation: formation,
                            isSelected: index == selectedFormationIndex,
                            squad: gameState.selectedSquad
                        ) {
                            selectedFormationIndex = index
                        }
                    }
                }
                .padding()
            }
            
            // Continue button
            Button(action: {
                gameState.selectFormation(gameState.allFormations[selectedFormationIndex])
            }) {
                Text("SELECT & START MATCH")
                    .font(.system(size: 16, weight: .bold, design: .monospaced))
                    .foregroundColor(.black)
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.green)
                    .cornerRadius(8)
            }
            .padding()
            .background(Color.black.opacity(0.3))
        }
    }
}

struct FormationCard: View {
    let formation: FormationCard
    let isSelected: Bool
    let squad: [PlayerCard]
    let onSelect: () -> Void
    
    var body: some View {
        Button(action: onSelect) {
            VStack(alignment: .leading, spacing: 10) {
                HStack {
                    Text(formation.name)
                        .font(.system(size: 18, weight: .bold, design: .monospaced))
                        .foregroundColor(isSelected ? .green : .white)
                    
                    Spacer()
                    
                    if isSelected {
                        Text("✓")
                            .font(.system(size: 20, weight: .bold))
                            .foregroundColor(.green)
                    }
                }
                
                Text(formation.description)
                    .font(.system(size: 12, design: .monospaced))
                    .foregroundColor(.gray)
                
                // Position bonuses
                if !formation.positionBonus.isEmpty {
                    HStack(spacing: 8) {
                        ForEach(formation.positionBonus.sorted(by: { $0.key < $1.key }), id: \.key) { pos, bonus in
                            HStack(spacing: 2) {
                                Text(pos)
                                    .font(.system(size: 10, weight: .bold, design: .monospaced))
                                Text(bonus >= 0 ? "+\(bonus)" : "\(bonus)")
                                    .font(.system(size: 10, weight: .bold, design: .monospaced))
                            }
                            .foregroundColor(bonus >= 0 ? .green : .red)
                            .padding(.horizontal, 6)
                            .padding(.vertical, 3)
                            .background((bonus >= 0 ? Color.green : Color.red).opacity(0.2))
                            .cornerRadius(4)
                        }
                    }
                }
                
                // Fit score
                let fitScore = calculateFitScore()
                if fitScore > 0 {
                    HStack {
                        Text("Squad fit:")
                            .font(.system(size: 10, design: .monospaced))
                            .foregroundColor(.gray)
                        Text("\(fitScore)")
                            .font(.system(size: 10, weight: .bold, design: .monospaced))
                            .foregroundColor(fitScore > 50 ? .green : .yellow)
                    }
                }
            }
            .padding(12)
            .background(isSelected ? Color.green.opacity(0.1) : Color.white.opacity(0.05))
            .cornerRadius(8)
            .overlay(
                RoundedRectangle(cornerRadius: 8)
                    .stroke(isSelected ? Color.green : Color.gray.opacity(0.3), lineWidth: isSelected ? 2 : 1)
            )
        }
    }
    
    func calculateFitScore() -> Int {
        var score = 0
        let posCounts = Dictionary(grouping: squad, by: { $0.position }).mapValues { $0.count }
        
        for (pos, bonus) in formation.positionBonus {
            let count = posCounts[pos] ?? 0
            if bonus > 0 && count > 0 {
                score += count * count * 2
            }
        }
        
        return score
    }
}

#Preview {
    FormationSelectView()
        .environmentObject(GameState())
}
