import SwiftUI

struct ContentView: View {
    @EnvironmentObject var gameState: GameState
    
    var body: some View {
        ZStack {
            // CM01-style dark background with subtle grid
            LinearGradient(
                colors: [Color(red: 0.05, green: 0.08, blue: 0.12),
                         Color(red: 0.08, green: 0.12, blue: 0.18)],
                startPoint: .top,
                endPoint: .bottom
            )
            .ignoresSafeArea()
            
            // Grid overlay for tactical feel
            GeometryReader { geo in
                Path { path in
                    let spacing = 20.0
                    for x in stride(from: 0, through: geo.size.width, by: spacing) {
                        path.move(to: CGPoint(x: x, y: 0))
                        path.addLine(to: CGPoint(x: x, y: geo.size.height))
                    }
                    for y in stride(from: 0, through: geo.size.height, by: spacing) {
                        path.move(to: CGPoint(x: 0, y: y))
                        path.addLine(to: CGPoint(x: geo.size.width, y: y))
                    }
                }
                .stroke(Color.green.opacity(0.03), lineWidth: 0.5)
            }
            .ignoresSafeArea()
            
            switch gameState.currentScreen {
            case .title:
                TitleView()
            case .squadBuilder:
                SquadBuilderView()
            case .formationSelect:
                FormationSelectView()
            case .match:
                MatchView()
            case .campaignComplete:
                CampaignCompleteView()
            }
        }
    }
}

#Preview {
    ContentView()
        .environmentObject(GameState())
}
