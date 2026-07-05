import SwiftUI

struct PhaseResultView: View {
    let result: ScoreResult
    let onContinue: () -> Void
    
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                // Phase total
                VStack(spacing: 4) {
                    Text("PHASE TOTAL")
                        .font(.system(size: 12, design: .monospaced))
                        .foregroundColor(.gray)
                    Text("\(result.total)")
                        .font(.system(size: 48, weight: .bold, design: .monospaced))
                        .foregroundColor(.green)
                        .shadow(color: .green.opacity(0.5), radius: 8)
                }
                .frame(maxWidth: .infinity)
                .padding()
                .background(Color.black.opacity(0.3))
                .cornerRadius(8)
                
                // Breakdown
                VStack(alignment: .leading, spacing: 8) {
                    Text("BREAKDOWN")
                        .font(.system(size: 12, weight: .bold, design: .monospaced))
                        .foregroundColor(.cyan)
                    
                    ForEach(result.breakdown) { entry in
                        VStack(alignment: .leading, spacing: 4) {
                            HStack {
                                Text(entry.player)
                                    .font(.system(size: 13, weight: .bold, design: .monospaced))
                                    .foregroundColor(.white)
                                Text("[\(entry.position)]")
                                    .font(.system(size: 11, design: .monospaced))
                                    .foregroundColor(.cyan)
                                Spacer()
                                Text("\(entry.subtotal)")
                                    .font(.system(size: 14, weight: .bold, design: .monospaced))
                                    .foregroundColor(.green)
                            }
                            
                            // Formula
                            HStack(spacing: 8) {
                                Text("\(entry.baseChips) base")
                                    .font(.system(size: 10, design: .monospaced))
                                    .foregroundColor(.gray)
                                if entry.addChips > 0 {
                                    Text("+\(entry.addChips) syn")
                                        .font(.system(size: 10, design: .monospaced))
                                        .foregroundColor(.yellow)
                                }
                                if entry.multiply != 1.0 {
                                    Text("×\(String(format: "%.2f", entry.multiply))")
                                        .font(.system(size: 10, design: .monospaced))
                                        .foregroundColor(.magenta)
                                }
                                if entry.fatigue != 1.0 {
                                    Text("×\(String(format: "%.2f", entry.fatigue)) fat")
                                        .font(.system(size: 10, design: .monospaced))
                                        .foregroundColor(.red)
                                }
                            }
                        }
                        .padding(8)
                        .background(Color.white.opacity(0.05))
                        .cornerRadius(4)
                    }
                }
                
                // Global effects
                if result.globalMult != 1.0 || result.globalAdd != 0 {
                    VStack(alignment: .leading, spacing: 4) {
                        Text("GLOBAL")
                            .font(.system(size: 12, weight: .bold, design: .monospaced))
                            .foregroundColor(.magenta)
                        
                        if result.globalMult != 1.0 {
                            Text("×\(String(format: "%.2f", result.globalMult)) global mult")
                                .font(.system(size: 11, design: .monospaced))
                                .foregroundColor(.magenta)
                        }
                        if result.globalAdd != 0 {
                            Text("+\(result.globalAdd) global bonus")
                                .font(.system(size: 11, design: .monospaced))
                                .foregroundColor(.magenta)
                        }
                    }
                    .padding(8)
                    .background(Color.magenta.opacity(0.1))
                    .cornerRadius(4)
                }
                
                // Formation
                if result.formationMult != 1.0 {
                    HStack {
                        Text("Formation: \(result.formationName)")
                            .font(.system(size: 11, design: .monospaced))
                            .foregroundColor(.cyan)
                        Spacer()
                        Text("×\(String(format: "%.1f", result.formationMult))")
                            .font(.system(size: 11, weight: .bold, design: .monospaced))
                            .foregroundColor(.cyan)
                    }
                    .padding(8)
                    .background(Color.cyan.opacity(0.1))
                    .cornerRadius(4)
                }
                
                // Synergies
                if !result.firedSynergies.isEmpty {
                    VStack(alignment: .leading, spacing: 6) {
                        Text("SYNERGIES")
                            .font(.system(size: 12, weight: .bold, design: .monospaced))
                            .foregroundColor(.yellow)
                        
                        ForEach(result.firedSynergies, id: \.self) { syn in
                            HStack(alignment: .top, spacing: 6) {
                                Text("⚡")
                                    .font(.system(size: 10))
                                VStack(alignment: .leading, spacing: 2) {
                                    Text(syn)
                                        .font(.system(size: 11, weight: .bold, design: .monospaced))
                                        .foregroundColor(.yellow)
                                    if let desc = result.synergyDescriptions[syn] {
                                        Text(desc)
                                            .font(.system(size: 9, design: .monospaced))
                                            .foregroundColor(.gray)
                                    }
                                    if let contributors = result.synergyContributors[syn] {
                                        Text(contributors.joined(separator: ", "))
                                            .font(.system(size: 9, design: .monospaced))
                                            .foregroundColor(.orange)
                                    }
                                }
                            }
                            .padding(6)
                            .background(Color.yellow.opacity(0.1))
                            .cornerRadius(4)
                        }
                    }
                }
                
                // Continue button
                Button(action: onContinue) {
                    Text("CONTINUE")
                        .font(.system(size: 16, weight: .bold, design: .monospaced))
                        .foregroundColor(.black)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.green)
                        .cornerRadius(8)
                }
            }
            .padding()
        }
    }
}

#Preview {
    PhaseResultView(
        result: ScoreResult(
            total: 420,
            breakdown: [
                ScoreBreakdownEntry(player: "V. van Dijk", position: "CB", baseChips: 50, addChips: 30, multiply: 1.0, fatigue: 1.0, subtotal: 80),
                ScoreBreakdownEntry(player: "H. Lloris", position: "GK", baseChips: 40, addChips: 30, multiply: 1.0, fatigue: 1.0, subtotal: 70)
            ],
            subtotalBeforeGlobals: 150,
            formationMult: 1.0,
            formationName: "4-4-2",
            globalMult: 1.0,
            globalAdd: 0,
            firedSynergies: ["Clean Sheet"],
            nextCarryover: nil,
            synergyContributors: ["Clean Sheet": ["V. van Dijk [CB]", "H. Lloris [GK]"]],
            synergyDescriptions: ["Clean Sheet": "GK+CB DEF≥16: both +30 chips"]
        ),
        onContinue: {}
    )
}
