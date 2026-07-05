import Foundation

struct ScoringEngine {
    // Position → Chips Formula
    static let chipsFormula: [String: (PlayerCard) -> Int] = [
        "ST":  { $0.atk * 3 + $0.pac * 2 + $0.spc * 1 },
        "LW":  { $0.atk * 2 + $0.pac * 3 + $0.pas * 1 },
        "RW":  { $0.atk * 2 + $0.pac * 3 + $0.pas * 1 },
        "CM":  { $0.pas * 3 + $0.atk * 1 + $0.def * 2 },
        "CAM": { $0.pas * 3 + $0.atk * 2 + $0.spc * 1 },
        "CDM": { $0.def * 3 + $0.pas * 2 + $0.atk * 1 },
        "CB":  { $0.def * 4 + $0.spc * 1 + $0.pac * 1 },
        "FB":  { $0.def * 2 + $0.pac * 3 + $0.pas * 1 },
        "GK":  { $0.def * 3 + $0.spc * 2 },
    ]
    
    static func calculateChips(_ player: PlayerCard, position: String) -> Int {
        return chipsFormula[position]?(player) ?? 0
    }
    
    static let attackerPositions: Set<String> = ["LW", "RW", "ST"]
    
    // MARK: - Synergy Detection
    
    static func detectSynergies(
        field: [(PlayerCard, String)],
        synergyCards: [SynergyCard]
    ) -> (playerEffects: [String: PlayerSynergyEffect], globalMult: Double, globalAdd: Int, nextCarryover: [String: Any]?) {
        var results: [String: PlayerSynergyEffect] = [:]
        for (player, _) in field {
            results[player.id] = PlayerSynergyEffect()
        }
        
        var globalMult = 1.0
        var globalAdd = 0
        var nextCarryover: [String: Any]? = nil
        
        for syn in synergyCards {
            if syn.persistent { continue }
            
            switch syn.triggerType {
            case "clean_sheet":
                let posA = syn.trigger["pos_a"]?.value as? String ?? ""
                let posB = syn.trigger["pos_b"]?.value as? String ?? ""
                let stat = syn.trigger["stat"]?.value as? String ?? ""
                let threshold = syn.trigger["threshold"]?.value as? Int ?? 0
                if let gk = bestAt(field, position: posA, stat: stat),
                   let cb = bestAt(field, position: posB, stat: stat) {
                    let total = statValue(gk, stat: stat) + statValue(cb, stat: stat)
                    if total >= threshold {
                        let addChips = syn.effect["add_chips"]?.value as? Int ?? 0
                        results[gk.id]?.addChips += addChips
                        results[gk.id]?.firedSynergies.append(syn.name)
                        results[cb.id]?.addChips += addChips
                        results[cb.id]?.firedSynergies.append(syn.name)
                    }
                }
                
            case "organised_defence":
                let positions = syn.trigger["positions"]?.value as? [String] ?? []
                let stat = syn.trigger["stat"]?.value as? String ?? ""
                let threshold = syn.trigger["threshold"]?.value as? Int ?? 0
                let cbs = playersAt(field, position: positions.first ?? "")
                if cbs.count >= 2 {
                    let sorted = cbs.sorted { statValue($0, stat: stat) > statValue($1, stat: stat) }
                    let total = statValue(sorted[0], stat: stat) + statValue(sorted[1], stat: stat)
                    if total >= threshold {
                        let addChips = syn.effect["add_chips"]?.value as? Int ?? 0
                        for p in [sorted[0], sorted[1]] {
                            results[p.id]?.addChips += addChips
                            results[p.id]?.firedSynergies.append(syn.name)
                        }
                    }
                }
                
            case "wingback_overlap":
                let posA = syn.trigger["pos_a"]?.value as? String ?? ""
                let statA = syn.trigger["stat_a"]?.value as? String ?? ""
                let posB = syn.trigger["pos_b"]?.value as? String ?? ""
                let statB = syn.trigger["stat_b"]?.value as? String ?? ""
                let threshold = syn.trigger["threshold"]?.value as? Int ?? 0
                if let fb = bestAt(field, position: posA, stat: statA),
                   let cm = bestAt(field, position: posB, stat: statB) {
                    let total = statValue(fb, stat: statA) + statValue(cm, stat: statB)
                    if total >= threshold {
                        let addChips = syn.effect["add_chips"]?.value as? Int ?? 0
                        results[fb.id]?.addChips += addChips
                        results[fb.id]?.firedSynergies.append(syn.name)
                        results[cm.id]?.addChips += addChips
                        results[cm.id]?.firedSynergies.append(syn.name)
                    }
                }
                
            case "stretch_backline":
                let posA = syn.trigger["pos_a"]?.value as? String ?? ""
                let statA = syn.trigger["stat_a"]?.value as? String ?? ""
                let posB = syn.trigger["pos_b"]?.value as? String ?? ""
                let statB = syn.trigger["stat_b"]?.value as? String ?? ""
                let threshold = syn.trigger["threshold"]?.value as? Int ?? 0
                if let fb = bestAt(field, position: posA, stat: statA),
                   let lw = bestAt(field, position: posB, stat: statB) {
                    let total = statValue(fb, stat: statA) + statValue(lw, stat: statB)
                    if total >= threshold {
                        let mult = syn.effect["multiply"]?.value as? Double ?? 1.0
                        results[fb.id]?.multiply *= mult
                        results[fb.id]?.firedSynergies.append(syn.name)
                        results[lw.id]?.multiply *= mult
                        results[lw.id]?.firedSynergies.append(syn.name)
                    }
                }
                
            case "route_one":
                let posA = syn.trigger["pos_a"]?.value as? String ?? ""
                let statA = syn.trigger["stat_a"]?.value as? String ?? ""
                let posB = syn.trigger["pos_b"]?.value as? String ?? ""
                let statB = syn.trigger["stat_b"]?.value as? String ?? ""
                let threshold = syn.trigger["threshold"]?.value as? Int ?? 0
                if let cb = bestAt(field, position: posA, stat: statA),
                   let st = bestAt(field, position: posB, stat: statB) {
                    let total = statValue(cb, stat: statA) + statValue(st, stat: statB)
                    if total >= threshold {
                        let addChips = syn.effect["add_chips"]?.value as? Int ?? 0
                        let target = syn.effect["target"]?.value as? String ?? "ST"
                        if target == "ST" {
                            results[st.id]?.addChips += addChips
                        }
                        results[st.id]?.firedSynergies.append(syn.name)
                        results[cb.id]?.firedSynergies.append(syn.name)
                    }
                }
                
            case "battering_ram":
                let posA = syn.trigger["pos_a"]?.value as? String ?? ""
                let statA = syn.trigger["stat_a"]?.value as? String ?? ""
                let posB = syn.trigger["pos_b"]?.value as? String ?? ""
                let statB = syn.trigger["stat_b"]?.value as? String ?? ""
                let threshold = syn.trigger["threshold"]?.value as? Int ?? 0
                if let cb = bestAt(field, position: posA, stat: statA),
                   let st = bestAt(field, position: posB, stat: statB) {
                    let total = statValue(cb, stat: statA) + statValue(st, stat: statB)
                    if total >= threshold {
                        let addChips = syn.effect["add_chips"]?.value as? Int ?? 0
                        results[cb.id]?.addChips += addChips
                        results[cb.id]?.firedSynergies.append(syn.name)
                        results[st.id]?.addChips += addChips
                        results[st.id]?.firedSynergies.append(syn.name)
                    }
                }
                
            case "midfield_engine":
                let positions = syn.trigger["positions"]?.value as? [String] ?? []
                let statA = syn.trigger["stat_a"]?.value as? String ?? ""
                let statB = syn.trigger["stat_b"]?.value as? String ?? ""
                let threshold = syn.trigger["threshold"]?.value as? Int ?? 0
                let cms = playersAt(field, position: positions.first ?? "")
                if cms.count >= 2 {
                    let bestPas = cms.max { statValue($0, stat: statA) < statValue($1, stat: statA) }
                    let remaining = cms.filter { $0.id != bestPas?.id }
                    let bestDef = remaining.max { statValue($0, stat: statB) < statValue($1, stat: statB) }
                    if let bp = bestPas, let bd = bestDef {
                        let total = statValue(bp, stat: statA) + statValue(bd, stat: statB)
                        if total >= threshold {
                            let addChips = syn.effect["add_chips"]?.value as? Int ?? 0
                            results[bp.id]?.addChips += addChips
                            results[bp.id]?.firedSynergies.append(syn.name)
                            results[bd.id]?.addChips += addChips
                            results[bd.id]?.firedSynergies.append(syn.name)
                        }
                    }
                }
                
            case "double_pivot":
                let positions = syn.trigger["positions"]?.value as? [String] ?? []
                let stat = syn.trigger["stat"]?.value as? String ?? ""
                let threshold = syn.trigger["threshold"]?.value as? Int ?? 0
                let cms = playersAt(field, position: positions.first ?? "")
                if cms.count >= 2 {
                    let sorted = cms.sorted { statValue($0, stat: stat) > statValue($1, stat: stat) }
                    let total = statValue(sorted[0], stat: stat) + statValue(sorted[1], stat: stat)
                    if total >= threshold {
                        nextCarryover = [
                            "type": "double_pivot",
                            "source_synergy": syn.name,
                            "add_chips": syn.effect["add_chips"]?.value as? Int ?? 40,
                            "target_role": syn.effect["target_role"]?.value as? String ?? "attacker"
                        ]
                        for p in [sorted[0], sorted[1]] {
                            results[p.id]?.firedSynergies.append(syn.name)
                        }
                    }
                }
                
            case "one_two":
                let posA = syn.trigger["pos_a"]?.value as? String ?? ""
                let statA = syn.trigger["stat_a"]?.value as? String ?? ""
                let posB = syn.trigger["pos_b"]?.value as? String ?? ""
                let statB = syn.trigger["stat_b"]?.value as? String ?? ""
                let threshold = syn.trigger["threshold"]?.value as? Int ?? 0
                if let cm = bestAt(field, position: posA, stat: statA),
                   let st = bestAt(field, position: posB, stat: statB) {
                    let total = statValue(cm, stat: statA) + statValue(st, stat: statB)
                    if total >= threshold {
                        let mult = syn.effect["multiply"]?.value as? Double ?? 1.0
                        results[cm.id]?.multiply *= mult
                        results[cm.id]?.firedSynergies.append(syn.name)
                        results[st.id]?.multiply *= mult
                        results[st.id]?.firedSynergies.append(syn.name)
                    }
                }
                
            case "near_post_flick":
                let posA = syn.trigger["pos_a"]?.value as? String ?? ""
                let statA = syn.trigger["stat_a"]?.value as? String ?? ""
                let posB = syn.trigger["pos_b"]?.value as? String ?? ""
                let statB = syn.trigger["stat_b"]?.value as? String ?? ""
                let threshold = syn.trigger["threshold"]?.value as? Int ?? 0
                if let cam = bestAt(field, position: posA, stat: statA),
                   let st = bestAt(field, position: posB, stat: statB) {
                    let total = statValue(cam, stat: statA) + statValue(st, stat: statB)
                    if total >= threshold {
                        let mult = syn.effect["multiply"]?.value as? Double ?? 1.0
                        results[st.id]?.multiply *= mult
                        results[st.id]?.firedSynergies.append(syn.name)
                        results[cam.id]?.firedSynergies.append(syn.name)
                    }
                }
                
            case "target_man_release":
                let posA = syn.trigger["pos_a"]?.value as? String ?? ""
                let statA = syn.trigger["stat_a"]?.value as? String ?? ""
                let statB = syn.trigger["stat_b"]?.value as? String ?? ""
                let threshold = syn.trigger["threshold"]?.value as? Int ?? 0
                let wingerPositions = syn.trigger["winger_positions"]?.value as? [String] ?? ["LW", "RW"]
                let st = bestAt(field, position: posA, stat: statA)
                let wingers = field.filter { wingerPositions.contains($0.1) }.map { $0.0 }
                if let st = st, !wingers.isEmpty {
                    let bestWinger = wingers.max { statValue($0, stat: statB) < statValue($1, stat: statB) }
                    if let bw = bestWinger {
                        let total = statValue(st, stat: statA) + statValue(bw, stat: statB)
                        if total >= threshold {
                            let mult = syn.effect["multiply"]?.value as? Double ?? 1.0
                            results[bw.id]?.multiply *= mult
                            results[bw.id]?.firedSynergies.append(syn.name)
                            results[st.id]?.firedSynergies.append(syn.name)
                        }
                    }
                }
                
            case "covering_defender":
                let position = syn.trigger["position"]?.value as? String ?? ""
                let statA = syn.trigger["stat_a"]?.value as? String ?? ""
                let thresholdA = syn.trigger["threshold_a"]?.value as? Int ?? 0
                let statB = syn.trigger["stat_b"]?.value as? String ?? ""
                let thresholdB = syn.trigger["threshold_b"]?.value as? Int ?? 0
                let cbs = playersAt(field, position: position)
                if cbs.count >= 2 {
                    let pacCBs = cbs.filter { statValue($0, stat: statA) >= thresholdA }
                    let defCBs = cbs.filter { statValue($0, stat: statB) >= thresholdB }
                    if !pacCBs.isEmpty && !defCBs.isEmpty {
                        for fastP in pacCBs {
                            for strongP in defCBs where fastP.id != strongP.id {
                                let addChips = syn.effect["add_chips"]?.value as? Int ?? 0
                                results[fastP.id]?.addChips += addChips
                                results[fastP.id]?.firedSynergies.append(syn.name)
                                results[strongP.id]?.addChips += addChips
                                results[strongP.id]?.firedSynergies.append(syn.name)
                                break
                            }
                            if !results.values.filter({ $0.firedSynergies.contains(syn.name) }).isEmpty { break }
                        }
                    }
                }
                
            case "back_three":
                let stat = syn.trigger["stat"]?.value as? String ?? ""
                let threshold = syn.trigger["threshold"]?.value as? Int ?? 0
                let players = field.map { $0.0 }
                if players.count >= 3 && players.allSatisfy({ statValue($0, stat: stat) >= threshold }) {
                    let mult = syn.effect["multiply"]?.value as? Double ?? 1.0
                    for p in players {
                        results[p.id]?.multiply *= mult
                        results[p.id]?.firedSynergies.append(syn.name)
                    }
                }
                
            case "set_piece_threat":
                let statA = syn.trigger["stat_a"]?.value as? String ?? ""
                let thresholdA = syn.trigger["threshold_a"]?.value as? Int ?? 0
                let statB = syn.trigger["stat_b"]?.value as? String ?? ""
                let thresholdB = syn.trigger["threshold_b"]?.value as? Int ?? 0
                let players = field.map { $0.0 }
                let defPlayers = players.filter { statValue($0, stat: statA) >= thresholdA }
                let spcPlayers = players.filter { statValue($0, stat: statB) >= thresholdB }
                if !defPlayers.isEmpty && !spcPlayers.isEmpty {
                    for dp in defPlayers {
                        for sp in spcPlayers where dp.id != sp.id {
                            let addChips = syn.effect["add_chips"]?.value as? Int ?? 0
                            globalAdd += addChips
                            for p in players {
                                results[p.id]?.firedSynergies.append(syn.name)
                            }
                            break
                        }
                        if globalAdd > 0 { break }
                    }
                }
                
            case "overlap":
                let posA = syn.trigger["pos_a"]?.value as? String ?? ""
                let statA = syn.trigger["stat_a"]?.value as? String ?? ""
                let posB = syn.trigger["pos_b"]?.value as? String ?? ""
                let statB = syn.trigger["stat_b"]?.value as? String ?? ""
                let threshold = syn.trigger["threshold"]?.value as? Int ?? 0
                if let fb = bestAt(field, position: posA, stat: statA),
                   let lw = bestAt(field, position: posB, stat: statB) {
                    let total = statValue(fb, stat: statA) + statValue(lw, stat: statB)
                    if total >= threshold {
                        let mult = syn.effect["multiply"]?.value as? Double ?? 1.0
                        results[fb.id]?.multiply *= mult
                        results[fb.id]?.firedSynergies.append(syn.name)
                        results[lw.id]?.firedSynergies.append(syn.name)
                    }
                }
                
            case "defensive_duo":
                let stat = syn.trigger["stat"]?.value as? String ?? ""
                let threshold = syn.trigger["threshold"]?.value as? Int ?? 0
                let players = field.map { $0.0 }
                if players.count >= 2 {
                    let sorted = players.sorted { statValue($0, stat: stat) > statValue($1, stat: stat) }
                    let total = statValue(sorted[0], stat: stat) + statValue(sorted[1], stat: stat)
                    if total >= threshold {
                        let addChips = syn.effect["add_chips"]?.value as? Int ?? 0
                        for p in players {
                            results[p.id]?.addChips += addChips
                            results[p.id]?.firedSynergies.append(syn.name)
                        }
                    }
                }
                
            case "trio":
                let position = syn.trigger["position"]?.value as? String ?? ""
                let stat = syn.trigger["stat"]?.value as? String ?? ""
                let threshold = syn.trigger["threshold"]?.value as? Int ?? 0
                let cms = playersAt(field, position: position)
                if cms.count >= 3 && cms.allSatisfy({ statValue($0, stat: stat) >= threshold }) {
                    let sorted = cms.sorted { statValue($0, stat: stat) > statValue($1, stat: stat) }
                    let mults = syn.effect["multipliers"]?.value as? [Double] ?? [1.3, 1.5, 1.3]
                    for (i, p) in sorted.enumerated() {
                        let multIdx = min(i, mults.count - 1)
                        results[p.id]?.multiply *= mults[multIdx]
                        results[p.id]?.firedSynergies.append("\(syn.name) (×\(mults[multIdx]))")
                    }
                }
                
            default:
                break
            }
        }
        
        return (results, globalMult, globalAdd, nextCarryover)
    }
    
