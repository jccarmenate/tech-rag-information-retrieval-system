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

## Licencia

MIT — ver [LICENSE](LICENSE).
