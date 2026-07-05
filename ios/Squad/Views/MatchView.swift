import SwiftUI

struct MatchView: View {
    @EnvironmentObject var gameState: GameState
    @State private var showingPhaseResult = false
    @State private var currentPhaseResult: ScoreResult?
    
    var body: some View {
        VStack(spacing: 0) {
            if let match = gameState.currentMatch {
                // Match header
                matchHeaderView(match: match)
                
                // Campaign bracket
                campaignBracketView
                
                // Main content
                if let phase = match.currentPhase {
                    if showingPhaseResult && currentPhaseResult != nil {
                        PhaseResultView(result: currentPhaseResult!) {
                            showingPhaseResult = false
                            advanceToNextPhase()
                        }
                    } else {
                        PhasePlacementView(phase: phase, match: match) { result in
                            currentPhaseResult = result
                            showingPhaseResult = true
                        }
                    }
                } else {
                    RoundResultView(match: match) {
                        advanceToNextRound()
                    }
                }
            }
        }
    }
    
    func matchHeaderView(match: MatchState) -> some View {
        let matchDef = gameState.campaignMatches[gameState.campaignMatchIndex]
        
        return VStack(spacing: 8) {
            HStack {
                VStack(alignment: .leading, spacing: 2) {
                    Text(matchDef["name"] as? String ?? "Match")
                        .font(.system(size: 16, weight: .bold, design: .monospaced))
                        .foregroundColor(.green)
                    Text("vs \(match.opponentName)")
                        .font(.system(size: 12, design: .monospaced))
                        .foregroundColor(.gray)
                }
                
                Spacer()
                
                VStack(alignment: .trailing, spacing: 2) {
                    Text("Round \(match.currentRound + 1)/3")
                        .font(.system(size: 12, weight: .bold, design: .monospaced))
                        .foregroundColor(.cyan)
                    Text("\(match.roundsWon)-\(match.roundsLost)")
                        .font(.system(size: 14, weight: .bold, design: .monospaced))
                        .foregroundColor(.white)
                }
            }
            
            // Target
            HStack {
                Text("Target: \(match.currentTarget)")
                    .font(.system(size: 11, design: .monospaced))
                    .foregroundColor(.yellow)
                Spacer()
                Text("Score: \(match.roundScore)")
                    .font(.system(size: 11, design: .monospaced))
                    .foregroundColor(.green)
            }
        }
        .padding()
        .background(Color.black.opacity(0.3))
    }
    
    var campaignBracketView: some View {
        HStack(spacing: 8) {
            ForEach(0..<5) { index in
                VStack(spacing: 2) {
                    Text(["GS", "R16", "QF", "SF", "FN"][index])
                        .font(.system(size: 9, weight: .bold, design: .monospaced))
                        .foregroundColor(.gray)
                    
                    Circle()
                        .fill(index < gameState.campaignMatchIndex ? Color.green :
                              index == gameState.campaignMatchIndex ? Color.yellow : Color.gray.opacity(0.3))
                        .frame(width: 12, height: 12)
                }
                
                if index < 4 {
                    Rectangle()
                        .fill(Color.gray.opacity(0.3))
                        .frame(height: 1)
                }
            }
        }
        .padding(.horizontal)
        .padding(.vertical, 8)
        .background(Color.black.opacity(0.2))
    }
    
    func advanceToNextPhase() {
        guard let match = gameState.currentMatch else { return }
        
        if match.currentPhaseIdx >= match.phases.count - 1 {
            // Round complete
            let won = match.roundScore >= match.currentTarget
            if won {
                match.roundsWon += 1
            } else {
                match.roundsLost += 1
            }
            showingPhaseResult = false
            currentPhaseResult = nil
        } else {
            match.currentPhaseIdx += 1
            match.field = []
        }
    }
    
    func advanceToNextRound() {
        guard let match = gameState.currentMatch else { return }
        
        if match.isMatchOver {
            if match.isMatchWon {
                gameState.matchWon()
            } else {
                gameState.matchLost()
            }
        } else {
            match.currentRound += 1
            startNewRound()
        }
    }
    
    func startNewRound() {
        guard let match = gameState.currentMatch else { return }
        
        // Shuffle phases
        match.phases = Array(DataLoader.shared.loadPhases().shuffled().prefix(6))
        match.currentPhaseIdx = 0
        match.fatigue = [:]
        match.phaseResults = []
        match.roundScore = 0
        match.field = []
        match.carryover = nil
        
        // Re-sample synergies
        if !match.synergyPool.isEmpty {
            match.synergies = Array(match.synergyPool.shuffled().prefix(5))
        }
    }
}

#Preview {
    MatchView()
        .environmentObject(GameState())
}
