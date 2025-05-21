# clustering.py
import pandas as pd
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import os


def segment_customers(filepath):
    df = pd.read_csv(filepath)

    cols_to_use = ['Annual Income (k$)', 'Spending Score (1-100)']
    df = df.dropna(subset=cols_to_use)
    X = df[cols_to_use]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    best_k = 0
    best_score = -1
    for k in range(2, 10):
        model = KMeans(n_clusters=k, random_state=42)
        labels = model.fit_predict(X_scaled)
        score = silhouette_score(X_scaled, labels)
        if score > best_score:
            best_score = score
            best_k = k

    final_model = KMeans(n_clusters=best_k, random_state=42)
    df['Cluster'] = final_model.fit_predict(X_scaled)

    # Crear gráfico interactivo
    fig = px.scatter(
        df,
        x='Annual Income (k$)',
        y='Spending Score (1-100)',
        color='Cluster',
        title=f'Segmentación de Clientes (k={best_k})',
        hover_data=['Cluster']
    )
    graph_html = fig.to_html(full_html=False)

    # Crear resumen con descripciones
    summary = df.groupby('Cluster')[cols_to_use].mean().round(1)
    summary['Count'] = df['Cluster'].value_counts().sort_index()

    def categorize_income(x):
        if x < 40: return 'Bajo'
        elif x < 70: return 'Medio'
        else: return 'Alto'

    def categorize_spending(x):
        if x < 40: return 'Poco Gasto'
        elif x < 60: return 'Gasto Medio'
        else: return 'Gasto Alto'

    descriptions = []
    for i, row in summary.iterrows():
        income = categorize_income(row['Annual Income (k$)'])
        spending = categorize_spending(row['Spending Score (1-100)'])

        recommendation = "Atraer con promociones" if income == 'Alto' and spending == 'Poco Gasto' else \
                         "Fidelizar" if spending == 'Gasto Alto' else \
                         "Clientes potenciales"

        descriptions.append(f"Cluster {i}: Ingreso {income}, {spending} → {recommendation} ({row['Count']} clientes)")

    return df, graph_html, descriptions
