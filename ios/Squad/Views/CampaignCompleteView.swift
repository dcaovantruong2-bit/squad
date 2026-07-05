import SwiftUI

struct CampaignCompleteView: View {
    @EnvironmentObject var gameState: GameState
    
    var body: some View {
        VStack(spacing: 30) {
            Spacer()
            
            Text("🏆")
                .font(.system(size: 100))
            
            Text("TOURNAMENT CHAMPIONS!")
                .font(.system(size: 24, weight: .bold, design: .monospaced))
                .foregroundColor(.green)
                .shadow(color: .green.opacity(0.6), radius: 10)
                .multilineTextAlignment(.center)
            
            Text("Your squad conquered all 5 matches!")
                .font(.system(size: 14, design: .monospaced))
                .foregroundColor(.white)
            
            // Campaign results
            VStack(alignment: .leading, spacing: 8) {
                ForEach(Array(gameState.campaignMatches.enumerated()), id: \.offset) { index, matchDef in
                    HStack {
                        Text("Match \(index + 1):")
                            .font(.system(size: 11, design: .monospaced))
                            .foregroundColor(.gray)
                        Text(matchDef["name"] as? String ?? "")
                            .font(.system(size: 11, weight: .bold, design: .monospaced))
                            .foregroundColor(.white)
                        Spacer()
                        Text("✓ WIN")
                            .font(.system(size: 11, weight: .bold, design: .monospaced))
                            .foregroundColor(.green)
                    }
                }
            }
            .padding()
            .background(Color.white.opacity(0.05))
            .cornerRadius(8)
            
            Spacer()
            
            Button(action: { gameState.resetToTitle() }) {
                Text("PLAY AGAIN")
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
    CampaignCompleteView()
        .environmentObject(GameState())
}
