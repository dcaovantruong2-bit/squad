import Foundation

class DataLoader {
    static let shared = DataLoader()
    
    func loadPlayers() -> [PlayerCard] {
        guard let url = Bundle.main.url(forResource: "players", withExtension: "json"),
              let data = try? Data(contentsOf: url),
              let decoded = try? JSONDecoder().decode([PlayerCardDTO].self, from: data) else {
            return Self.defaultPlayers()
        }
        return decoded.map { $0.toPlayerCard() }
    }
    
    func loadSynergies() -> [SynergyCard] {
        guard let url = Bundle.main.url(forResource: "synergies", withExtension: "json"),
              let data = try? Data(contentsOf: url),
              let decoded = try? JSONDecoder().decode([SynergyCardDTO].self, from: data) else {
            return Self.defaultSynergies()
        }
        return decoded.map { $0.toSynergyCard() }
    }
    
    func loadFormations() -> [FormationCard] {
        return Self.defaultFormations()
    }
    
    func loadPhases() -> [Phase] {
        return Self.defaultPhases()
    }
    
    // MARK: - Default Data (embedded)
    
    static func defaultPlayers() -> [PlayerCard] {
        return [
            // GK
            PlayerCard(id: "gk1", name: "H. Lloris", position: "GK", atk: 2, pac: 5, pas: 7, def: 9, spc: 7, traits: ["leader"], description: "Veteran keeper"),
            PlayerCard(id: "gk2", name: "K. Navas", position: "GK", atk: 1, pac: 6, pas: 5, def: 8, spc: 8, traits: ["reflex"], description: "Quick reflexes"),
            // CB
            PlayerCard(id: "cb1", name: "V. van Dijk", position: "CB", atk: 4, pac: 6, pas: 6, def: 10, spc: 5, traits: ["physical", "leader"], description: "Dominant defender"),
            PlayerCard(id: "cb2", name: "R. Araújo", position: "CB", atk: 3, pac: 7, pas: 5, def: 9, spc: 4, traits: ["physical"], description: "Strong tackler"),
            PlayerCard(id: "cb3", name: "M. de Ligt", position: "CB", atk: 4, pac: 5, pas: 7, def: 8, spc: 5, traits: ["technical"], description: "Ball-playing CB"),
            PlayerCard(id: "cb4", name: "A. Bastoni", position: "CB", atk: 3, pac: 5, pas: 8, def: 8, spc: 5, traits: ["technical"], description: "Left-footed CB"),
            PlayerCard(id: "cb5", name: "W. Saliba", position: "CB", atk: 2, pac: 7, pas: 6, def: 9, spc: 4, traits: ["pacey"], description: "Athletic defender"),
            // FB
            PlayerCard(id: "fb1", name: "A. Robertson", position: "FB", atk: 5, pac: 8, pas: 8, def: 7, spc: 5, traits: ["pacey", "crosser"], description: "Overlapping left-back"),
            PlayerCard(id: "fb2", name: "K. Trippier", position: "FB", atk: 4, pac: 6, pas: 9, def: 7, spc: 8, traits: ["crosser", "technical"], description: "Set-piece specialist"),
            PlayerCard(id: "fb3", name: "J. Koundé", position: "FB", atk: 4, pac: 8, pas: 6, def: 8, spc: 5, traits: ["pacey", "physical"], description: "Versatile defender"),
            PlayerCard(id: "fb4", name: "T. Alexander-Arnold", position: "FB", atk: 5, pac: 6, pas: 10, def: 5, spc: 8, traits: ["crosser", "technical"], description: "Playmaker from deep"),
            // CDM
            PlayerCard(id: "cdm1", name: "C. Casemiro", position: "CDM", atk: 5, pac: 5, pas: 7, def: 9, spc: 5, traits: ["physical", "leader"], description: "Defensive anchor"),
            PlayerCard(id: "cdm2", name: "R. Fernández", position: "CDM", atk: 5, pac: 6, pas: 8, def: 7, spc: 6, traits: ["technical"], description: "Box-to-box"),
            PlayerCard(id: "cdm3", name: "D. Rice", position: "CDM", atk: 5, pac: 6, pas: 7, def: 8, spc: 5, traits: ["physical", "leader"], description: "Complete midfielder"),
            // CM
            PlayerCard(id: "cm1", name: "K. De Bruyne", position: "CM", atk: 8, pac: 6, pas: 10, def: 4, spc: 9, traits: ["technical", "visionary"], description: "Master playmaker"),
            PlayerCard(id: "cm2", name: "L. Modric", position: "CM", atk: 6, pac: 5, pas: 10, def: 5, spc: 9, traits: ["technical", "visionary"], description: "Maestro"),
            PlayerCard(id: "cm3", name: "Pedri", position: "CM", atk: 6, pac: 6, pas: 9, def: 5, spc: 8, traits: ["technical"], description: "Young talent"),
            PlayerCard(id: "cm4", name: "F. Valverde", position: "CM", atk: 7, pac: 8, pas: 7, def: 6, spc: 5, traits: ["pacey", "physical"], description: "Engine room"),
            PlayerCard(id: "cm5", name: "J. Bellingham", position: "CM", atk: 8, pac: 7, pas: 7, def: 5, spc: 7, traits: ["physical", "technical"], description: "Complete midfielder"),
            // CAM
            PlayerCard(id: "cam1", name: "Bruno Fernandes", position: "CAM", atk: 8, pac: 5, pas: 9, def: 4, spc: 8, traits: ["technical", "visionary"], description: "Creative force"),
            PlayerCard(id: "cam2", name: "M. Ødegaard", position: "CAM", atk: 7, pac: 6, pas: 9, def: 4, spc: 8, traits: ["technical", "visionary"], description: "Playmaker"),
            // LW
            PlayerCard(id: "lw1", name: "V. Júnior", position: "LW", atk: 9, pac: 9, pas: 7, def: 2, spc: 8, traits: ["pacey", "technical", "dribbler"], description: "Electric winger"),
            PlayerCard(id: "lw2", name: "R. Sterling", position: "LW", atk: 7, pac: 9, pas: 6, def: 3, spc: 6, traits: ["pacey", "dribbler"], description: "Quick and direct"),
            PlayerCard(id: "lw3", name: "L. Sané", position: "LW", atk: 7, pac: 9, pas: 7, def: 3, spc: 7, traits: ["pacey", "technical"], description: "Pacey winger"),
            // RW
            PlayerCard(id: "rw1", name: "M. Salah", position: "RW", atk: 10, pac: 8, pas: 7, def: 3, spc: 8, traits: ["clinical", "pacey"], description: "Goal machine"),
            PlayerCard(id: "rw2", name: "B. Saka", position: "RW", atk: 8, pac: 8, pas: 7, def: 4, spc: 7, traits: ["technical", "pacey"], description: "Rising star"),
            PlayerCard(id: "rw3", name: "Rodrygo", position: "RW", atk: 8, pac: 8, pas: 6, def: 3, spc: 7, traits: ["technical", "clinical"], description: "Clinical finisher"),
            // ST
            PlayerCard(id: "st1", name: "E. Haaland", position: "ST", atk: 10, pac: 8, pas: 4, def: 3, spc: 6, traits: ["physical", "clinical"], description: "Goal machine"),
            PlayerCard(id: "st2", name: "K. Mbappé", position: "ST", atk: 9, pac: 10, pas: 6, def: 3, spc: 7, traits: ["pacey", "clinical"], description: "Lightning fast"),
            PlayerCard(id: "st3", name: "H. Kane", position: "ST", atk: 9, pac: 5, pas: 8, def: 4, spc: 7, traits: ["clinical", "technical"], description: "Complete striker"),
            PlayerCard(id: "st4", name: "R. Lewandowski", position: "ST", atk: 9, pac: 5, pas: 7, def: 3, spc: 8, traits: ["clinical", "technical"], description: "Veteran poacher"),
        ]
    }
    
