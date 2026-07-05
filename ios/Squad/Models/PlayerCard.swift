import Foundation

struct PlayerCard: Identifiable, Codable, Hashable {
    let id: String
    let name: String
    let position: String  // ST, RW, LW, CM, CDM, CB, FB, GK
    let atk: Int       // 1-10
    let pac: Int       // 1-10
    let pas: Int       // 1-10
    let def: Int       // 1-10 (def_)
    let spc: Int       // 1-10 (special)
    var traits: [String]
    let description: String
    
    var cost: Int {
        atk + pac + pas + `def` + spc
    }
    
    func hasTrait(_ trait: String) -> Bool {
        traits.contains(trait)
    }
}
