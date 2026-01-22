import os
import time
import gzip
import io
from datetime import datetime, timedelta
import requests
import pandas as pd
import json
from src.sources.amplitude.utils import process_data


class Amplitude:
    def __init__(self):
        self.api_key = os.getenv('API_KEY')
        self.api_secret = os.getenv('API_SECRET')

    def get_raw_events(self, start_date, end_date):
        """
        Descarga eventos RAW directamente desde Amplitude.
        NO usa charts, por lo tanto NO tiene el límite de 100 URLs.

        Args:
            start_date: string 'YYYYMMDD' o datetime
            end_date: string 'YYYYMMDD' o datetime

        Returns:
            list: Eventos raw completos
        """
        # Convertir fechas
        if isinstance(start_date, datetime):
            start_str = start_date.strftime('%Y%m%d')
        else:
            start_str = start_date

        if isinstance(end_date, datetime):
            end_str = end_date.strftime('%Y%m%d')
        else:
            end_str = end_date

        # API de export (NO de charts)
        url = 'https://amplitude.com/api/2/export'

        params = {
            'start': start_str,
            'end': end_str
        }

        print(f"📥 Descargando eventos RAW: {start_str} → {end_str}")

        response = requests.get(
            url,
            auth=(self.api_key, self.api_secret),
            params=params,
            stream=True
        )

        if response.status_code != 200:
            print(f"❌ Error {response.status_code}: {response.text[:300]}")
            return None

        # Parsear eventos - los datos vienen comprimidos en GZIP
        events = []
        total_lines = 0
        comparator_events = 0

        try:
            # Descomprimir el contenido gzip
            decompressed = gzip.GzipFile(fileobj=io.BytesIO(response.content))

            for line in decompressed:
                if line:
                    total_lines += 1
                    try:
                        # Decodificar bytes a string y luego parsear JSON
                        event = json.loads(line.decode('utf-8'))

                        # Filtrar solo "Comparator Viewed"
                        if event.get('event_type') == 'Comparator Viewed':
                            events.append(event)
                            comparator_events += 1

                        if total_lines % 50000 == 0:
                            print(f"  📊 {total_lines:,} eventos procesados ({comparator_events:,} relevantes)")

                    except json.JSONDecodeError:
                        continue

        except gzip.BadGzipFile:
            # Si no está comprimido, intentar como texto plano (fallback)
            print("⚠️  Datos no comprimidos, procesando como texto plano...")
            for line in response.iter_lines():
                if line:
                    total_lines += 1
                    try:
                        event = json.loads(line.decode('utf-8') if isinstance(line, bytes) else line)

                        if event.get('event_type') == 'Comparator Viewed':
                            events.append(event)
                            comparator_events += 1

                        if total_lines % 50000 == 0:
                            print(f"  📊 {total_lines:,} eventos procesados ({comparator_events:,} relevantes)")

                    except json.JSONDecodeError:
                        continue

        print(f"✅ Total eventos: {total_lines:,}")
        print(f"✅ Comparator Viewed: {comparator_events:,}\n")

        return events

    def process_raw_events(self, events):
        """
        Convierte eventos raw en DataFrame agrupado por URL.
        Esta es tu nueva función "process_data" pero para eventos raw.

        Args:
            events: Lista de eventos raw de Amplitude

        Returns:
            DataFrame con columnas: url, total_views, unique_users, unique_sessions
        """
        if not events:
            print("❌ No hay eventos para procesar")
            return None

        df = pd.DataFrame(events)

        print(f"📋 Columnas disponibles: {df.columns.tolist()[:10]}...")

        # Extraer URL desde event_properties
        if 'event_properties' in df.columns:
            df['url'] = df['event_properties'].apply(
                lambda x: x.get('url', None) if isinstance(x, dict) else None
            )
        elif 'url' in df.columns:
            pass  # Ya existe
        else:
            print("⚠️  No se encontró el campo URL")
            # Mostrar ejemplo de event_properties para debugging
            if len(df) > 0 and 'event_properties' in df.columns:
                print(f"Ejemplo de event_properties: {df['event_properties'].iloc[0]}")
            return df

        # Eliminar URLs nulas
        df = df[df['url'].notna()]

        print(f"\n🔄 Agrupando {len(df):,} eventos por URL...")

        # Agrupar por URL
        url_stats = df.groupby('url').agg({
            'event_time': 'count',      # Total vistas
            'user_id': 'nunique',       # Usuarios únicos
            'session_id': 'nunique'     # Sesiones únicas
        }).rename(columns={
            'event_time': 'total_views',
            'user_id': 'unique_users',
            'session_id': 'unique_sessions'
        }).reset_index()

        # Ordenar por vistas descendente
        url_stats = url_stats.sort_values('total_views', ascending=False)

        print(f"✅ URLs únicas: {len(url_stats):,}")
        print(f"✅ Total vistas: {url_stats['total_views'].sum():,}")

        return url_stats

    def start_session_weekly(self, weeks=4):
        """
        Reemplazo de start_session() para descargar por semanas.

        Args:
            weeks: Número de semanas hacia atrás

        Returns:
            DataFrame con TODAS las URLs (sin límite de 100)
        """
        all_events = []
        end_date = datetime.now()

        print(f"\n{'='*70}")
        print(f"🚀 DESCARGA SEMANAL - {weeks} semanas")
        print(f"{'='*70}\n")

        for week_num in range(weeks):
            week_end = end_date - timedelta(days=7 * week_num)
            week_start = week_end - timedelta(days=7)

            print(f"📅 SEMANA {week_num + 1}/{weeks}: {week_start.date()} → {week_end.date()}")

            events = self.get_raw_events(week_start, week_end)

            if events:
                all_events.extend(events)
                print(f"   📦 Acumulado: {len(all_events):,} eventos\n")
            else:
                print(f"   ⚠️  No se obtuvieron eventos\n")

            # Delay entre semanas para no saturar la API
            if week_num < weeks - 1:
                time.sleep(2)

        if not all_events:
            print("❌ No se descargaron eventos")
            return None

        # Procesar todos los eventos juntos
        print(f"\n{'='*70}")
        print(f"🔄 PROCESAMIENTO FINAL")
        print(f"{'='*70}\n")

        df = self.process_raw_events(all_events)

        return df

    # Mantener start_session original pero con warning
    def start_session(self, chart_id):
        """
        ⚠️  DEPRECADO: Solo obtendrás ~100 URLs debido a límite del chart.

        Usa start_session_weekly() en su lugar para obtener TODAS las URLs.
        """
        print("\n⚠️  ADVERTENCIA ⚠️")
        print("Este método usa charts que tienen límite de ~100 URLs.")
        print("Para obtener todas las URLs, usa: amp.start_session_weekly(weeks=4)")
        print("Continuando de todas formas...\n")

        data = self.get_data_from_chart_id(chart_id)

        if data:
            data = process_data(data)

        return data

    def get_data_from_chart_id(self, chart_id, limit_per_page=10000, delay_between_requests=1):
        """
        Método original para charts (mantiene compatibilidad).
        Solo útil si necesitas exactamente lo que el chart muestra.
        """
        all_data = None
        offset = 0
        page = 1

        while True:
            print(f"Obteniendo página {page} (offset: {offset})...")

            url = f'https://amplitude.com/api/3/chart/{chart_id}/query'

            params = {
                'limit': limit_per_page,
                'offset': offset
            }

            response = requests.get(url, auth=(self.api_key, self.api_secret), params=params)

            if response.status_code == 200:
                data = response.json()

                if all_data is None:
                    all_data = data
                else:
                    if 'data' in data and 'data' in all_data:
                        all_data['data'].extend(data['data'])
                    elif 'series' in data and 'series' in all_data:
                        for i, series in enumerate(data['series']):
                            if i < len(all_data['series']):
                                all_data['series'][i]['data'].extend(series['data'])

                current_data_count = len(data.get('data', data.get('series', [data] if isinstance(data, list) else [])))

                if current_data_count < limit_per_page:
                    print(f"Datos completos obtenidos. Total de páginas: {page}")
                    break

                offset += limit_per_page
                page += 1

                if delay_between_requests > 0:
                    time.sleep(delay_between_requests)

            else:
                print(f"Error al obtener los datos en la página {page}: {response.status_code}")
                if page == 1:
                    return None
                else:
                    print("Devolviendo datos parciales obtenidos hasta ahora...")
                    break

        return all_data