import { useState } from 'react'
import { askRag, search, searchImages } from './api/client'
import type { Citation, ImageResultItem, RetrievalMode, SearchResultItem } from './api/types'
import { Filters } from './components/Filters'
import { ImageResults } from './components/ImageResults'
import { RagAnswerPanel } from './components/RagAnswerPanel'
import { RecommendationsPanel } from './components/RecommendationsPanel'
import { ResultsList } from './components/ResultsList'
import { SearchBar } from './components/SearchBar'
import { useUserId } from './hooks/useUserId'
import './App.css'

export default function App() {
  const userId = useUserId()

  const [query, setQuery] = useState('')
  const [mode, setMode] = useState<RetrievalMode>('inference_network')
  const [expand, setExpand] = useState(false)

  const [results, setResults] = useState<SearchResultItem[]>([])
  const [usedWebFallback, setUsedWebFallback] = useState(false)
  const [answer, setAnswer] = useState('')
  const [citations, setCitations] = useState<Citation[]>([])
  const [images, setImages] = useState<ImageResultItem[]>([])

  const [searching, setSearching] = useState(false)
  const [answering, setAnswering] = useState(false)
  const [hasSearched, setHasSearched] = useState(false)
  const [recommendationsKey, setRecommendationsKey] = useState(0)

  async function handleSearch(nextQuery: string) {
    setQuery(nextQuery)
    setHasSearched(true)
    setSearching(true)
    setAnswering(true)

    search({ q: nextQuery, mode, expand })
      .then((res) => {
        setResults(res.results)
        setUsedWebFallback(res.used_web_fallback)
      })
      .catch(() => setResults([]))
      .finally(() => setSearching(false))

    askRag(nextQuery)
      .then((res) => {
        setAnswer(res.answer)
        setCitations(res.citations)
      })
      .catch(() => setAnswer(''))
      .finally(() => setAnswering(false))

    searchImages(nextQuery)
      .then((res) => setImages(res.results))
      .catch(() => setImages([]))
  }

  return (
    <div className="app">
      <header className="app__header">
        <h1 className="app__logo">Tech RAG Information Retrieval System</h1>
        <p className="app__tagline">
          Search + Retrieval-Augmented Generation over GitHub, Hacker News, Dev.to, Stack
          Overflow and arXiv
        </p>
      </header>

      <div className="app__search-area">
        <SearchBar onSearch={handleSearch} loading={searching || answering} />
        <Filters mode={mode} onModeChange={setMode} expand={expand} onExpandChange={setExpand} />
      </div>

      {hasSearched && (
        <div className="app__layout">
          <main className="app__main">
            <RagAnswerPanel answer={answer} citations={citations} loading={answering} />
            <ImageResults results={images} />
            <ResultsList
              results={results}
              query={query}
              userId={userId}
              usedWebFallback={usedWebFallback}
              onVoted={() => setRecommendationsKey((k) => k + 1)}
            />
          </main>

          <RecommendationsPanel userId={userId} refreshKey={recommendationsKey} />
        </div>
      )}
    </div>
  )
}
