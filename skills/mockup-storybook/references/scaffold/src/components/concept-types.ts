/** The concept index `scripts/gen-concept.ts` writes to `src/generated/concept.json`. */
export interface StoryRef { title: string; name: string }
export interface ConceptCriterion { id: string; label: string; ears?: string }
export interface ConceptLink { id: string; title?: string; stage?: string; story?: StoryRef }
export interface ConceptFeature {
  spec: string            // '05_features/<fs>/<slug>.md', the key everything joins on
  slug: string; featureset: string
  featuresetPurpose?: string; outcome?: string; priority?: string; framing?: string
  permissions: Record<string, string[]>
  scope: string[]; criteria: ConceptCriterion[]
  screens: ConceptLink[]; journeys: ConceptLink[]
}
export interface ConceptScreen { id: string; title?: string; purpose?: string; features: string[] /* spec paths */ }
export interface Concept { features: ConceptFeature[]; screens: Record<string, ConceptScreen> }
