import SwiftUI

struct SynergyListView: View {
    let synergies: [SynergyCard]
    @Environment(\.dismiss) var dismiss
    
    var rarityColor: (String) -> Color = { rarity in
        switch rarity {
        case "common": return .gray
        case "uncommon": return .green
        case "rare": return .purple
        default: return .gray
        }
    }
    
    var body: some View {
        VStack(spacing: 0) {
            // Header
            VStack(spacing: 8) {
                Text("ROUND SYNERGIES")
                    .font(.system(size: 18, weight: .bold, design: .monospaced))
                    .foregroundColor(.yellow)
                
                Text("\(synergies.count) active this round")
                    .font(.system(size: 12, design: .monospaced))
                    .foregroundColor(.gray)
            }
            .padding()
            .background(Color.black.opacity(0.3))
            
            // Synergy list
            ScrollView {
                LazyVStack(spacing: 10) {
                    ForEach(synergies) { syn in
                        VStack(alignment: .leading, spacing: 6) {
                            HStack {
                                Text("⚡")
                                    .font(.system(size: 12))
                                
                                Text(syn.name)
                                    .font(.system(size: 14, weight: .bold, design: .monospaced))
                                    .foregroundColor(rarityColor(syn.rarity))
                                
                                Spacer()
                                
                                Text(syn.rarity.uppercased())
                                    .font(.system(size: 9, weight: .bold, design: .monospaced))
                                    .foregroundColor(rarityColor(syn.rarity))
                                    .padding(.horizontal, 6)
                                    .padding(.vertical, 2)
                                    .background(rarityColor(syn.rarity).opacity(0.2))
                                    .cornerRadius(3)
                            }
                            
                            Text(syn.description)
                                .font(.system(size: 11, design: .monospaced))
                                .foregroundColor(.gray)
                                .fixedSize(horizontal: false, vertical: true)
                        }
                        .padding(10)
                        .background(Color.yellow.opacity(0.05))
                        .cornerRadius(6)
                        .overlay(
                            RoundedRectangle(cornerRadius: 6)
                                .stroke(rarityColor(syn.rarity).opacity(0.3), lineWidth: 1)
                        )
                    }
                }
                .padding()
            }
            
            // Close button
            Button(action: { dismiss() }) {
                Text("CLOSE")
                    .font(.system(size: 14, design: .monospaced))
                    .foregroundColor(.gray)
                    .padding()
            }
        }
        .background(
            LinearGradient(
                colors: [Color(red: 0.05, green: 0.08, blue: 0.12),
                         Color(red: 0.08, green: 0.12, blue: 0.18)],
                startPoint: .top,
                endPoint: .bottom
            )
            .ignoresSafeArea()
        )
    }
}

#Preview {
    SynergyListView(synergies: [])
}
