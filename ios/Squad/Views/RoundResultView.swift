import SwiftUI

struct RoundResultView: View {
    @ObservedObject var match: MatchState
    let onContinue: () -> Void
    
    var body: some View {
        let won = match.roundScore >= match.currentTarget
        
        VStack(spacing: 20) {
            Spacer()
            
            // Result icon
            Text(won ? "🎉" : "💔")
                .font(.system(size: 80))
            
            // Result text
            Text(won ? "ROUND WON!" : "ROUND LOST")
                .font(.system(size: 32, weight: .bold, design: .monospaced))
                .foregroundColor(won ? .green : .red)
                .shadow(color: (won ? Color.green : Color.red).opacity(0.5), radius: 10)
            
            // Score
            Text("\(match.roundScore) / \(match.currentTarget)")
                .font(.system(size: 20, weight: .bold, design: .monospaced))
                .foregroundColor(.white)
            
            // Phase breakdown
            VStack(alignment: .leading, spacing: 8) {
                Text("Phase Results:")
                    .font(.system(size: 12, weight: .bold, design: .monospaced))
                    .foregroundColor(.gray)
                
                ForEach(Array(match.phaseResults.enumerated()), id: \.offset) { index, result in
                    HStack {
                        Text("Phase \(index + 1):")
                            .font(.system(size: 11, design: .monospaced))
                            .foregroundColor(.gray)
                        Text(result["phase_name"] as? String ?? "")
                            .font(.system(size: 11, design: .monospaced))
                            .foregroundColor(.white)
                        Spacer()
                        Text("\(result["total"] as? Int ?? 0)")
                            .font(.system(size: 11, weight: .bold, design: .monospaced))
                            .foregroundColor(.green)
                    }
                }
                
                Divider()
                    .background(Color.gray)
                
                HStack {
                    Text("Total")
                        .font(.system(size: 12, weight: .bold, design: .monospaced))
                        .foregroundColor(.white)
                    Spacer()
                    Text("\(match.roundScore)")
                        .font(.system(size: 12, weight: .bold, design: .monospaced))
                        .foregroundColor(.green)
                }
            }
            .padding()
            .background(Color.white.opacity(0.05))
            .cornerRadius(8)
            
            // Match score
            Text("Match: \(match.roundsWon)-\(match.roundsLost)")
                .font(.system(size: 16, weight: .bold, design: .monospaced))
                .foregroundColor(.yellow)
            
            Spacer()
            
            // Continue button
            Button(action: onContinue) {
                Text(match.isMatchOver ? "MATCH RESULT" : "NEXT ROUND")
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

#Preview {
    RoundResultView(
        match: MatchState(squad: [], synergies: []),
        onContinue: {}
    )
}