    // MARK: - Full Round Score
    
    static func calculateRoundScore(
        field: [(PlayerCard, String)],
        synergyCards: [SynergyCard],
        formation: FormationCard? = nil,
        fatigue: [String: Double] = [:],
        carryover: [String: Any]? = nil,
        persistentBuffs: [String: Any]? = nil
    ) -> ScoreResult {
        let pb = persistentBuffs ?? [:]
        
        var synergyResult = detectSynergies(field: field, synergyCards: synergyCards)
        var playerEffects = synergyResult.playerEffects
        var globalMult = synergyResult.globalMult
        var globalAdd = synergyResult.globalAdd
        let nextCarryover = synergyResult.nextCarryover
        
        // Apply carryover
        if let carryover = carryover {
            let targetRole = carryover["target_role"] as? String ?? "attacker"
            let sourceName = carryover["source_synergy"] as? String ?? "Carryover"
            let bonusChips = carryover["add_chips"] as? Int ?? 0
            
            if targetRole == "attacker" {
                for (player, pos) in field where attackerPositions.contains(pos) {
                    if playerEffects[player.id] == nil {
                        playerEffects[player.id] = PlayerSynergyEffect()
                    }
                    playerEffects[player.id]?.addChips += bonusChips
                    playerEffects[player.id]?.firedSynergies.append("\(sourceName) (carryover)")
                    break
                }
            }
        }
        
        // Apply persistent buffs
        let combinedGlobalMult = globalMult * ((pb["global_mult"] as? Double) ?? 1.0)
        let combinedGlobalAdd = globalAdd + ((pb["global_add"] as? Int) ?? 0)
        
        let persistentNames = pb["fired_synergies"] as? [String] ?? []
        for (player, _) in field {
            if let mult = (pb["player_mult"] as? [String: Double])?[player.id] {
                playerEffects[player.id]?.multiply *= mult
            }
            if let add = (pb["player_add"] as? [String: Int])?[player.id] {
                playerEffects[player.id]?.addChips += add
            }
        }
        
        for (player, pos) in field {
            let posMult = (pb["position_mult"] as? [String: Double])?[pos] ?? 1.0
            let posAdd = (pb["position_add"] as? [String: Int])?[pos] ?? 0
            if posMult != 1.0 || posAdd != 0 {
                playerEffects[player.id]?.multiply *= posMult
                playerEffects[player.id]?.addChips += posAdd
            }
        }
        
        for name in persistentNames {
            for pid in playerEffects.keys {
                playerEffects[pid]?.firedSynergies.append("\(name) (persistent)")
            }
        }
        
        // Build contributors map
        var synergyContributors: [String: [String]] = [:]
        for (player, pos) in field {
            if let effect = playerEffects[player.id] {
                for rawName in effect.firedSynergies {
                    let cleanName = String(rawName.split(separator: " (").first ?? Substring(rawName))
                    let entry = "\(player.name) [\(pos)]"
                    if synergyContributors[cleanName] == nil {
                        synergyContributors[cleanName] = []
                    }
                    if !synergyContributors[cleanName]!.contains(entry) {
                        synergyContributors[cleanName]!.append(entry)
                    }
                }
            }
        }
        
        // Build synergy descriptions
        var synergyDescriptions: [String: String] = [:]
        let allFired = Set(playerEffects.values.flatMap { $0.firedSynergies })
        for syn in synergyCards {
            if allFired.contains(syn.name) || persistentNames.contains(syn.name) {
                synergyDescriptions[syn.name] = syn.description
            }
        }
        
        let formationMult = formation?.globalMult ?? 1.0
        
        var breakdown: [ScoreBreakdownEntry] = []
        var total: Double = 0
        
        for (player, pos) in field {
            var baseChips = calculateChips(player, position: pos)
            baseChips += formation?.positionBonus[pos] ?? 0
            
            let playerSyn = playerEffects[player.id] ?? PlayerSynergyEffect()
            let fatigueMult = fatigue[player.id] ?? 1.0
            
            let chipsWithBonus = baseChips + playerSyn.addChips
            let afterMult = Double(chipsWithBonus) * playerSyn.multiply * fatigueMult
            
            breakdown.append(ScoreBreakdownEntry(
                player: player.name,
                position: pos,
                baseChips: baseChips,
                addChips: playerSyn.addChips,
                multiply: round(playerSyn.multiply * 100) / 100,
                fatigue: round(fatigueMult * 100) / 100,
                subtotal: Int(afterMult.rounded())
            ))
            total += afterMult
        }
        
        let subtotalBeforeGlobals = Int(total)
        total = total * combinedGlobalMult + Double(combinedGlobalAdd)
        let finalTotal = Int((total * formationMult).rounded())
        
        let firedSynergies = Array(Set(playerEffects.values.flatMap { $0.firedSynergies })).sorted()
        
        return ScoreResult(
            total: finalTotal,
            breakdown: breakdown,
            subtotalBeforeGlobals: subtotalBeforeGlobals,
            formationMult: formationMult,
            formationName: formation?.name ?? "",
            globalMult: round(combinedGlobalMult * 1000) / 1000,
            globalAdd: combinedGlobalAdd,
            firedSynergies: firedSynergies,
            nextCarryover: nextCarryover,
            synergyContributors: synergyContributors,
            synergyDescriptions: synergyDescriptions
        )
    }
    