    static func defaultFormations() -> [FormationCard] {
        return [
            FormationCard(id: "4-4-2", name: "4-4-2", slots: ["CB", "CB", "FB", "FB", "CM", "CM", "ST", "ST"],
                         handSize: 11, globalMult: 1.0, positionBonus: [:],
                         description: "Balanced. No frills. Classic."),
            FormationCard(id: "4-3-3", name: "4-3-3", slots: ["CB", "CB", "FB", "FB", "CDM", "CM", "CM", "LW", "RW", "ST"],
                         handSize: 12, globalMult: 1.0, positionBonus: ["LW": 20, "RW": 20, "ST": -15, "CDM": -10],
                         description: "Wingers thrive (+20), ST and CDM stretched."),
            FormationCard(id: "5-3-2", name: "5-3-2", slots: ["CB", "CB", "CB", "FB", "FB", "CM", "CM", "CDM", "ST", "ST"],
                         handSize: 11, globalMult: 1.0, positionBonus: ["CB": 25, "FB": 12, "LW": -20, "RW": -20],
                         description: "Defence wins. CBs+25, FBs+12."),
            FormationCard(id: "3-4-3", name: "3-4-3", slots: ["CB", "CB", "FB", "FB", "CM", "CM", "LW", "RW", "ST", "ST"],
                         handSize: 12, globalMult: 1.0, positionBonus: ["ST": 20, "LW": 15, "RW": 15, "CB": -25],
                         description: "All-out attack. Attackers boosted, CBs exposed."),
            FormationCard(id: "4-2-3-1", name: "4-2-3-1", slots: ["CB", "CB", "FB", "FB", "CM", "CM", "CAM", "LW", "RW", "ST"],
                         handSize: 12, globalMult: 1.0, positionBonus: ["CM": 10, "CAM": 25, "ST": -15],
                         description: "Possession. CAM+25, CM+10."),
            FormationCard(id: "4-5-1", name: "4-5-1", slots: ["CB", "CB", "FB", "FB", "CDM", "CM", "CM", "LW", "RW", "ST"],
                         handSize: 12, globalMult: 1.0, positionBonus: ["CDM": 15, "LW": 20, "RW": 20, "ST": -20, "CB": -5],
                         description: "Counter. CDM+15, wingers+20."),
        ]
    }
    
