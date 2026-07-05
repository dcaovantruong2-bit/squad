import Foundation

struct FormationCard: Identifiable, Codable, Hashable {
    let id: String
    let name: String
    let slots: [String]
    let handSize: Int
    let globalMult: Double
    let positionBonus: [String: Int]
    let description: String
}
