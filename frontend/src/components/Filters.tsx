import type { RetrievalMode } from '../api/types'
import './Filters.css'

interface FiltersProps {
  mode: RetrievalMode
  onModeChange: (mode: RetrievalMode) => void
  expand: boolean
  onExpandChange: (expand: boolean) => void
}

export function Filters({ mode, onModeChange, expand, onExpandChange }: FiltersProps) {
  return (
    <div className="filters">
      <label className="filters__field">
        <span>Retrieval model</span>
        <select
          value={mode}
          onChange={(e) => onModeChange(e.target.value as RetrievalMode)}
        >
          <option value="inference_network">Bayesian Inference Network</option>
          <option value="vector">Vector (embeddings)</option>
        </select>
      </label>

      <label className="filters__checkbox">
        <input
          type="checkbox"
          checked={expand}
          onChange={(e) => onExpandChange(e.target.checked)}
        />
        <span>Expand query (Rocchio + WordNet)</span>
      </label>
    </div>
  )
}
