import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import io
import json
import base64
from io import BytesIO
import calendar

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

if 'objectifs' not in st.session_state:
    st.session_state.objectifs = {"Julie": 50, "Sherman": 45, "Alvin": 40}

if 'commissions' not in st.session_state:
    st.session_state.commissions = {
        "Pneumatique": 15,
        "Bris de glace": 20,
        "Conducteur supplémentaire": 25,
        "Rachat partiel de franchise": 30
    }

if 'notes' not in st.session_state:
    st.session_state.notes = {}

# Gestion de la réinitialisation des champs après ajout d'une vente
if 'vente_ajoutee' in st.session_state and st.session_state.vente_ajoutee:
    st.session_state.vente_ajoutee = False
    if 'nom_client_input' in st.session_state:
        del st.session_state.nom_client_input
    if 'numero_reservation_input' in st.session_state:
        del st.session_state.numero_reservation_input
    if 'types_assurance_select' in st.session_state:
        del st.session_state.types_assurance_select

# Fonctions utilitaires
def save_data_to_json():
    data = {
        'sales_data': st.session_state.sales_data,
        'objectifs': st.session_state.objectifs,
        'commissions': st.session_state.commissions,
        'notes': st.session_state.notes,
        'export_date': datetime.now().isoformat()
    }
    return json.dumps(data, indent=2, ensure_ascii=False)

def load_data_from_json(json_content):
    try:
        data = json.loads(json_content)
        if 'sales_data' in data:
            st.session_state.sales_data = data['sales_data']
        if 'objectifs' in data:
            st.session_state.objectifs = data['objectifs']
        if 'commissions' in data:
            st.session_state.commissions = data['commissions']
        if 'notes' in data:
            st.session_state.notes = data['notes']
        return True
    except:
        return False

def calculer_commissions(employe, types_assurance):
    total = 0
    for type_assurance in types_assurance:
        total += st.session_state.commissions.get(type_assurance, 0)
    return total

def generer_rapport_performance():
    if not st.session_state.sales_data:
        return "Aucune donnée disponible"
    
    df = pd.DataFrame(st.session_state.sales_data)
    rapport = []
    
    # Analyse par employé
    for employe in ["Julie", "Sherman", "Alvin"]:
        ventes_employe = df[df['Employé'] == employe]
        objectif = st.session_state.objectifs.get(employe, 0)
        nb_ventes = len(ventes_employe)
        taux_reussite = (nb_ventes / objectif * 100) if objectif > 0 else 0
        
        rapport.append(f"📊 {employe}:")
        rapport.append(f"   • Ventes: {nb_ventes}/{objectif} ({taux_reussite:.1f}%)")
        
        if len(ventes_employe) > 0:
            # Commission totale
            commission_total = 0
            for _, vente in ventes_employe.iterrows():
                commission_total += st.session_state.commissions.get(vente['Type d\'assurance'], 0)
            rapport.append(f"   • Commission totale: {commission_total}€")
        
        rapport.append("")
    
    return "\n".join(rapport)

# CSS pour améliorer l'apparence
st.markdown("""
<style>
.metric-card {
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    padding: 1rem;
    border-radius: 10px;
    border-left: 4px solid #1f77b4;
    margin: 0.5rem 0;
}

.success-card {
    background: linear-gradient(135deg, #e8f5e8 0%, #a5d6a7 100%);
    border-left: 4px solid #4caf50;
}

.warning-card {
    background: linear-gradient(135deg, #fff3e0 0%, #ffcc80 100%);
    border-left: 4px solid #ff9800;
}

.danger-card {
    background: linear-gradient(135deg, #ffebee 0%, #ef9a9a 100%);
    border-left: 4px solid #f44336;
}

.sidebar-metric {
    text-align: center;
    padding: 10px;
    margin: 5px 0;
    border-radius: 8px;
    background: rgba(255,255,255,0.1);
}
</style>
""", unsafe_allow_html=True)

