import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import io
import json
import re
from typing import List, Dict

# Configuration de la page
st.set_page_config(
    page_title="Suivi des Ventes d'Assurances",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour améliorer l'interface
st.markdown("""
<style>
.metric-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1rem;
    border-radius: 10px;
    color: white;
    text-align: center;
    margin: 0.5rem 0;
}
.success-box {
    background: #d4edda;
    border: 1px solid #c3e6cb;
    border-radius: 5px;
    padding: 10px;
    margin: 10px 0;
}
.warning-box {
    background: #fff3cd;
    border: 1px solid #ffeaa7;
    border-radius: 5px;
    padding: 10px;
    margin: 10px 0;
}
</style>
""", unsafe_allow_html=True)

# Initialisation des données en session
if 'sales_data' not in st.session_state:
    st.session_state.sales_data = []
if 'objetifs' not in st.session_state:
    st.session_state.objetifs = {'mensuel': 50, 'employe': 15}
if 'settings' not in st.session_state:
    st.session_state.settings = {'theme': 'light', 'auto_save': True}

# Gestion de la réinitialisation des champs
if 'vente_ajoutee' in st.session_state and st.session_state.vente_ajoutee:
    st.session_state.vente_ajoutee = False
    for key in ['nom_client_input', 'numero_reservation_input', 'types_assurance_select']:
        if key in st.session_state:
            del st.session_state[key]

# Fonctions utilitaires
def generate_id():
    """Génère un ID unique pour chaque vente"""
    if not st.session_state.sales_data:
        return 1
    return max([v.get('ID', 0) for v in st.session_state.sales_data]) + 1

def validate_reservation_number(numero):
    """Valide le format du numéro de réservation"""
    pattern = r'^[A-Z0-9]{6,}
import pandas as pd
from datetime import datetime, date
import io

# Configuration de la page
st.set_page_config(
    page_title="Suivi des Ventes d'Assurances",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialisation des données en session
if 'sales_data' not in st.session_state:
    st.session_state.sales_data = []

# Gestion de la réinitialisation des champs après ajout d'une vente
if 'vente_ajoutee' in st.session_state and st.session_state.vente_ajoutee:
    # Réinitialiser les valeurs par défaut pour les champs
    st.session_state.vente_ajoutee = False
    if 'nom_client_input' in st.session_state:
        del st.session_state.nom_client_input
    if 'numero_reservation_input' in st.session_state:
        del st.session_state.numero_reservation_input
    if 'types_assurance_select' in st.session_state:
        del st.session_state.types_assurance_select

# Titre principal
st.title("🛡️ Suivi des Ventes d'Assurances Complémentaires")
st.markdown("---")

# Section 1: Saisie des ventes
st.header("📝 Nouvelle Vente")

col1, col2 = st.columns(2)

with col1:
    employe = st.selectbox(
        "Employé",
        options=["Julie", "Sherman", "Alvin"],
        key="employe_select"
    )
    
    nom_client = st.text_input(
        "Nom du client",
        key="nom_client_input"
    )

with col2:
    numero_reservation = st.text_input(
        "Numéro de réservation",
        key="numero_reservation_input"
    )
    
    types_assurance = st.multiselect(
        "Type(s) d'assurance vendue(s)",
        options=["Pneumatique", "Bris de glace", "Conducteur supplémentaire", "Rachat partiel de franchise"],
        key="types_assurance_select"
    )

# Bouton d'enregistrement
if st.button("💾 Enregistrer la vente", type="primary"):
    if nom_client and numero_reservation and types_assurance:
        # Créer une entrée pour chaque type d'assurance sélectionné
        for type_assurance in types_assurance:
            nouvelle_vente = {
                'Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'Employé': employe,
                'Client': nom_client,
                'Numéro de réservation': numero_reservation,
                'Type d\'assurance': type_assurance,
                'Mois': datetime.now().strftime('%Y-%m')
            }
            st.session_state.sales_data.append(nouvelle_vente)
        
        st.success(f"✅ Vente enregistrée avec succès ! ({len(types_assurance)} assurance(s))")
        
        # Marquer qu'une vente a été ajoutée pour réinitialiser les champs
        st.session_state.vente_ajoutee = True
        st.rerun()
    else:
        st.error("❌ Veuillez remplir tous les champs obligatoires")

st.markdown("---")

# Section 2: Visualisation des ventes
st.header("📊 Ventes Enregistrées")

if st.session_state.sales_data:
    df_sales = pd.DataFrame(st.session_state.sales_data)
    
    # Affichage du tableau avec possibilité de tri
    st.dataframe(
        df_sales.sort_values('Date', ascending=False),
        use_container_width=True,
        hide_index=True
    )
    
    st.info(f"📈 Total des ventes : {len(df_sales)} assurance(s) vendue(s)")
else:
    st.info("Aucune vente enregistrée pour le moment.")

st.markdown("---")

# Section 3: Résumé mensuel
st.header("📅 Résumé Mensuel")

if st.session_state.sales_data:
    df_sales = pd.DataFrame(st.session_state.sales_data)
    
    # Création du tableau croisé dynamique
    pivot_table = pd.crosstab(
        df_sales['Employé'], 
        df_sales['Type d\'assurance'], 
        margins=True, 
        margins_name="Total"
    )
    
    st.subheader("Nombre de ventes par employé et par type d'assurance")
    st.dataframe(pivot_table, use_container_width=True)
    
    # Résumé par employé
    st.subheader("Total des ventes par employé")
    total_par_employe = df_sales.groupby('Employé').size().reset_index(name='Total des ventes')
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.dataframe(total_par_employe, use_container_width=True, hide_index=True)
    
    with col2:
        # Graphique en barres
        st.bar_chart(total_par_employe.set_index('Employé'))

else:
    st.info("Aucune donnée disponible pour le résumé mensuel.")

st.markdown("---")

# Section 4: Export des données
st.header("💾 Export des Données")

if st.session_state.sales_data:
    df_sales = pd.DataFrame(st.session_state.sales_data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Export CSV
        csv_buffer = io.StringIO()
        df_sales.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
        csv_data = csv_buffer.getvalue()
        
        st.download_button(
            label="📄 Télécharger CSV",
            data=csv_data,
            file_name=f"ventes_assurances_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with col2:
        # Export Excel
        excel_buffer = io.BytesIO()
        
        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
            # Feuille des ventes détaillées
            df_sales.to_excel(writer, sheet_name='Ventes Détaillées', index=False)
            
            # Feuille du résumé
            pivot_table = pd.crosstab(
                df_sales['Employé'], 
                df_sales['Type d\'assurance'], 
                margins=True, 
                margins_name="Total"
            )
            pivot_table.to_excel(writer, sheet_name='Résumé Mensuel')
            
            # Feuille totaux par employé
            total_par_employe = df_sales.groupby('Employé').size().reset_index(name='Total des ventes')
            total_par_employe.to_excel(writer, sheet_name='Totaux par Employé', index=False)
        
        excel_data = excel_buffer.getvalue()
        
        st.download_button(
            label="📊 Télécharger Excel",
            data=excel_data,
            file_name=f"ventes_assurances_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

else:
    st.info("Aucune donnée à exporter.")

# Section 5: Gestion des données
st.markdown("---")
st.header("🗂️ Gestion des Données")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🗑️ Effacer toutes les données", type="secondary"):
        if st.session_state.sales_data:
            st.session_state.sales_data = []
            st.success("✅ Toutes les données ont été supprimées")
            st.rerun()
        else:
            st.info("Aucune donnée à supprimer")

with col2:
    st.metric("📊 Total des ventes", len(st.session_state.sales_data))

with col3:
    if st.session_state.sales_data:
        df_temp = pd.DataFrame(st.session_state.sales_data)
        nb_employes = df_temp['Employé'].nunique()
        st.metric("👥 Employés actifs", nb_employes)

# Message de fin
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; font-size: 0.9em; padding: 20px;'>"
    "Application réalisée avec ❤️ par votre assistant IA"
    "</div>", 
    unsafe_allow_html=True
)