    // MARK: - Synergy Preview
    
    static func computeSynergyPreview(
        player: PlayerCard,
        fieldPosition: String,
        currentField: [(PlayerCard, String)],
        synergies: [SynergyCard]
    ) -> Set<String> {
        let currentResult = detectSynergies(field: currentField, synergyCards: synergies)
        let currentFired = getFiredSynergyNames(playerEffects: currentResult.playerEffects)
        
        var newField = currentField
        newField.append((player, fieldPosition))
        let newResult = detectSynergies(field: newField, synergyCards: synergies)
        let newFired = getFiredSynergyNames(playerEffects: newResult.playerEffects)
        
        return newFired.subtracting(currentFired)
    }
    
    static func getFiredSynergyNames(playerEffects: [String: PlayerSynergyEffect]) -> Set<String> {
        var fired = Set<String>()
        for (_, stats) in playerEffects {
            for rawName in stats.firedSynergies {
                let clean = String(rawName.split(separator: " (").first ?? Substring(rawName))
                fired.insert(clean)
            }
        }
        return fired
    }
    
    // MARK: - Squad-Persistent Synergy Detection
    
    static func detectSquadSynergies(
        squad: [PlayerCard],
        synergyCards: [SynergyCard]
    ) -> [String: Any] {
        var buffs: [String: Any] = [
            "fatigue_penalty": 0.7,
            "player_mult": [String: Double](),
            "player_add": [String: Int](),
            "position_mult": [String: Double](),
            "position_add": [String: Int](),
            "global_mult": 1.0,
            "global_add": 0,
            "journeyman_available": false,
            "fired_synergies": [String]()
        ]
        
        var traitToPlayers: [String: [PlayerCard]] = [:]
        for p in squad {
            for t in p.traits {
                if traitToPlayers[t] == nil { traitToPlayers[t] = [] }
                traitToPlayers[t]!.append(p)
            }
        }
        
        var firedSynergies: [String] = []
        
        for syn in synergyCards where syn.persistent {
            let triggered: Bool
            var matchingPlayers: [PlayerCard] = []
            
            switch syn.triggerType {
            case "squad_trait_count":
                let trait = syn.trigger["trait"]?.value as? String ?? ""
                let minCount = syn.trigger["min_count"]?.value as? Int ?? 1
                matchingPlayers = traitToPlayers[trait] ?? []
                triggered = matchingPlayers.count >= minCount
            case "squad_trait_present":
                let trait = syn.trigger["trait"]?.value as? String ?? ""
                matchingPlayers = traitToPlayers[trait] ?? []
                triggered = !matchingPlayers.isEmpty
            case "squad_trait_combo":
                let requiredTraits = syn.trigger["traits"]?.value as? [String] ?? []
                let minCount = syn.trigger["min_count"]?.value as? Int ?? 1
                matchingPlayers = squad.filter { p in requiredTraits.allSatisfy { p.traits.contains($0) } }
                triggered = matchingPlayers.count >= minCount
            default:
                triggered = false
            }
            
            if triggered {
                firedSynergies.append(syn.name)
                applyPersistentEffect(&buffs, syn: syn, matchingPlayers: matchingPlayers, squad: squad)
            }
        }
        
        buffs["fired_synergies"] = firedSynergies
        return buffs
    }
    
