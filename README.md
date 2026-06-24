# CodeRadar

Sistema de Recuperación de Información (SRI) con Retrieval-Augmented Generation (RAG)
para el dominio de tecnología y software.

> Estado: en desarrollo inicial. Este README se irá ampliando a medida que avancen los
> módulos (adquisición, indexación, recuperación, RAG, ranking, interfaz, evaluación...).

## Idea

Buscar, indexar y sintetizar información técnica actual (repos de GitHub, discusiones de
Hacker News y Stack Overflow, artículos de Dev.to, papers de arXiv) y responder preguntas
del usuario con respuestas generadas por RAG, citando las fuentes recuperadas.

## Arquitectura (planeada)

El sistema se construye como un pipeline modular:

1. **Adquisición** — conectores contra APIs de GitHub, Hacker News, Dev.to, Stack Exchange
   y arXiv, con refresco periódico.
2. **Indexación** — índice invertido + TF-IDF propio sobre el corpus adquirido.
3. **Recuperación** — modelo de Redes de Inferencia Bayesianas (no un vectorial básico)
   sobre el índice.
4. **Base vectorial** — embeddings semánticos persistidos en ChromaDB, como segunda vía de
   recuperación y soporte del RAG.
5. **RAG** — combina evidencia de recuperación + vectorial para generar respuestas citadas,
   con proveedor de LLM intercambiable (Ollama local / Anthropic API).
6. **Posicionamiento** — fusiona señales (relevancia, similitud, recencia, feedback) para
   ordenar los resultados mostrados al usuario.
7. **Interfaz** — SPA en React donde se lanza la consulta y se visualizan resultados y
   respuesta generada.
8. **Búsqueda web** — fallback automático cuando el corpus local no cubre la consulta.
9. **Expansión y feedback** — mejora consultas y aprende de las señales de los usuarios.
10. **Multimodal** — incorpora imágenes asociadas a los documentos al espacio de búsqueda.
11. **Recomendación** — sugiere contenido relacionado según perfil e historial.
12. **Evaluación** — métricas clásicas de RI y de fidelidad del RAG.

Este documento se irá actualizando a medida que cada módulo quede implementado.

### Estado actual

- ✅ **Adquisición de datos**: conectores para GitHub, Hacker News, Dev.to, Stack Overflow
  y arXiv (`backend/app/acquisition/`), con deduplicación por URL, refresco periódico vía
  APScheduler y disparo manual en `POST /api/acquisition/refresh`.
- ✅ **Indexación**: índice invertido + TF-IDF propio (`backend/app/indexing/`),
  reconstruido automáticamente después de cada refresco de adquisición.
- ✅ **Recuperación (modelo no básico)**: Red de Inferencia Bayesiana
  (`backend/app/retrieval/inference_network.py`), expuesta en `GET /api/search`.
- ✅ **Base de datos vectorial**: ChromaDB persistente con embeddings de
  `sentence-transformers` (`backend/app/vectorstore/`); los documentos largos se
  fragmentan (`chunker.py`) antes de generar embeddings para no truncar contenido.
  `GET /api/search?mode=vector` usa esta vía en paralelo a la Red de Inferencia.
- ✅ **RAG**: pipeline propio (`backend/app/rag/`) que combina evidencia de ambos
  retrievers, genera una respuesta citada y extrae las citas usadas realmente en el
  texto. Proveedor de LLM intercambiable: Ollama local por defecto, Anthropic si hay
  `ANTHROPIC_API_KEY` configurada — sin tocar código (`GET /api/rag/answer`).
- ✅ **Posicionamiento**: `Ranker` (`backend/app/ranking/`) fusiona relevancia +
  recencia + autoridad de la fuente + retroalimentación del usuario para decidir el
  orden final mostrado en `GET /api/search`, sobre-muestreando candidatos antes de
  re-rankear.
- ✅ **Búsqueda web**: detección de insuficiencia multi-criterio (cantidad, calidad,
  cobertura) que activa un fallback a DuckDuckGo cuando el corpus local no alcanza;
  los resultados web se indexan y quedan disponibles para futuras consultas
  (`backend/app/web_search/`).
- ✅ **Expansión y retroalimentación**: expansión de consultas por pseudo-relevancia
  (Rocchio) y sinónimos (WordNet) en `GET /api/search?expand=true`
  (`backend/app/expansion/`), más `POST /api/feedback` (👍/👎) cuyo puntaje agregado
  alimenta al `Ranker`.

## Licencia

MIT — ver [LICENSE](LICENSE).
