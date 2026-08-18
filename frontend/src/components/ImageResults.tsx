import type { ImageResultItem } from '../api/types'
import './ImageResults.css'

interface ImageResultsProps {
  results: ImageResultItem[]
}

export function ImageResults({ results }: ImageResultsProps) {
  if (results.length === 0) return null

  return (
    <section className="image-results">
      <h2 className="image-results__heading">Related images</h2>
      <div className="image-results__grid">
        {results.map((item) => (
          <a
            key={item.doc_id}
            href={item.url}
            target="_blank"
            rel="noreferrer"
            className="image-results__item"
            title={item.title}
          >
            <img src={item.image_url} alt={item.title} loading="lazy" />
          </a>
        ))}
      </div>
    </section>
  )
}