    private static func applyPersistentEffect(_ buffs: inout [String: Any], syn: SynergyCard,
                                               matchingPlayers: [PlayerCard], squad: [PlayerCard]) {
        let eff = syn.effect
        let etype = syn.effectType
        
        if etype == "persistent_fatigue" {
            if let penalty = eff["fatigue_penalty"]?.value as? Double {
                buffs["fatigue_penalty"] = penalty
            }
        } else if etype == "persistent_multiply" {
            let mult = eff["multiply"]?.value as? Double ?? 1.0
            if let targetTrait = eff["target_trait"]?.value as? String {
                var playerMult = buffs["player_mult"] as? [String: Double] ?? [:]
                for p in squad where p.traits.contains(targetTrait) {
                    let current = playerMult[p.id] ?? 1.0
                    playerMult[p.id] = current * mult
                }
                buffs["player_mult"] = playerMult
            }
            if let targetPositions = eff["target_position"]?.value as? [String] {
                var posMult = buffs["position_mult"] as? [String: Double] ?? [:]
                for pos in targetPositions {
                    let current = posMult[pos] ?? 1.0
                    posMult[pos] = current * mult
                }
                buffs["position_mult"] = posMult
            }
        } else if etype == "persistent_add" {
            let chips = eff["add_chips"]?.value as? Int ?? 0
            if eff["target"]?.value as? String == "all" {
                buffs["global_add"] = ((buffs["global_add"] as? Int) ?? 0) + chips
            }
            if let targetPositions = eff["target_position"]?.value as? [String] {
                var posAdd = buffs["position_add"] as? [String: Int] ?? [:]
                for pos in targetPositions {
                    posAdd[pos] = (posAdd[pos] ?? 0) + chips
                }
                buffs["position_add"] = posAdd
            }
        } else if etype == "persistent_special" {
            if eff["special"]?.value as? String == "fatigue_reset" {
                buffs["journeyman_available"] = true
            }
        }
    }
    