    static func defaultPhases() -> [Phase] {
        return [
            Phase(id: "goal_kick", name: "Goal Kick",
                  slots: [.position("GK"), .statBased(as: "CB", minAtk: nil, minPac: nil, minPas: nil, minDef: 7, minSpc: nil, trait: nil),
                          .statBased(as: "CB", minAtk: nil, minPac: nil, minPas: nil, minDef: 6, minSpc: nil, trait: nil)],
                  weight: "DEF", maxCards: 3, description: "Keeper launches long — best defenders win the header"),
            Phase(id: "build_up", name: "Build-Up",
                  slots: [.statBased(as: "FB", minAtk: nil, minPac: nil, minPas: 6, minDef: nil, minSpc: nil, trait: nil),
                          .statBased(as: "FB", minAtk: nil, minPac: nil, minPas: 6, minDef: nil, minSpc: nil, trait: nil),
                          .statBased(as: "CM", minAtk: nil, minPac: nil, minPas: 7, minDef: nil, minSpc: nil, trait: nil)],
                  weight: "PAS", maxCards: 3, description: "Play out from the back — any good passer can step up"),
            Phase(id: "wing_attack", name: "Wing Attack",
                  slots: [.statBased(as: "FB", minAtk: nil, minPac: 7, minPas: nil, minDef: nil, minSpc: nil, trait: nil),
                          .statBased(as: "LW", minAtk: nil, minPac: 7, minPas: nil, minDef: nil, minSpc: nil, trait: nil)],
                  weight: "PAC", maxCards: 2, description: "Overlap and cross — pace wins"),
            Phase(id: "long_ball", name: "Long Ball",
                  slots: [.statBased(as: "CB", minAtk: nil, minPac: 5, minPas: nil, minDef: 6, minSpc: nil, trait: nil),
                          .statBased(as: "ST", minAtk: 6, minPac: nil, minPas: nil, minDef: nil, minSpc: nil, trait: nil)],
                  weight: "ATK", maxCards: 2, description: "Bypass midfield — best attackers chase it down"),
            Phase(id: "defensive_block", name: "Defensive Block",
                  slots: [.statBased(as: "CB", minAtk: nil, minPac: nil, minPas: nil, minDef: 8, minSpc: nil, trait: nil),
                          .statBased(as: "CB", minAtk: nil, minPac: nil, minPas: nil, minDef: 7, minSpc: nil, trait: nil),
                          .statBased(as: "CDM", minAtk: nil, minPac: nil, minPas: nil, minDef: 6, minSpc: nil, trait: nil)],
                  weight: "DEF", maxCards: 3, description: "Park the bus — your toughest players"),
            Phase(id: "tiki_taka", name: "Tiki-Taka",
                  slots: [.statBased(as: "CM", minAtk: nil, minPac: nil, minPas: 8, minDef: nil, minSpc: nil, trait: nil),
                          .statBased(as: "CM", minAtk: nil, minPac: nil, minPas: 7, minDef: nil, minSpc: nil, trait: nil),
                          .statBased(as: "CM", minAtk: nil, minPac: nil, minPas: 6, minDef: nil, minSpc: nil, trait: nil)],
                  weight: "PAS", maxCards: 3, description: "Pass, pass, pass — best passers control the game"),
            Phase(id: "counter_attack", name: "Counter-Attack",
                  slots: [.statBased(as: "LW", minAtk: nil, minPac: 7, minPas: nil, minDef: nil, minSpc: nil, trait: nil),
                          .statBased(as: "ST", minAtk: 7, minPac: nil, minPas: nil, minDef: nil, minSpc: nil, trait: nil),
                          .statBased(as: "RW", minAtk: nil, minPac: 7, minPas: nil, minDef: nil, minSpc: nil, trait: nil)],
                  weight: "PAC", maxCards: 3, description: "Explosive break — pacey wingers stretch the defence"),
            Phase(id: "set_piece", name: "Set Piece",
                  slots: [.statBased(as: "CAM", minAtk: nil, minPac: nil, minPas: nil, minDef: nil, minSpc: 7, trait: nil),
                          .statBased(as: "ST", minAtk: 7, minPac: nil, minPas: nil, minDef: nil, minSpc: nil, trait: "physical")],
                  weight: "SPC", maxCards: 2, description: "Corner or free kick — specialist delivery meets a physical target"),
            Phase(id: "high_press", name: "High Press",
                  slots: [.statBased(as: "ST", minAtk: nil, minPac: 7, minPas: nil, minDef: nil, minSpc: nil, trait: nil),
                          .statBased(as: "RW", minAtk: nil, minPac: 7, minPas: nil, minDef: nil, minSpc: nil, trait: nil),
                          .statBased(as: "CM", minAtk: nil, minPac: 6, minPas: nil, minDef: nil, minSpc: nil, trait: nil)],
                  weight: "PAC", maxCards: 3, description: "Suffocate the opponent — all three need pace"),
            Phase(id: "through_ball", name: "Through Ball",
                  slots: [.statBased(as: "CM", minAtk: nil, minPac: nil, minPas: 7, minDef: nil, minSpc: nil, trait: nil),
                          .statBased(as: "ST", minAtk: nil, minPac: 7, minPas: nil, minDef: nil, minSpc: nil, trait: nil)],
                  weight: "ATK", maxCards: 2, description: "One pass unlocks the defence — passer meets pace"),
            Phase(id: "wingback_push", name: "Wingback Push",
                  slots: [.statBased(as: "FB", minAtk: nil, minPac: 7, minPas: nil, minDef: nil, minSpc: nil, trait: nil),
                          .statBased(as: "LW", minAtk: nil, minPac: nil, minPas: 6, minDef: nil, minSpc: nil, trait: nil)],
                  weight: "PAC", maxCards: 2, description: "Fullback bombs forward to combine with the winger"),
        ]
    }
    