# Sidebar avec navigation et métriques en temps réel
st.sidebar.title("🎯 Navigation")

if st.session_state.sales_data:
    df_sidebar = pd.DataFrame(st.session_state.sales_data)
    
    # Métriques en temps réel dans la sidebar
    st.sidebar.markdown("### 📊 Métriques en Temps Réel")
    
    # Ventes aujourd'hui
    today = datetime.now().strftime('%Y-%m-%d')
    ventes_aujourd_hui = len(df_sidebar[df_sidebar['Date'].str.startswith(today)])
    st.sidebar.markdown(f'<div class="sidebar-metric">🔥 Aujourd\'hui<br><strong>{ventes_aujourd_hui}</strong></div>', unsafe_allow_html=True)
    
    # Ventes cette semaine
    week_start = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime('%Y-%m-%d')
    ventes_semaine = len(df_sidebar[df_sidebar['Date'] >= week_start])
    st.sidebar.markdown(f'<div class="sidebar-metric">📅 Cette semaine<br><strong>{ventes_semaine}</strong></div>', unsafe_allow_html=True)
    
    # Top vendeur
    top_vendeur = df_sidebar['Employé'].value_counts().index[0] if len(df_sidebar) > 0 else "N/A"
    nb_ventes_top = df_sidebar['Employé'].value_counts().iloc[0] if len(df_sidebar) > 0 else 0
    st.sidebar.markdown(f'<div class="sidebar-metric">🏆 Top vendeur<br><strong>{top_vendeur}</strong> ({nb_ventes_top})</div>', unsafe_allow_html=True)

# Menu de navigation
page = st.sidebar.selectbox("Choisir une section", [
    "🏠 Accueil & Saisie",
    "📊 Tableau de Bord",
    "📈 Analyses Avancées", 
    "⚙️ Configuration",
    "📋 Rapports",
    "💾 Sauvegarde & Import"
])

