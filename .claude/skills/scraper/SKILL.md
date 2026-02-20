---
name: scraper
description: Este skill debe usarse cuando se recolectan experiencias reales de usuarios sobre un modelo específico de motocicleta. Construye un prompt para Gemini con Google Search para recopilar reseñas vivenciales, publicaciones en foros y opiniones de usuarios, retornando un JSON estructurado.
---

# Skill: Scraper - Recolección de Experiencias de Usuarios

## Objetivo

Recolectar experiencias reales y vivenciales de usuarios sobre la motocicleta especificada. Tu trabajo es construir un prompt preciso para Gemini que capture cómo se **siente** vivir con la moto y cómo la **perciben** los usuarios, priorizando sensaciones, emociones y experiencias vividas sobre descripciones técnicas.

---

## Contexto de Uso

Eres llamado por el Orchestrator con los siguientes parámetros:

- `marca`: Marca de la motocicleta
- `modelo`: Modelo específico
- `año`: Año del modelo
- `pais`: País del mercado
- `tipo`: Tipo de motocicleta
- `excluded_data`: (Opcional) Lista de datos a excluir en retries
- `failed_sources`: (Opcional) Lista de URLs/fuentes que fallaron validación

---

## Proceso de Recolección

### Paso 1: Construir el Prompt para Gemini

Construye un prompt completo que incluya:

1. **Contexto de búsqueda**: marca, modelo, año, país, tipo
2. **Qué priorizar**: las categorías de experiencias definidas en la sección siguiente
3. **Fuentes a buscar**: grupos Facebook, YouTube, foros, MercadoLibre, blogs en el país
4. **Exclusiones**: si `excluded_data` o `failed_sources` están presentes, instrúyele a Gemini que los evite
5. **El schema JSON exacto** que debe retornar (ver sección Formato de Salida)
6. **Las restricciones críticas** de recolección

El prompt debe cerrar con una instrucción explícita:
> "Retorna ÚNICAMENTE JSON válido. Sin texto adicional antes ni después. Sin bloques markdown."

### Paso 2: Ejecutar el Script

**Ubicación del script**: `.claude/skills/scraper/scripts/scraper_fetch.py`

El script recibe el prompt construido, lo ejecuta en Gemini con `google_search` y maneja la validación del JSON y los reintentos automáticamente.

**Cómo ejecutarlo**:
1. Escribe el prompt en un archivo JSON temporal:
```json
{ "prompt": "<el prompt completo que construiste>" }
```
2. Ejecuta el script directamente:
```bash
python .claude/skills/scraper/scripts/scraper_fetch.py input_scraper.json output_scraper.json
```
3. Lee el resultado desde `output_scraper.json`.

El script reintenta hasta 3 veces si el JSON es inválido. Si falla en todos los intentos, retorna:
```json
{"experiencias_usuarios": [], "error": "No se pudo obtener JSON valido..."}
```

### Paso 3: Verificar el Output

Antes de pasar el resultado al Orchestrator, verifica:

- `"error"` no está presente en el resultado
- `"experiencias_usuarios"` no está vacío
- Al menos una experiencia tiene `extractos_relevantes` con objetos anidados (no strings)

Si el output es inválido o vacío, reportarlo al Orchestrator para que decida si reintenta.

---

## Qué Priorizar en la Recolección

Incluye estas prioridades en el prompt que construyes para Gemini:

### 1. Experiencias Vivenciales (Prioridad Máxima)

- **Sensaciones de manejo**: estabilidad percibida, vibraciones, confianza al frenar, respuesta del acelerador, postura y comodidad
- **Problemas o dolores recurrentes**: fallas, defectos, inconvenientes reportados con contexto (clima, altura, tipo de uso)
- **Motivaciones reales de compra**: por qué eligieron esta moto sobre otras
- **Experiencia de propiedad**: qué se siente tenerla día a día
- **Calidad percibida**: ensamble, plásticos, acabados según usuarios
- **Comportamiento en condiciones específicas**: lluvia, ciudad, carretera, con pasajero
- **Confiabilidad a largo plazo**: reportes de alto kilometraje, mantenimiento
- **Valor de reventa**: facilidad de venta, depreciación percibida
- **Modificaciones populares**: qué modifican comúnmente los usuarios y por qué