    // MARK: - Helpers
    
    private static func playersAt(_ field: [(PlayerCard, String)], position: String) -> [PlayerCard] {
        return field.filter { $0.1 == position }.map { $0.0 }
    }
    
    private static func bestAt(_ field: [(PlayerCard, String)], position: String, stat: String) -> PlayerCard? {
        let candidates = playersAt(field, position: position)
        return candidates.max { statValue($0, stat: stat) < statValue($1, stat: stat) }
    }
    
    static func statValue(_ player: PlayerCard, stat: String) -> Int {
        switch stat {
        case "atk": return player.atk
        case "pac": return player.pac
        case "pas": return player.pas
        case "def_": return player.def
        case "def": return player.def
        case "spc": return player.spc
        default: return 0
        }
    }
}

// MARK: - Supporting Types

struct PlayerSynergyEffect {
    var multiply: Double = 1.0
    var addChips: Int = 0
    var firedSynergies: [String] = []
}

struct ScoreBreakdownEntry {
    let player: String
    let position: String
    let baseChips: Int
    let addChips: Int
    let multiply: Double
    let fatigue: Double
    let subtotal: Int
}

struct ScoreResult {
    let total: Int
    let breakdown: [ScoreBreakdownEntry]
    let subtotalBeforeGlobals: Int
    let formationMult: Double
    let formationName: String
    let globalMult: Double
    let globalAdd: Int
    let firedSynergies: [String]
    let nextCarryover: [String: Any]?
    let synergyContributors: [String: [String]]
    let synergyDescriptions: [String: String]
}
