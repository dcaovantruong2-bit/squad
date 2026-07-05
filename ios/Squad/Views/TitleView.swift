import SwiftUI

struct TitleView: View {
    @EnvironmentObject var gameState: GameState
    
    var body: some View {
        VStack(spacing: 40) {
            Spacer()
            
            // Logo
            VStack(spacing: 12) {
                Text("⚽")
                    .font(.system(size: 80))
                
                Text("SQUAD")
                    .font(.system(size: 56, weight: .bold, design: .monospaced))
                    .foregroundColor(.green)
                    .shadow(color: .green.opacity(0.6), radius: 10)
                
                Text("Football Card Roguelike")
                    .font(.system(size: 16, weight: .medium, design: .monospaced))
                    .foregroundColor(.gray)
            }
            
            Spacer()
            
            // Start button
            Button(action: { gameState.startNewCampaign() }) {
                HStack {
                    Text("START CAMPAIGN")
                        .font(.system(size: 18, weight: .bold, design: .monospaced))
                        .foregroundColor(.black)
                }
                .frame(maxWidth: .infinity)
                .padding()
                .background(Color.green)
                .cornerRadius(8)
            }
            .padding(.horizontal, 40)
            
            // Info
            VStack(spacing: 8) {
                Text("5 matches • 3 rounds each • 6 phases per round")
                    .font(.system(size: 12, design: .monospaced))
                    .foregroundColor(.gray)
                Text("Win 2 of 3 rounds to advance")
                    .font(.system(size: 12, design: .monospaced))
                    .foregroundColor(.gray)
            }
            
            Spacer()
        }
        .padding()
    }
}

#Preview {
    TitleView()
        .environmentObject(GameState())
}
