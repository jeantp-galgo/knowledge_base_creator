# Análisis: Por qué el pipeline no genera buenas bases de conocimiento

**Fecha:** 2026-04-09  
**Contexto:** Comparación entre output del pipeline (testing.ipynb) vs Gemini Web — el pipeline produce outputs vacíos ("Sin datos suficientes") mientras que Gemini web produce KBs ricas y detalladas.

---

## Diagnóstico raíz

### 1. Una sola búsqueda vs. Deep Research

El scraper hace una **única interacción** con búsqueda grounded:

```python
interaction = self.client.interactions.create(
    model='gemini-3-pro-preview',
    input=prompt,
    tools=[{'type': 'google_search'}]
)
```

Gemini en la web (Deep Research) hace **10 a 30+ rondas de búsqueda iterativas**, lee páginas completas, sigue links y sintetiza progresivamente. No es el mismo modelo con el mismo prompt — es un proceso fundamentalmente diferente.

### 2. El pipeline actúa como embudo destructor de datos

```
Scraper encuentra 3-5 experiencias
    → Validator descarta las que no coinciden con la ficha o son "incierto"
        → Writer recibe 1-2 experiencias
            → Output: "Sin datos suficientes" en casi todo
```

Para modelos con poca actividad en foros locales (ej: Bajaj Pulsar N 250 en México), el scraper encuentra pocas experiencias mexicanas. El validator las descarta porque el país no coincide con la ficha. El writer recibe una sola experiencia válida y produce un output vacío.

**Contraste:** El output de Colombia (TVS Raider 125) es excelente NO porque el pipeline sea bueno, sino porque ese modelo tiene mucha actividad en foros colombianos — el scraper encontró suficientes experiencias para que el pipeline funcionara.

### 3. El writer tiene prohibido usar lo que sabe

La `knowledge_base_template.md` dice:
> "Tu fuente exclusiva de contenido son las EXPERIENCIAS VALIDADAS. No complementes con conocimiento general ni con búsquedas adicionales."

Con 1 experiencia válida → output vacío. Aunque Gemini conoce perfectamente el modelo, tiene prohibido usarlo.

### 4. El validator descarta experiencias válidas

El validator filtra experiencias de otros países aunque sean del mismo modelo. Para motos con poca presencia en foros locales, las experiencias de India, Colombia o Argentina sobre la misma moto son relevantes (el motor es el mismo). Esas experiencias se descartan en lugar de incluirse con etiqueta.

---

## Soluciones propuestas

### Opción A: Prompt único tipo "Deep Research" ⭐ Recomendada a largo plazo

En lugar del pipeline de 4 pasos, **un solo llamado** donde Gemini tiene libertad de investigar iterativamente y luego sintetizar:

```python
prompt = f"""
Eres un investigador especializado en motocicletas. Realiza una investigación profunda 
sobre la {brand} {model} en {country}.

PROCESO DE INVESTIGACIÓN (hazlo en orden):
1. Busca: "{model} {country} opiniones usuarios"
2. Busca: "{model} {country} foro experiencia"
3. Busca: "{brand} {model} review propietario"
4. Busca: "{model} problemas comunes"
5. Busca: "{model} vs [competidores]"
6. Si hay poca info específica de {country}, busca info general del modelo 
   y señala explícitamente qué aplica al mercado general vs. al país específico.

Con TODO lo encontrado, genera la base de conocimiento en el formato:
[SEGMENTO], [SENTIMIENTO], [SENSACIONES], etc.
"""
```

Replica lo que hace Gemini web: múltiples búsquedas en un solo contexto, síntesis progresiva, sin filtros que descarten datos intermedios.

### Opción B: Múltiples llamadas al scraper con queries distintas ⭐ Recomendada a corto plazo

Mantener el pipeline pero correr el scraper 4-6 veces con queries diferentes antes de la validación:

```python
queries = [
    f"{model} {country} opiniones",
    f"{model} {country} foro experiencia usuario",
    f"{brand} {model} review propietario",
    f"{model} problemas comunes",
    f"{model} vs honda yamaha",  # comparaciones
]

todas_experiencias = []
for query in queries:
    scraper = ScraperAgent(..., title=query)
    result = scraper.scrape()
    todas_experiencias.extend(result.get("experiencias_usuarios", []))

# Luego pasar todas al validator
```

Cambio mínimo al código existente, puede triplicar la cantidad de experiencias disponibles.

### Opción C: Relajar el validator

Cambiar la lógica del validator para **incluir** experiencias de otros países con una etiqueta de contexto, en lugar de descartarlas. El motor de una Pulsar N 250 es el mismo en México, India o Colombia — esas experiencias son válidas con la advertencia correspondiente.

---

## Resumen ejecutivo

| Problema | Causa | Solución |
|---|---|---|
| Output vacío en mercados pequeños | Pocas experiencias locales + validator que descarta | Opción B o C |
| Output nunca tan bueno como Gemini web | Una búsqueda vs. 30 búsquedas iterativas | Opción A |
| Pipeline funciona bien solo con CO | Solo Colombia tiene volumen suficiente de datos | Todas las opciones |

**Conclusión:** El pipeline multi-paso tiene sentido cuando hay datos abundantes para filtrar. Para mercados con poca actividad online, el approach de "deja que Gemini investigue libremente" (Opción A) es superior y produce resultados comparables a Gemini web.

---

## Archivos clave revisados en este análisis

- `notebooks/testing.ipynb` — Flujo principal de 4 pasos
- `src/core/scraper_agent.py` — Una sola búsqueda grounded
- `src/core/validator_agent.py` — Filtra por país estrictamente
- `src/core/writer_agent.py` — Solo usa experiencias validadas, sin búsqueda propia
- `src/core/gemini_processor.py` — `interactions.create` con una sola llamada
- `src/data/input/prompts/knowledge_base_template.md` — Prohíbe usar conocimiento general
- `src/data/output/gemini/MX-Bajaj_Pulsar N 250-knowledge_base.md` — Ejemplo de output malo
- `src/data/output/gemini/test/2026-01-23-CO-knowledge_base_final.md` — Ejemplo de output bueno (CO)