    static func defaultSynergies() -> [SynergyCard] {
        return [
            // Phase-specific synergies
            SynergyCard(id: "clean_sheet", name: "Clean Sheet", rarity: "common",
                       triggerType: "clean_sheet",
                       trigger: ["pos_a": AnyCodable("GK"), "pos_b": AnyCodable("CB"), "stat": AnyCodable("def_"), "threshold": AnyCodable(16)],
                       altTrigger: nil, effectType: "add",
                       effect: ["add_chips": AnyCodable(30)],
                       description: "GK+CB DEF≥16: both +30 chips", persistent: false),
            SynergyCard(id: "organised_defence", name: "Organised Defence", rarity: "common",
                       triggerType: "organised_defence",
                       trigger: ["positions": AnyCodable(["CB"]), "stat": AnyCodable("def_"), "threshold": AnyCodable(17)],
                       altTrigger: nil, effectType: "add",
                       effect: ["add_chips": AnyCodable(25)],
                       description: "2 CBs DEF sum≥17: both +25 chips", persistent: false),
            SynergyCard(id: "wingback_overlap_syn", name: "Wingback Overlap", rarity: "uncommon",
                       triggerType: "wingback_overlap",
                       trigger: ["pos_a": AnyCodable("FB"), "stat_a": AnyCodable("pac"), "pos_b": AnyCodable("CM"), "stat_b": AnyCodable("pas"), "threshold": AnyCodable(15)],
                       altTrigger: nil, effectType: "add",
                       effect: ["add_chips": AnyCodable(20)],
                       description: "FB PAC + CM PAS≥15: both +20 chips", persistent: false),
            SynergyCard(id: "stretch_backline", name: "Stretch the Backline", rarity: "uncommon",
                       triggerType: "stretch_backline",
                       trigger: ["pos_a": AnyCodable("FB"), "stat_a": AnyCodable("pac"), "pos_b": AnyCodable("LW"), "stat_b": AnyCodable("pac"), "threshold": AnyCodable(16)],
                       altTrigger: nil, effectType: "multiply",
                       effect: ["multiply": AnyCodable(1.3)],
                       description: "FB PAC + LW PAC≥16: both ×1.3", persistent: false),
            SynergyCard(id: "route_one", name: "Route One", rarity: "common",
                       triggerType: "route_one",
                       trigger: ["pos_a": AnyCodable("CB"), "stat_a": AnyCodable("pas"), "pos_b": AnyCodable("ST"), "stat_b": AnyCodable("pac"), "threshold": AnyCodable(14)],
                       altTrigger: nil, effectType: "add",
                       effect: ["add_chips": AnyCodable(35), "target": AnyCodable("ST")],
                       description: "CB PAS + ST PAC≥14: ST +35 chips", persistent: false),
            SynergyCard(id: "battering_ram", name: "Battering Ram", rarity: "uncommon",
                       triggerType: "battering_ram",
                       trigger: ["pos_a": AnyCodable("CB"), "stat_a": AnyCodable("def_"), "pos_b": AnyCodable("ST"), "stat_b": AnyCodable("atk"), "threshold": AnyCodable(17)],
                       altTrigger: nil, effectType: "add",
                       effect: ["add_chips": AnyCodable(30)],
                       description: "CB DEF + ST ATK≥17: both +30 chips", persistent: false),
            SynergyCard(id: "midfield_engine", name: "Midfield Engine", rarity: "uncommon",
                       triggerType: "midfield_engine",
                       trigger: ["positions": AnyCodable(["CM"]), "stat_a": AnyCodable("pas"), "stat_b": AnyCodable("def_"), "threshold": AnyCodable(15)],
                       altTrigger: nil, effectType: "add",
                       effect: ["add_chips": AnyCodable(25)],
                       description: "2 CMs: best PAS + best DEF≥15: both +25", persistent: false),
            SynergyCard(id: "double_pivot", name: "Double Pivot", rarity: "rare",
                       triggerType: "double_pivot",
                       trigger: ["positions": AnyCodable(["CM"]), "stat": AnyCodable("pas"), "threshold": AnyCodable(17)],
                       altTrigger: nil, effectType: "carryover",
                       effect: ["add_chips": AnyCodable(40), "target_role": AnyCodable("attacker")],
                       description: "2 CMs PAS sum≥17: next phase first attacker +40", persistent: false),
            SynergyCard(id: "one_two", name: "One-Two", rarity: "uncommon",
                       triggerType: "one_two",
                       trigger: ["pos_a": AnyCodable("CM"), "stat_a": AnyCodable("pas"), "pos_b": AnyCodable("ST"), "stat_b": AnyCodable("pac"), "threshold": AnyCodable(15)],
                       altTrigger: nil, effectType: "multiply",
                       effect: ["multiply": AnyCodable(1.25)],
                       description: "CM PAS + ST PAC≥15: both ×1.25", persistent: false),
            SynergyCard(id: "near_post_flick", name: "Near Post Flick", rarity: "uncommon",
                       triggerType: "near_post_flick",
                       trigger: ["pos_a": AnyCodable("CAM"), "stat_a": AnyCodable("spc"), "pos_b": AnyCodable("ST"), "stat_b": AnyCodable("atk"), "threshold": AnyCodable(15)],
                       altTrigger: nil, effectType: "multiply",
                       effect: ["multiply": AnyCodable(1.3)],
                       description: "CAM SPC + ST ATK≥15: ST ×1.3", persistent: false),
            SynergyCard(id: "target_man_release", name: "Target Man Release", rarity: "rare",
                       triggerType: "target_man_release",
                       trigger: ["pos_a": AnyCodable("ST"), "stat_a": AnyCodable("atk"), "stat_b": AnyCodable("pac"), "threshold": AnyCodable(16), "winger_positions": AnyCodable(["LW", "RW"])],
                       altTrigger: nil, effectType: "multiply",
                       effect: ["multiply": AnyCodable(1.35)],
                       description: "ST ATK + best winger PAC≥16: winger ×1.35", persistent: false),
            SynergyCard(id: "covering_defender", name: "Covering Defender", rarity: "rare",
                       triggerType: "covering_defender",
                       trigger: ["position": AnyCodable("CB"), "stat_a": AnyCodable("pac"), "threshold_a": AnyCodable(7), "stat_b": AnyCodable("def_"), "threshold_b": AnyCodable(9)],
                       altTrigger: nil, effectType: "add",
                       effect: ["add_chips": AnyCodable(35)],
                       description: "2 CBs: one PAC≥7 + one DEF≥9: both +35", persistent: false),
            SynergyCard(id: "back_three", name: "Back Three", rarity: "rare",
                       triggerType: "back_three",
                       trigger: ["stat": AnyCodable("def_"), "threshold": AnyCodable(7)],
                       altTrigger: nil, effectType: "multiply",
                       effect: ["multiply": AnyCodable(1.2)],
                       description: "All 3 on field DEF≥7: everyone ×1.2", persistent: false),
            SynergyCard(id: "set_piece_threat", name: "Set Piece Threat", rarity: "uncommon",
                       triggerType: "set_piece_threat",
                       trigger: ["stat_a": AnyCodable("def_"), "threshold_a": AnyCodable(9), "stat_b": AnyCodable("spc"), "threshold_b": AnyCodable(8), "different_players": AnyCodable(true)],
                       altTrigger: nil, effectType: "global_add",
                       effect: ["add_chips": AnyCodable(50)],
                       description: "DEF≥9 + SPC≥8 (different players): +50 global", persistent: false),
            SynergyCard(id: "overlap_syn", name: "Overlap", rarity: "common",
                       triggerType: "overlap",
                       trigger: ["pos_a": AnyCodable("FB"), "stat_a": AnyCodable("pac"), "pos_b": AnyCodable("LW"), "stat_b": AnyCodable("pas"), "threshold": AnyCodable(15)],
                       altTrigger: nil, effectType: "multiply",
                       effect: ["multiply": AnyCodable(1.2)],
                       description: "FB PAC + LW PAS≥15: FB ×1.2", persistent: false),
            SynergyCard(id: "defensive_duo", name: "Defensive Duo", rarity: "common",
                       triggerType: "defensive_duo",
                       trigger: ["stat": AnyCodable("def_"), "threshold": AnyCodable(16)],
                       altTrigger: nil, effectType: "add",
                       effect: ["add_chips": AnyCodable(20)],
                       description: "2 highest DEF on field sum≥16: everyone +20", persistent: false),
            SynergyCard(id: "trio_syn", name: "Midfield Trio", rarity: "rare",
                       triggerType: "trio",
                       trigger: ["position": AnyCodable("CM"), "stat": AnyCodable("pas"), "threshold": AnyCodable(7)],
                       altTrigger: nil, effectType: "chain_multiply",
                       effect: ["multipliers": AnyCodable([1.3, 1.5, 1.3])],
                       description: "3 CMs all PAS≥7: chained multipliers", persistent: false),
            // Persistent (squad) synergies
            SynergyCard(id: "pace_squad", name: "Pace Merchants", rarity: "uncommon",
                       triggerType: "squad_trait_count",
                       trigger: ["trait": AnyCodable("pacey"), "min_count": AnyCodable(3)],
                       altTrigger: nil, effectType: "persistent_multiply",
                       effect: ["target_trait": AnyCodable("pacey"), "multiply": AnyCodable(1.1)],
                       description: "3+ pacey players: all pacey ×1.1", persistent: true),
            SynergyCard(id: "tech_squad", name: "Technical Masters", rarity: "uncommon",
                       triggerType: "squad_trait_count",
                       trigger: ["trait": AnyCodable("technical"), "min_count": AnyCodable(3)],
                       altTrigger: nil, effectType: "persistent_fatigue",
                       effect: ["fatigue_penalty": AnyCodable(0.6)],
                       description: "3+ technical: fatigue ×0.6 instead of ×0.7", persistent: true),
            SynergyCard(id: "leader_squad", name: "Leadership", rarity: "common",
                       triggerType: "squad_trait_present",
                       trigger: ["trait": AnyCodable("leader")],
                       altTrigger: nil, effectType: "persistent_add",
                       effect: ["target": AnyCodable("all"), "add_chips": AnyCodable(5)],
                       description: "Have a leader: all players +5 chips", persistent: true),
            SynergyCard(id: "journeyman", name: "Journeyman", rarity: "rare",
                       triggerType: "squad_trait_present",
                       trigger: ["trait": AnyCodable("versatile")],
                       altTrigger: nil, effectType: "persistent_special",
                       effect: ["special": AnyCodable("fatigue_reset")],
                       description: "Have a versatile player: once per match restore fatigue", persistent: true),
            SynergyCard(id: "clinical_finishers", name: "Clinical Finishers", rarity: "uncommon",
                       triggerType: "squad_trait_count",
                       trigger: ["trait": AnyCodable("clinical"), "min_count": AnyCodable(2)],
                       altTrigger: nil, effectType: "persistent_multiply",
                       effect: ["target_trait": AnyCodable("clinical"), "multiply": AnyCodable(1.15)],
                       description: "2+ clinical: all clinical ×1.15", persistent: true),
        ]
    }
}

// DTOs for JSON decoding
struct PlayerCardDTO: Codable {
    let id: String
    let name: String
    let position: String
    let atk: Int
    let pac: Int
    let pas: Int
    let def: Int
    let spc: Int
    let traits: [String]
    let description: String
    
    func toPlayerCard() -> PlayerCard {
        PlayerCard(id: id, name: name, position: position, atk: atk, pac: pac, pas: pas,
                  def: `def`, spc: spc, traits: traits, description: description)
    }
}

struct SynergyCardDTO: Codable {
    let id: String
    let name: String
    let rarity: String
    let triggerType: String
    let trigger: [String: AnyCodable]
    let altTrigger: [String: AnyCodable]?
    let effectType: String
    let effect: [String: AnyCodable]
    let description: String
    let persistent: Bool
    
    func toSynergyCard() -> SynergyCard {
        SynergyCard(id: id, name: name, rarity: rarity, triggerType: triggerType,
                   trigger: trigger, altTrigger: altTrigger, effectType: effectType,
                   effect: effect, description: description, persistent: persistent)
    }
}
