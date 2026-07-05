import Foundation

enum SlotSpec: Codable, Hashable {
    case position(String)
    case positions([String])
    case statBased(as: String, minAtk: Int?, minPac: Int?, minPas: Int?, minDef: Int?, minSpc: Int?, trait: String?)
    
    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        if let pos = try? container.decode(String.self) {
            self = .position(pos)
        } else if let positions = try? container.decode([String].self) {
            self = .positions(positions)
        } else if let dict = try? container.decode([String: AnyCodable].self) {
            let asPos = dict["as"]?.value as? String ?? ""
            let minAtk = dict["min_atk"]?.value as? Int
            let minPac = dict["min_pac"]?.value as? Int
            let minPas = dict["min_pas"]?.value as? Int
            let minDef = dict["min_def"]?.value as? Int
            let minSpc = dict["min_spc"]?.value as? Int
            let trait = dict["trait"]?.value as? String
            self = .statBased(as: asPos, minAtk: minAtk, minPac: minPac, minPas: minPas, minDef: minDef, minSpc: minSpc, trait: trait)
        } else {
            throw DecodingError.dataCorruptedError(in: container, debugDescription: "Invalid SlotSpec")
        }
    }
    
    func encode(to encoder: Encoder) throws {
        var container = encoder.singleValueContainer()
        switch self {
        case .position(let pos):
            try container.encode(pos)
        case .positions(let positions):
            try container.encode(positions)
        case .statBased(let asPos, let minAtk, let minPac, let minPas, let minDef, let minSpc, let trait):
            var dict: [String: Any] = ["as": asPos]
            if let v = minAtk { dict["min_atk"] = v }
            if let v = minPac { dict["min_pac"] = v }
            if let v = minPas { dict["min_pas"] = v }
            if let v = minDef { dict["min_def"] = v }
            if let v = minSpc { dict["min_spc"] = v }
            if let v = trait { dict["trait"] = v }
            try container.encode(dict.mapValues { AnyCodable($0) })
        }
    }
}

struct Phase: Identifiable, Codable {
    let id: String
    let name: String
    let slots: [SlotSpec]
    let weight: String  // DEF, PAS, PAC, ATK, SPC
    let maxCards: Int
    let description: String
}