### 2. Relaciones Causa-Efecto

Cuando un usuario conecta una característica con una sensación:
- Ejemplo: "Llanta trasera ancha → Mayor estabilidad, menor agilidad en tráfico cerrado"
- Ejemplo: "Frenos sin ABS → Menor confianza en lluvia"

### 3. Comparaciones Naturales

Cuando usuarios comparan con otros modelos:
- Modelo comparado, razón de comparación, ventajas y desventajas percibidas, motivo de elección

### 4. Menciones de Especificaciones Técnicas

Cuando usuarios mencionan specs (ABS, inyección, frenos, etc.): documenta la mención literal, el contexto y si es por experiencia propia o asumido. **NO validar** si es correcto o incorrecto.

---

## Restricciones Críticas para el Prompt

Incluye estas reglas en el prompt que le construyes a Gemini:

1. **NO filtrar experiencias**: incluir todas, incluso si el país no es claro o hay contradicciones
2. **NO validar**: solo recolectar. La validación ocurre en otra etapa
3. **NO inventar ni especular**: basarse exclusivamente en lo encontrado en internet
4. **Etiquetado preciso de país**: confirmado → nombre del país, dudoso → "incierto" + observación
5. **Enfoque vivencial**: sensaciones sobre specs. "Se siente estable" > "tiene llantas de X pulgadas"
6. **Evitar fuentes fallidas**: si `failed_sources` está presente, no incluir esas fuentes

---

## Formato de Salida

El script retorna este JSON directamente. Inclúyelo como schema en el prompt que construyes.

```json
{
  "experiencias_usuarios": [
    {
      "fuente": "URL o identificador de la fuente",
      "pais_identificado": "Colombia | incierto | nombre_otro_pais",
      "tipo_contenido": "review_propietario | video_youtube | comentario_foro | opinion_marketplace | post_red_social | blog_usuario | otro",
      "fecha_aprox": "2024 | 2024-03 | desconocida",
      "extractos_relevantes": [
        {
          "categoria": "sensaciones_manejo | problemas | ventajas_percibidas | consumo_real | comodidad | confiabilidad | reventa | modificaciones | motivacion_compra | calidad_percibida | comportamiento_lluvia | experiencia_propiedad | otro",
          "texto": "Texto de la experiencia",
          "frecuencia_indicador": "alta | media | baja | unica"
        }
      ],
      "menciones_specs_tecnicas": [
        {
          "spec": "sistema_frenos | sistema_alimentacion | cilindraje | potencia | consumo | seguridad | otro",
          "mencion": "Texto exacto mencionado por el usuario",
          "contexto_mencion": "confirma_tiene | confirma_no_tiene | asume_tiene | asume_no_tiene | compara | otro",
          "fuente_mencion": "experiencia_propia | leido | asumido | desconocido"
        }
      ],
      "relaciones_causa_efecto": [
        {
          "causa": "Característica o especificación mencionada",
          "efecto": "Sensación o consecuencia percibida",
          "texto_original": "Texto donde el usuario conecta causa y efecto"
        }
      ],
      "comparaciones": [
        {
          "modelo_comparado": "Nombre del modelo con el que comparan",
          "razon_comparacion": "Por qué la comparan (segmento, precio, uso)",
          "ventajas_percibidas": ["Ventaja 1", "Ventaja 2"],
          "desventajas_percibidas": ["Desventaja 1"],
          "motivo_eleccion": "Por qué eligieron esta sobre la otra (si aplica)"
        }
      ],
      "observacion": "Solo incluir si hay ambigüedad de país, información parcial o contradicciones"
    }
  ]
}
```

---

## Recordatorios Finales

- Tu trabajo es construir un prompt preciso y pasarlo al script, no estructurar texto crudo
- El schema del prompt y el de esta sección deben ser idénticos
- Incluye en el prompt todas las prioridades y restricciones críticas de este SKILL.md
- El script maneja reintentos automáticamente: si falla, repórtalo al Orchestrator
- Verifica que el JSON recibido tenga objetos anidados, no strings simples
- NO inventes, NO especules, NO valides