# PAGE PRINCIPALE
if page == "🏠 Accueil & Saisie":
    st.title("🛡️ Suivi des Ventes d'Assurances Complémentaires")
    
    # Alertes et notifications
    if st.session_state.sales_data:
        df_alerts = pd.DataFrame(st.session_state.sales_data)
        
        # Vérification des objectifs
        col1, col2, col3 = st.columns(3)
        
        for i, employe in enumerate(["Julie", "Sherman", "Alvin"]):
            ventes_employe = len(df_alerts[df_alerts['Employé'] == employe])
            objectif = st.session_state.objectifs.get(employe, 0)
            pourcentage = (ventes_employe / objectif * 100) if objectif > 0 else 0
            
            with [col1, col2, col3][i]:
                if pourcentage >= 100:
                    st.markdown(f'<div class="metric-card success-card">🎉 <strong>{employe}</strong><br>Objectif atteint ! ({ventes_employe}/{objectif})</div>', unsafe_allow_html=True)
                elif pourcentage >= 80:
                    st.markdown(f'<div class="metric-card warning-card">⚡ <strong>{employe}</strong><br>Proche de l\'objectif ({ventes_employe}/{objectif})</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="metric-card">📊 <strong>{employe}</strong><br>{ventes_employe}/{objectif} ventes ({pourcentage:.0f}%)</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Section de saisie améliorée
    st.header("📝 Nouvelle Vente")
    
    col1, col2 = st.columns(2)
    
    with col1:
        employe = st.selectbox(
            "👤 Employé",
            options=["Julie", "Sherman", "Alvin"],
            key="employe_select"
        )
        
        nom_client = st.text_input(
            "🧑‍💼 Nom du client",
            key="nom_client_input",
            placeholder="Ex: Jean Dupont"
        )
        
        # Validation en temps réel
        if nom_client and len(nom_client) < 2:
            st.warning("⚠️ Le nom doit contenir au moins 2 caractères")

    with col2:
        numero_reservation = st.text_input(
            "🎫 Numéro de réservation",
            key="numero_reservation_input",
            placeholder="Ex: RES123456"
        )
        
        # Vérification des doublons
        if numero_reservation and st.session_state.sales_data:
            df_check = pd.DataFrame(st.session_state.sales_data)
            if numero_reservation in df_check['Numéro de réservation'].values:
                st.error("❌ Ce numéro de réservation existe déjà !")
        
        types_assurance = st.multiselect(
            "🛡️ Type(s) d'assurance vendue(s)",
            options=["Pneumatique", "Bris de glace", "Conducteur supplémentaire", "Rachat partiel de franchise"],
            key="types_assurance_select",
            help="Vous pouvez sélectionner plusieurs assurances pour un même client"
        )
    
    # Aperçu de la commission
    if types_assurance:
        commission_prevue = calculer_commissions(employe, types_assurance)
        st.info(f"💰 Commission prévue: {commission_prevue}€ pour {len(types_assurance)} assurance(s)")
    
    # Note optionnelle
    note_vente = st.text_area(
        "📝 Note (optionnel)",
        placeholder="Commentaire sur cette vente...",
        max_chars=500
    )
    
    # Bouton d'enregistrement amélioré
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if st.button("💾 Enregistrer la vente", type="primary", use_container_width=True):
            if nom_client and numero_reservation and types_assurance:
                # Vérification finale des doublons
                if st.session_state.sales_data:
                    df_check = pd.DataFrame(st.session_state.sales_data)
                    if numero_reservation in df_check['Numéro de réservation'].values:
                        st.error("❌ Ce numéro de réservation existe déjà !")
                        st.stop()
                
                # Enregistrement
                new_id = max([v.get('ID', 0) for v in st.session_state.sales_data] + [0]) + 1
                
                for type_assurance in types_assurance:
                    nouvelle_vente = {
                        'ID': new_id,
                        'Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'Employé': employe,
                        'Client': nom_client,
                        'Numéro de réservation': numero_reservation,
                        'Type d\'assurance': type_assurance,
                        'Commission': st.session_state.commissions.get(type_assurance, 0),
                        'Mois': datetime.now().strftime('%Y-%m'),
                        'Jour_semaine': calendar.day_name[datetime.now().weekday()]
                    }
                    st.session_state.sales_data.append(nouvelle_vente)
                    new_id += 1
                
                # Enregistrer la note si fournie
                if note_vente.strip():
                    st.session_state.notes[numero_reservation] = note_vente.strip()
                
                st.success(f"✅ Vente enregistrée ! {len(types_assurance)} assurance(s) • Commission: {calculer_commissions(employe, types_assurance)}€")
                st.session_state.vente_ajoutee = True
                st.rerun()
            else:
                st.error("❌ Veuillez remplir tous les champs obligatoires")
    
    with col2:
        if st.button("🔄 Effacer", use_container_width=True):
            st.session_state.vente_ajoutee = True
            st.rerun()

elif page == "📊 Tableau de Bord":
    st.title("📊 Tableau de Bord des Ventes")
    
    if not st.session_state.sales_data:
        st.info("📝 Aucune vente enregistrée. Rendez-vous dans 'Accueil & Saisie' pour commencer.")
        st.stop()
    
    df_sales = pd.DataFrame(st.session_state.sales_data)
    
    # Interface de suppression et gestion complète des ventes
    st.subheader("🗑️ Gestion des Ventes")
    
    # Recherche rapide
    search_term = st.text_input("🔍 Rechercher", placeholder="Client, numéro de réservation...")
    
    # Application de la recherche
    df_filtered = df_sales.copy()
    if search_term:
        mask = (
            df_filtered['Client'].str.contains(search_term, case=False, na=False) |
            df_filtered['Numéro de réservation'].str.contains(search_term, case=False, na=False)
        )
        df_filtered = df_filtered[mask]
    
    # Sélection des ventes à supprimer
    if len(df_filtered) > 0:
        ventes_a_supprimer = st.multiselect(
            "Sélectionnez les ventes à supprimer :",
            options=df_filtered.index.tolist(),
            format_func=lambda x: f"ID {df_filtered.loc[x, 'ID']} • {df_filtered.loc[x, 'Client']} • {df_filtered.loc[x, 'Type d\'assurance']} • {df_filtered.loc[x, 'Date'][:16]}",
            help="Maintenez Ctrl/Cmd pour sélectionner plusieurs ventes"
        )
        
        if ventes_a_supprimer:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Supprimer sélection", type="secondary"):
                    st.session_state.confirm_delete = ventes_a_supprimer
            
            if 'confirm_delete' in st.session_state:
                st.warning(f"⚠️ Confirmer la suppression de {len(st.session_state.confirm_delete)} vente(s) ?")
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("✅ Confirmer", type="primary"):
                        # Supprimer les ventes
                        for idx in sorted(st.session_state.confirm_delete, reverse=True):
                            del st.session_state.sales_data[idx]
                        
                        st.success(f"✅ {len(st.session_state.confirm_delete)} vente(s) supprimée(s)")
                        del st.session_state.confirm_delete
                        st.rerun()
                
                with col2:
                    if st.button("❌ Annuler"):
                        del st.session_state.confirm_delete
                        st.rerun()
    
    # Affichage du tableau
    st.subheader("📋 Tableau des Ventes")
    
    if len(df_filtered) > 0:
        st.dataframe(
            df_filtered.sort_values('Date', ascending=False),
            use_container_width=True,
            hide_index=True
        )
        
        # Statistiques
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📊 Ventes affichées", len(df_filtered))
        
        with col2:
            commission_totale = df_filtered['Commission'].sum() if 'Commission' in df_filtered.columns else 0
            st.metric("💰 Commission totale", f"{commission_totale}€")
        
        with col3:
            client_unique = df_filtered['Client'].nunique()
            st.metric("👥 Clients uniques", client_unique)
        
        with col4:
            if len(df_filtered) > 0:
                assurance_populaire = df_filtered['Type d\'assurance'].mode()[0]
                st.metric("🏆 Assurance populaire", assurance_populaire)

elif page == "📈 Analyses Avancées":
    st.title("📈 Analyses Avancées")
    
    if not st.session_state.sales_data:
        st.info("📝 Aucune donnée pour l'analyse.")
        st.stop()
    
    df_analysis = pd.DataFrame(st.session_state.sales_data)
    df_analysis['Date'] = pd.to_datetime(df_analysis['Date'])
    
    # Graphiques et analyses
    tab1, tab2, tab3 = st.tabs(["📊 Performance", "📅 Tendances", "🎯 Objectifs"])
    
    with tab1:
        st.subheader("📊 Performance par Employé")
        ventes_par_employe = df_analysis['Employé'].value_counts()
        st.bar_chart(ventes_par_employe)
        
        st.subheader("🛡️ Types d'Assurance")
        assurance_counts = df_analysis['Type d\'assurance'].value_counts()
        st.bar_chart(assurance_counts)
    
    with tab2:
        st.subheader("📅 Ventes par Jour")
        df_analysis['Date_only'] = df_analysis['Date'].dt.date
        ventes_par_jour = df_analysis.groupby('Date_only').size()
        st.line_chart(ventes_par_jour)
    
    with tab3:
        st.subheader("🎯 Suivi des Objectifs")
        for employe in ["Julie", "Sherman", "Alvin"]:
            ventes = len(df_analysis[df_analysis['Employé'] == employe])
            objectif = st.session_state.objectifs[employe]
            pourcentage = (ventes / objectif * 100) if objectif > 0 else 0
            
            st.write(f"**{employe}**")
            st.progress(min(pourcentage / 100, 1.0))
            st.write(f"Ventes: {ventes}/{objectif} ({pourcentage:.1f}%)")

elif page == "⚙️ Configuration":
    st.title("⚙️ Configuration")
    
    tab1, tab2 = st.tabs(["🎯 Objectifs", "💰 Commissions"])
    
    with tab1:
        st.subheader("🎯 Objectifs Mensuels")
        for employe in ["Julie", "Sherman", "Alvin"]:
            current_objectif = st.session_state.objectifs.get(employe, 0)
            new_objectif = st.number_input(
                f"Objectif pour {employe}",
                min_value=0,
                max_value=200,
                value=current_objectif,
                key=f"obj_{employe}"
            )
            st.session_state.objectifs[employe] = new_objectif
    
    with tab2:
        st.subheader("💰 Commissions")
        for assurance in ["Pneumatique", "Bris de glace", "Conducteur supplémentaire", "Rachat partiel de franchise"]:
            current_commission = st.session_state.commissions.get(assurance, 0)
            new_commission = st.number_input(
                f"Commission {assurance} (€)",
                min_value=0.0,
                max_value=100.0,
                value=float(current_commission),
                step=0.5,
                key=f"comm_{assurance}"
            )
            st.session_state.commissions[assurance] = new_commission

elif page == "📋 Rapports":
    st.title("📋 Rapports")
    
    if not st.session_state.sales_data:
        st.info("📝 Aucune donnée pour les rapports.")
        st.stop()
    
    df_reports = pd.DataFrame(st.session_state.sales_data)
    
    # Exports multiples
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Export CSV
        csv_buffer = io.StringIO()
        df_reports.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
        st.download_button(
            label="📄 CSV",
            data=csv_buffer.getvalue(),
            file_name=f"ventes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with col2:
        # Export Excel
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
            df_reports.to_excel(writer, sheet_name='Ventes', index=False)
        
        st.download_button(
            label="📊 Excel",
            data=excel_buffer.getvalue(),
            file_name=f"rapport_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    with col3:
        # Export JSON
        json_data = save_data_to_json()
        st.download_button(
            label="💾 JSON",
            data=json_data,
            file_name=f"sauvegarde_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

elif page == "💾 Sauvegarde & Import":
    st.title("💾 Sauvegarde & Import")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📂 Import")
        uploaded_file = st.file_uploader("Charger fichier", type=['json', 'csv'])
        
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.json'):
                    content = uploaded_file.read().decode('utf-8')
                    if load_data_from_json(content):
                        st.success(f"✅ {len(st.session_state.sales_data)} ventes chargées !")
                        st.rerun()
                
                elif uploaded_file.name.endswith('.csv'):
                    df_imported = pd.read_csv(uploaded_file)
                    st.session_state.sales_data = df_imported.to_dict('records')
                    st.success(f"✅ {len(df_imported)} ventes importées !")
                    st.rerun()
            
            except Exception as e:
                st.error(f"❌ Erreur: {str(e)}")
    
    with col2:
        st.subheader("💾 Sauvegarde")
        
        if st.session_state.sales_data:
            json_backup = save_data_to_json()
            st.download_button(
                label="💾 Sauvegarde Complète",
                data=json_backup,
                file_name=f"sauvegarde_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
            
            st.info(f"📊 {len(st.session_state.sales_data)} ventes + configuration")

# Footer
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.session_state.sales_data:
        st.metric("📊 Total ventes", len(st.session_state.sales_data))

with col2:
    if st.session_state.sales_data:
        df_footer = pd.DataFrame(st.session_state.sales_data)
        commission_totale = df_footer['Commission'].sum() if 'Commission' in df_footer.columns else 0
        st.metric("💰 Commissions", f"{commission_totale}€")

with col3:
    st.metric("🕐 Dernière MAJ", datetime.now().strftime('%H:%M:%S'))

with col4:
    st.metric("👥 Équipe", 3)

# Message de fin
st.markdown(
    "<div style='text-align: center; color: #666; font-size: 0.9em; padding: 20px;'>"
    "Application professionnelle réalisée avec ❤️ par votre assistant IA<br>"
    f"Version 2.0 • {datetime.now().strftime('%d/%m/%Y')}"
    "</div>", 
    unsafe_allow_html=True
)