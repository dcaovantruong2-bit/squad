import Foundation
import SwiftUI

enum GameScreen {
    case title
    case squadBuilder
    case formationSelect
    case match
    case campaignComplete
}

class GameState: ObservableObject {
    @Published var currentScreen: GameScreen = .title
    @Published var allPlayers: [PlayerCard] = []
    @Published var allSynergies: [SynergyCard] = []
    @Published var allFormations: [FormationCard] = []
    @Published var allPhases: [Phase] = []
    
    @Published var selectedSquad: [PlayerCard] = []
    @Published var selectedFormation: FormationCard?
    @Published var persistentBuffs: [String: Any] = [:]
    
    @Published var currentMatch: MatchState?
    @Published var campaignMatchIndex: Int = 0
    @Published var campaignProgress: [Bool] = Array(repeating: false, count: 5)
    
    let budget = 360
    let minPlayers = 10
    
    let campaignMatches: [[String: Any]] = [
        ["name": "Group Stage", "opponent": "Wolves FC", "targets": [350, 450, 600], "tier": "Match 1/5 — Easy"],
        ["name": "Round of 16", "opponent": "Inter Your-Nan", "targets": [450, 580, 750], "tier": "Match 2/5 — Moderate"],
        ["name": "Quarter Final", "opponent": "Borussia Mönchen-flapjack", "targets": [550, 700, 880], "tier": "Match 3/5 — Challenging"],
        ["name": "Semi Final", "opponent": "Man City Oilers", "targets": [650, 800, 1050], "tier": "Match 4/5 — Elite"],
        ["name": "THE FINAL", "opponent": "Galácticos FC", "targets": [800, 950, 1200], "tier": "Match 5/5 — Final Boss"]
    ]
    
    init() {
        loadData()
    }
    
    func loadData() {
        let loader = DataLoader.shared
        allPlayers = loader.loadPlayers()
        allSynergies = loader.loadSynergies()
        allFormations = loader.loadFormations()
        allPhases = loader.loadPhases()
    }
    
    func startNewCampaign() {
        campaignMatchIndex = 0
        campaignProgress = Array(repeating: false, count: 5)
        currentScreen = .squadBuilder
    }
    
    func finalizeSquad() {
        currentScreen = .formationSelect
    }
    
    func selectFormation(_ formation: FormationCard) {
        selectedFormation = formation
        
        // Detect persistent synergies
        let allPersistent = allSynergies.filter { $0.persistent }
        persistentBuffs = ScoringEngine.detectSquadSynergies(squad: selectedSquad, synergyCards: allPersistent)
        
        currentScreen = .match
        startCampaignMatch()
    }
    
    func startCampaignMatch() {
        guard campaignMatchIndex < campaignMatches.count else {
            currentScreen = .campaignComplete
            return
        }
        
        let matchDef = campaignMatches[campaignMatchIndex]
        let opponent = matchDef["opponent"] as? String ?? "FC Rivals"
        let targets = matchDef["targets"] as? [Int] ?? [500, 650, 850]
        
        let phaseSynergyPool = allSynergies.filter { !$0.persistent }
        
        currentMatch = MatchState(
            squad: selectedSquad,
            synergies: [],
            opponentName: opponent,
            roundTargets: targets,
            formation: selectedFormation,
            persistentBuffs: persistentBuffs,
            synergyPool: phaseSynergyPool
        )
    }
    
    func matchWon() {
        campaignProgress[campaignMatchIndex] = true
        campaignMatchIndex += 1
        
        if campaignMatchIndex >= campaignMatches.count {
            currentScreen = .campaignComplete
        } else {
            startCampaignMatch()
        }
    }
    
    func matchLost() {
        // Campaign over
        currentScreen = .title
    }
    
    func resetToTitle() {
        currentScreen = .title
        selectedSquad = []
        selectedFormation = nil
        currentMatch = nil
        campaignMatchIndex = 0
        campaignProgress = Array(repeating: false, count: 5)
    }
}
