import Foundation

class MatchState: ObservableObject {
    @Published var squad: [PlayerCard]
    @Published var synergies: [SynergyCard]
    @Published var synergyPool: [SynergyCard]
    @Published var formation: FormationCard?
    @Published var opponentName: String
    @Published var roundTargets: [Int]
    @Published var currentRound: Int = 0
    @Published var roundsWon: Int = 0
    @Published var roundsLost: Int = 0
    
    @Published var phases: [Phase] = []
    @Published var currentPhaseIdx: Int = 0
    @Published var phaseResults: [[String: Any]] = []
    @Published var roundScore: Int = 0
    
    @Published var fatigue: [String: Double] = [:]
    @Published var field: [(PlayerCard, String)] = []
    @Published var carryover: [String: Any]? = nil
    @Published var persistentBuffs: [String: Any]? = nil
    @Published var journeymanUsed: Bool = false
    
    init(squad: [PlayerCard], synergies: [SynergyCard], opponentName: String = "FC Rivals",
         roundTargets: [Int] = [500, 650, 850], formation: FormationCard? = nil,
         persistentBuffs: [String: Any]? = nil, synergyPool: [SynergyCard] = []) {
        self.squad = squad
        self.synergies = synergies
        self.synergyPool = synergyPool
        self.opponentName = opponentName
        self.roundTargets = roundTargets
        self.formation = formation
        self.persistentBuffs = persistentBuffs
    }
    
    var roundsNeeded: Int { 2 }
    
    var isMatchOver: Bool {
        roundsWon >= roundsNeeded || roundsLost >= roundsNeeded
    }
    
    var isMatchWon: Bool {
        roundsWon >= roundsNeeded
    }
    
    var currentTarget: Int {
        currentRound < roundTargets.count ? roundTargets[currentRound] : 9999
    }
    
    var currentPhase: Phase? {
        currentPhaseIdx < phases.count ? phases[currentPhaseIdx] : nil
    }
    
    func getFatigue(_ playerId: String) -> Double {
        fatigue[playerId] ?? 1.0
    }
    
    func applyFatigue(_ playerId: String) {
        let penalty = (persistentBuffs?["fatigue_penalty"] as? Double) ?? 0.7
        let current = fatigue[playerId] ?? 1.0
        fatigue[playerId] = current * penalty
    }
}
