import pandas as pd
from pathlib import Path
from datetime import datetime

# Caminhos
BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "arquivos" / "folha_processada.csv"
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

# Carrega CSV
df = pd.read_csv(CSV_PATH, parse_dates=['dataadmissao', 'datarescisao', 'datanascimento'], dayfirst=True)

# Concatena ano e mês do cálculo para facilitar o filtro
df['ano_mes'] = pd.to_datetime(df['ano_calculo'].astype(str) + '-' + df['mes_calculo'].astype(str).str.zfill(2) + '-01')

# Define mês atual como o mais recente do dataset
mes_atual = df['ano_mes'].max()

# === Anomalia 1: Rubrica de RENDIMENTO que não aparece há 6 meses ===
anomalias_rendimento = []

# Filtra apenas rubricas de rendimento
df_rend = df[df['tipo_rubrica'] == 'RENDIMENTO']

# Para cada colaborador + rubrica, vê se teve um hiato de 6+ meses
for (cpf, cod_rubrica), grupo in df_rend.groupby(['cpf', 'codigo_rubrica']):
    grupo = grupo.sort_values('ano_mes')
    if mes_atual not in grupo['ano_mes'].values:
        continue  # Não processar se essa rubrica não está no mês atual

    ultimos_seis_meses = pd.date_range(end=mes_atual - pd.DateOffset(months=1), periods=6, freq='MS')
    anteriores = grupo[grupo['ano_mes'].isin(ultimos_seis_meses)]
    
    if anteriores.empty:
        registro_atual = grupo[grupo['ano_mes'] == mes_atual].iloc[0]
        anomalias_rendimento.append(registro_atual)


# =============================================================


# === Anomalia 2: Variação brusca em desconto (>=5%) ===
anomalias_desconto = []

# Filtra apenas rubricas de desconto
df_desc = df[df['tipo_rubrica'] == 'DESCONTO']

# Agrupa por colaborador + rubrica
for (cpf, cod_rubrica), grupo in df_desc.groupby(['cpf', 'codigo_rubrica']):
    grupo = grupo.sort_values('ano_mes')
    
    if mes_atual not in grupo['ano_mes'].values:
        continue  # Ignora se não tem dado do mês atual

    grupo_sem_atual = grupo[grupo['ano_mes'] < mes_atual]
    if len(grupo_sem_atual) < 3:
        continue  # Precisa de histórico pra comparar

    media_anterior = grupo_sem_atual['valor'].mean()
    atual = grupo[grupo['ano_mes'] == mes_atual]['valor'].values[0]
    
    variacao = abs(atual - media_anterior) / media_anterior
    if variacao >= 0.05:
        registro_atual = grupo[grupo['ano_mes'] == mes_atual].iloc[0]
        anomalias_desconto.append(registro_atual)

# === Exporta os relatórios ===
df_anom1 = pd.DataFrame(anomalias_rendimento)
df_anom2 = pd.DataFrame(anomalias_desconto)

df_anom1.to_csv(OUTPUT_DIR / "relatorio_rendimentos.csv", index=False)
df_anom2.to_csv(OUTPUT_DIR / "relatorio_descontos.csv", index=False)

print("Relatórios gerados em: outputs/")
