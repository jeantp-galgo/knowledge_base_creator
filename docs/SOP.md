# SOP — deep_research_models

## Proposito

Generar bases de conocimiento experienciales (.md) sobre modelos especificos de motocicletas a partir de una investigacion web directa con Gemini. El operador selecciona el modelo, ejecuta el notebook y obtiene la KB lista para usar.

## Configuracion inicial

### Variables de entorno

```bash
cp .env_example .env
```

Editar `.env` y completar:

```env
GEMINI_API_KEY=<tu clave de Google AI Studio>
MKP_INVENTORY_BASE64=<JSON de la cuenta de servicio de Google Sheets, codificado en base64>
```

Para generar el valor de `MKP_INVENTORY_BASE64` a partir del JSON de la service account:

```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("key.json"))
```

La cuenta de servicio debe tener acceso de lectura al Google Sheet **"[MKP] Base de conocimiento"**.

### Configuracion de pais

El inventario se lee desde el Google Sheet "[MKP] Base de conocimiento", con una pestaña por pais (`COUNTRY_TABS` en `src/sources/database/sheets/inventory.py`: `Base MX Moto`, `Base CO Moto`, `Base CL Moto`). Para elegir el pais activo, editar `src/config/settings.py`:

```python
COUNTRY = "CO"  # "CO" | "MX" | "CL"
```

### Instalacion

```bash
python -m venv venv
venv\Scripts\activate         # Windows
source venv/bin/activate      # Linux / macOS

pip install -r requirements.txt
```

---

## Ejecucion

**Notebook**: `notebooks/direct_research.ipynb`

1. Verificar que `COUNTRY` en `settings.py` corresponde al pais que quieres procesar
2. Ejecutar **Celda 1** — imports e inicializacion de Gemini e Inventory
3. Ejecutar **Celda 2** — carga el DataFrame del inventario (Google Sheets) del pais configurado
4. En **Celda 3**, cambiar el `code` al modelo que quieres procesar:
   ```python
   df_modelo = df_data_base[df_data_base["code"] == "CO2961-hero-hunk-125-r"]
   ```
5. Ejecutar **Celda 4** — extrae variables del modelo (BRAND, MODEL, TITLE, etc.)
6. Ejecutar **Celda 5** — construye y muestra el prompt armado; verificar que no haya `{VARIABLES}` sin reemplazar
7. Ejecutar **Celda 6** — llama a Gemini; la investigacion tarda entre 2 y 5 minutos
8. Ejecutar **Celda 7** — guarda la KB en disco

### Donde queda el resultado

```
src/data/output/gemini/{PAIS}-{MARCA}_{MODELO}-direct.md
```

Ejemplo: `CO-Hero_Hunk 125 R-direct.md`

---

## Agregar un nuevo pais

1. Agregar la pestaña del Sheet en `COUNTRY_TABS` (`src/sources/database/sheets/inventory.py`):
   ```python
   COUNTRY_TABS = {..., "PE": "Base PE Moto"}
   ```
2. Agregar el codigo a `SUPPORTED_COUNTRIES` y `COUNTRY_NAMES` en `settings.py`
3. Agregar el mapeo de codigo a nombre en el diccionario del notebook:
   ```python
   PAIS = {"CO": "Colombia", "MX": "Mexico", "CL": "Chile", "PE": "Peru"}.get(COUNTRY)
   ```

---

## Notas

| Situacion | Comportamiento | Solucion |
|---|---|---|
| Gemini bloquea por recitation | `GeminiProcessor` reintenta automaticamente con instruccion de parafraseo | No requiere accion manual |
| Modelo con codigo incorrecto | El DataFrame `df_modelo` queda vacio y las celdas siguientes fallan con KeyError | Verificar el `code` en el inventario (Google Sheets) |
| KB con muchos "Sin datos suficientes" | Ocurre en modelos con poca presencia en foros del pais; Gemini lo declara en `[LIMITACIONES]` | Revisar la KB — la seccion `[LIMITACIONES]` indica que mercados se consultaron |
| Quiero ajustar el comportamiento de la investigacion | El prompt esta en `src/data/input/prompts/direct_research_template.md` | Editar el template directamente; los cambios aplican en la siguiente ejecucion |
