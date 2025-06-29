import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image

# Configurare pagină
st.set_page_config(layout="wide", page_title="Well-to-Wheel")

# CSS personalizat
st.markdown("""
<style>
.stApp, .stDataFrame, .stPlotlyChart {
    background-color: white !important;
}
.css-1v0mbdj, .st-emotion-cache-1v0mbdj {
    display: none !important;
}
h1, h2, h3, p, .stMarkdown, .stSelectbox, .stRadio, .stSlider {
    color: black !important;
}
.stSelectbox, .stRadio, .stSlider {
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 10px;
    margin-bottom: 15px;
}
.specs-box {
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 10px;
    margin-top: 10px;
    background-color: #f9f9f9;
}
</style>
""", unsafe_allow_html=True)

# ---- DATE DE BAZĂ ----
# mix energetic
tari = {
    "Europa": {"Carbune": 35, "Gaz": 15, "Nuclear": 6, "Regenerabil": 44},
    "Romania": {"Gaz": 32, "Carbune": 28, "Nuclear": 20, "Regenerabil": 20},
    "Germania": {"Carbune": 35, "Gaz": 15, "Nuclear": 6, "Regenerabil": 44},
    "Franța": {"Nuclear": 69, "Regenerabil": 21, "Gaz": 7, "Carbune": 3},
    "Norvegia": {"Regenerabil": 98, "Gaz": 2, "Nuclear": 0, "Carbune": 0},
    "Polonia": {"Carbune": 74, "Regenerabil": 16, "Gaz": 9, "Nuclear": 1},
    "Spania": {"Regenerabil": 46, "Gaz": 27, "Nuclear": 20, "Carbune": 7},
    "Italia": {"Gaz": 42, "Regenerabil": 36, "Carbune": 5, "Nuclear": 0},
    "Suedia": {"Regenerabil": 65, "Nuclear": 30, "Gaz": 3, "Carbune": 2},
    "Olanda": {"Gaz": 54, "Regenerabil": 27, "Carbune": 14, "Nuclear": 5},
    "Danemarca": {"Regenerabil": 81, "Gaz": 15, "Carbune": 4, "Nuclear": 0}
}

# Coeficienți emisii pe productie de hidrogen (gCO₂/kWh)

emisii_hidrogen = {
    "Roz": 45,      # gCO₂/kg
    "Albastru": 45,
    "Verde": 0,
    "Galben": 100,
    "Brun": 130,
    "Gri": 130,
    "Turcoaz": 80,
}

# Coeficienți emisii pe sursă de energie (gCO₂/kWh)
coef_emisii = {
    "Carbune": 820,
    "Gaz": 490,
    "Nuclear": 12,
    "Regenerabil": 24
}

# Modele vehicule
modele_vehicule = {
    "HEV": {
        "Toyota Corolla Hybrid (Euro 6d)": {"consum": 4.1, "emisii_tank": 92},
        "Toyota Prius (Euro 6)": {"consum": 3.9, "emisii_tank": 89},
	"Toyota Prius (Euro 5)": {"consum": 4.1, "emisii_tank": 95},
	"Toyota Prius (Euro 4)": {"consum": 5, "emisii_tank": 100},
        "Honda Civic Hybrid (Euro 6d-TEMP)": {"consum": 4.3, "emisii_tank": 97},
        "Hyundai Ioniq Hybrid (Euro 6)": {"consum": 3.8, "emisii_tank": 86},
        "Lexus UX 250h (Euro 6d)": {"consum": 4.7, "emisii_tank": 105},
        "Ford Mondeo Hybrid (Euro 6d)": {"consum": 4.9, "emisii_tank": 110},
        "Toyota C-HR Hybrid (Euro 6d)": {"consum": 4.5, "emisii_tank": 101},
        "Suzuki Swace (Euro 6d)": {"consum": 4.2, "emisii_tank": 95},
    },
    "PHEV": {
        "Mitsubishi Outlander PHEV (Euro 6d)": {"consum_combustibil": 6.0, "consum_electric": 18, "emisii_tank": 80, "autonomie": 50},
        "Volvo XC60 Recharge (Euro 6d)": {"consum_combustibil": 6.5, "consum_electric": 19, "emisii_tank": 85, "autonomie": 50},
        "BMW 330e (Euro 6d-TEMP)": {"consum_combustibil": 5.5, "consum_electric": 15, "emisii_tank": 75, "autonomie": 50},
        "Mercedes A 250 e (Euro 6d)": {"consum_combustibil": 5.8, "consum_electric": 16, "emisii_tank": 78, "autonomie": 50},
        "Ford Kuga PHEV (Euro 6d)": {"consum_combustibil": 6.2, "consum_electric": 17, "emisii_tank": 82, "autonomie": 50},
        "Peugeot 308 HYBRID (Euro 6d)": {"consum_combustibil": 5.6, "consum_electric": 14, "emisii_tank": 76, "autonomie": 50},
        "VW Golf GTE (Euro 6d)": {"consum_combustibil": 5.9, "consum_electric": 15, "emisii_tank": 79, "autonomie": 50},
        "Audi A3 TFSI e (Euro 6d)": {"consum_combustibil": 5.7, "consum_electric": 14, "emisii_tank": 77, "autonomie": 50},
        "Kia Niro PHEV (Euro 6d)": {"consum_combustibil": 6.1, "consum_electric": 16, "emisii_tank": 81, "autonomie": 50},
        "Toyota RAV4 PHEV (Euro 6d)": {"consum_combustibil": 5.4, "consum_electric": 14, "emisii_tank": 74, "autonomie": 50}
    },
    "BEV": {
        "Tesla Model 3 Standard Range": {"consum": 14, "emisii_tank": 0},
        "Tesla Model Y Long Range": {"consum": 16, "emisii_tank": 0},
        "VW ID.3 Pro S": {"consum": 15, "emisii_tank": 0},
        "VW ID.4 GTX": {"consum": 18, "emisii_tank": 0},
        "Audi Q4 e-tron": {"consum": 17, "emisii_tank": 0},
        "BMW i4 eDrive40": {"consum": 16, "emisii_tank": 0},
        "Hyundai Kona Electric 64kWh": {"consum": 14, "emisii_tank": 0},
        "Kia EV6 GT-Line": {"consum": 16, "emisii_tank": 0},
        "Skoda Enyaq iV 80": {"consum": 16, "emisii_tank": 0},
        "Renault Megane E-Tech EV60": {"consum": 15, "emisii_tank": 0}
    },
    "FCEV": {
        "Toyota Mirai I": {
            "consum": 1
	},
	"Toyota Mirai II": {
            "consum": 0.9,
        },
        "Hyundai Nexo": {
            "consum": 1.0
        }
    }
}

# Specificații tehnice pentru fiecare model
specs_tehnice = {
    "HEV": {
        "Toyota Corolla Hybrid (Euro 6d)": {
            "An fabricatie": "2022",
            "Consum termic": "4.5",
            "Consum electric": "-",
            "Consum mixt": "4.1",
            "Cilindree": "1798",
            "Greutate totala": "1420",
            "Putere maxima": "140",
            "Cuplu maxim": "142"
        },
        "Toyota Prius (Euro 6)": {
            "An fabricatie": "2021",
            "Consum termic": "4.2",
            "Consum electric": "-",
            "Consum mixt": "3.9",
            "Cilindree": "1798",
            "Greutate totala": "1380",
            "Putere maxima": "122",
            "Cuplu maxim": "142"
        },
	 "Toyota Prius (Euro 5)": {
            "An fabricatie": "2021",
            "Consum termic": "4.2",
            "Consum electric": "-",
            "Consum mixt": "3.9",
            "Cilindree": "1798",
            "Greutate totala": "1380",
            "Putere maxima": "122",
            "Cuplu maxim": "142"
        },
 	"Toyota Prius (Euro 4)": {
            "An fabricatie": "2021",
            "Consum termic": "4.2",
            "Consum electric": "-",
            "Consum mixt": "3.9",
            "Cilindree": "1798",
            "Greutate totala": "1380",
            "Putere maxima": "122",
            "Cuplu maxim": "142"
        },
        "Honda Civic Hybrid (Euro 6d-TEMP)": {
            "An fabricatie": "2022",
            "Consum termic": "4.6",
            "Consum electric": "-",
            "Consum mixt": "4.3",
            "Cilindree": "1993",
            "Greutate totala": "1467",
            "Putere maxima": "135",
            "Cuplu maxim": "315"
        },
	 "Hyundai Ioniq Hybrid (Euro 6)": {
            "An fabricatie": "2022",
            "Consum termic": "4.6",
            "Consum electric": "-",
            "Consum mixt": "4.3",
            "Cilindree": "1993",
            "Greutate totala": "1467",
            "Putere maxima": "135",
            "Cuplu maxim": "315"
        },
 	"Lexus UX 250h (Euro 6d)": {
            "An fabricatie": "2022",
            "Consum termic": "4.6",
            "Consum electric": "-",
            "Consum mixt": "4.3",
            "Cilindree": "1993",
            "Greutate totala": "1467",
            "Putere maxima": "135",
            "Cuplu maxim": "315"
        },
 	"Ford Mondeo Hybrid (Euro 6d)": {
            "An fabricatie": "2022",
            "Consum termic": "4.6",
            "Consum electric": "-",
            "Consum mixt": "4.3",
            "Cilindree": "1993",
            "Greutate totala": "1467",
            "Putere maxima": "135",
            "Cuplu maxim": "315"
        },
 	"Toyota C-HR Hybrid (Euro 6d)": {
            "An fabricatie": "2022",
            "Consum termic": "4.6",
            "Consum electric": "-",
            "Consum mixt": "4.3",
            "Cilindree": "1993",
            "Greutate totala": "1467",
            "Putere maxima": "135",
            "Cuplu maxim": "315"
        },
 	"Suzuki Swace (Euro 6d)": {
            "An fabricatie": "2022",
            "Consum termic": "4.6",
            "Consum electric": "-",
            "Consum mixt": "4.3",
            "Cilindree": "1993",
            "Greutate totala": "1467",
            "Putere maxima": "135",
            "Cuplu maxim": "315"
        },
    },
   "PHEV": {
        "Mitsubishi Outlander PHEV (Euro 6d)": {
            "An fabricatie": "2021",
            "Consum termic": "6.0",
            "Consum electric": "18",
            "Consum mixt": "1.8",
            "Cilindree": "2360",
            "Greutate totala": "1995",
            "Putere maxima": "204",
            "Cuplu maxim": "332",
            "Capacitate baterie": "13.8"
        },
        "Volvo XC60 Recharge (Euro 6d)": {
            "An fabricatie": "2022",
            "Consum termic": "6.5",
            "Consum electric": "19",
            "Consum mixt": "2.1",
            "Cilindree": "1969",
            "Greutate totala": "2175",
            "Putere maxima": "340",
            "Cuplu maxim": "590",
            "Capacitate baterie": "11.6"
        },
	"BMW 330e (Euro 6d-TEMP)": {
            "An fabricatie": "2022",
            "Consum termic": "6.5",
            "Consum electric": "19",
            "Consum mixt": "2.1",
            "Cilindree": "1969",
            "Greutate totala": "2175",
            "Putere maxima": "340",
            "Cuplu maxim": "590",
            "Capacitate baterie": "11.6"
        },
	"Mercedes A 250 e (Euro 6d)": {
            "An fabricatie": "2022",
            "Consum termic": "6.5",
            "Consum electric": "19",
            "Consum mixt": "2.1",
            "Cilindree": "1969",
            "Greutate totala": "2175",
            "Putere maxima": "340",
            "Cuplu maxim": "590",
            "Capacitate baterie": "11.6"
        },
	"Ford Kuga PHEV (Euro 6d)": {
            "An fabricatie": "2022",
            "Consum termic": "6.5",
            "Consum electric": "19",
            "Consum mixt": "2.1",
            "Cilindree": "1969",
            "Greutate totala": "2175",
            "Putere maxima": "340",
            "Cuplu maxim": "590",
            "Capacitate baterie": "11.6"
        },
	"Peugeot 308 HYBRID (Euro 6d)": {
            "An fabricatie": "2022",
            "Consum termic": "6.5",
            "Consum electric": "19",
            "Consum mixt": "2.1",
            "Cilindree": "1969",
            "Greutate totala": "2175",
            "Putere maxima": "340",
            "Cuplu maxim": "590",
            "Capacitate baterie": "11.6"
        },
	"VW Golf GTE (Euro 6d)": {
            "An fabricatie": "2022",
            "Consum termic": "6.5",
            "Consum electric": "19",
            "Consum mixt": "2.1",
            "Cilindree": "1969",
            "Greutate totala": "2175",
            "Putere maxima": "340",
            "Cuplu maxim": "590",
            "Capacitate baterie": "11.6"
        },
	"Audi A3 TFSI e (Euro 6d)": {
            "An fabricatie": "2022",
            "Consum termic": "6.5",
            "Consum electric": "19",
            "Consum mixt": "2.1",
            "Cilindree": "1969",
            "Greutate totala": "2175",
            "Putere maxima": "340",
            "Cuplu maxim": "590",
            "Capacitate baterie": "11.6"
        },
	"Kia Niro PHEV (Euro 6d)": {
            "An fabricatie": "2022",
            "Consum termic": "6.5",
            "Consum electric": "19",
            "Consum mixt": "2.1",
            "Cilindree": "1969",
            "Greutate totala": "2175",
            "Putere maxima": "340",
            "Cuplu maxim": "590",
            "Capacitate baterie": "11.6"
        },
	"Toyota RAV4 PHEV (Euro 6d)": {
            "An fabricatie": "2022",
            "Consum termic": "6.5",
            "Consum electric": "19",
            "Consum mixt": "2.1",
            "Cilindree": "1969 cm³",
            "Greutate totala": "2175",
            "Putere maxima": "340",
            "Cuplu maxim": "590",
            "Capacitate baterie": "11.6"
        },
    },
    "BEV": {
        "Tesla Model 3 Standard Range": {
            "An fabricatie": "-",
            "Consum": "-",
            "Capacitate baterie": "-",
            "Greutate totala": "-",
            "Putere maxima": "-",
            "Cuplu maxim": "-",
            "Autonomie": "-"
        },
        "Tesla Model Y Long Range": {
            "An fabricatie": "-",
            "Consum": "-",
            "Capacitate baterie": "-",
            "Greutate totala": "-",
            "Putere maxima": "-",
            "Cuplu maxim": "-",
            "Autonomie": "-"
        },
        "VW ID.3 Pro S": {
            "An fabricatie": "-",
            "Consum": "-",
            "Capacitate baterie": "-",
            "Greutate totala": "-",
            "Putere maxima": "-",
            "Cuplu maxim": "-",
            "Autonomie": "-"
        },
 	"VW ID.4 GTX": {
            "An fabricatie": "-",
            "Consum": "-",
            "Capacitate baterie": "-",
            "Greutate totala": "-",
            "Putere maxima": "-",
            "Cuplu maxim": "-",
            "Autonomie": "-"
        },
 	"Audi Q4 e-tron": {
            "An fabricatie": "-",
            "Consum": "-",
            "Capacitate baterie": "-",
            "Greutate totala": "-",
            "Putere maxima": "-",
            "Cuplu maxim": "-",
            "Autonomie": "-"
        },
 	"Hyundai Kona Electric 64kWh": {
            "An fabricatie": "-",
            "Consum": "-",
            "Capacitate baterie": "-",
            "Greutate totala": "-",
            "Putere maxima": "-",
            "Cuplu maxim": "-",
            "Autonomie": "-"
        },
 	"Skoda Enyaq iV 80": {
            "An fabricatie": "-",
            "Consum": "-",
            "Capacitate baterie": "-",
            "Greutate totala": "-",
            "Putere maxima": "-",
            "Cuplu maxim": "-",
            "Autonomie": "-"
        },
 	"Renault Megane E-Tech EV60": {
            "An fabricatie": "-",
            "Consum": "-",
            "Capacitate baterie": "-",
            "Greutate totala": "-",
            "Putere maxima": "-",
            "Cuplu maxim": "-",
            "Autonomie": "-"
        },

    },
    "FCEV": {
        "Toyota Mirai I": {
            "An fabricatie": "-",
            "Consum": "-",
            "Capacitate rezervor hidrogen": "-",
            "Greutate totala": "-",
            "Putere maxima": "-",
            "Cuplu maxim": "-",
            "Autonomie": "-"
        },
	 "Toyota Mirai II": {
            "An fabricatie": "-",
            "Consum": "-",
            "Capacitate rezervor hidrogen": "-",
            "Greutate totala": "-",
            "Putere maxima": "-",
            "Cuplu maxim": "-",
            "Autonomie": "-"
        },
        "Hyundai Nexo": {
            "An fabricatie": "-",
            "Consum": "-",
            "Capacitate rezervor hidrogen": "-",
            "Greutate totala": "-",
            "Putere maxima": "-",
            "Cuplu maxim": "-",
            "Autonomie": "-"
        }
    }
}

# ---- FUNCȚIE CALCUL EMISII ----
def calculeaza_emisii(tip_vehicul, model, tara, distanta, **kwargs):
    # Calculează emisii medii pentru țara selectată
    emisii_medii_tara = sum(tari[tara][sursa] * coef_emisii[sursa] 
                           for sursa in tari[tara]) / 100
    
    if tip_vehicul == "HEV":
        date = modele_vehicule["HEV"][model]
        emisii_per_litru=560
        emisii_well = date["consum"] / 100 * emisii_per_litru * distanta
        emisii_tank = date["emisii_tank"] * distanta
        return {
            "Well-to-Tank": emisii_well,
            "Tank-to-Wheel": emisii_tank,
            "Total": emisii_well + emisii_tank
        }
    
    elif tip_vehicul == "PHEV":
        date = modele_vehicule["PHEV"][model]
        emisii_per_litru = 560  # gCO₂/litru pentru benzină
    
        if distanta <= date["autonomie"]:
            # Tot traseul este parcurs electric
            emisii_well = (date["consum_electric"] / 100 * distanta) * (emisii_medii_tara / 100)
        else:
            emisii_well = (date["consum_electric"] / 100 * date["autonomie"]) * emisii_medii_tara + (date["consum_combustibil"] / 100 * (distanta - date["autonomie"]) * emisii_per_litru )     

        emisii_tank = date["emisii_tank"] * distanta  
        return {
            "Well-to-Tank": emisii_well,
            "Tank-to-Wheel": emisii_tank,
            "Total": emisii_well + emisii_tank
        }

    elif tip_vehicul == "BEV":
        date = modele_vehicule["BEV"][model]
        emisii_well = (date["consum"] * distanta) * (emisii_medii_tara/100)
        emisii_tank = 0
        return {
            "Well-to-Tank": emisii_well,
            "Tank-to-Wheel": emisii_tank,
            "Total": emisii_well + emisii_tank
        }
    
    elif tip_vehicul == "FCEV":
        date = modele_vehicule["FCEV"][model]
        tip_hidrogen = kwargs.get("tip_hidrogen", "Gri")  

        emisii_tip_hidrogen = emisii_hidrogen[tip_hidrogen]  
        consum = date["consum"]  # consum vehicul în kg H₂ / 100 km

        emisii_well = (consum / 100) * emisii_tip_hidrogen * distanta  
        emisii_tank = 0  # Nu există emisii TTW la FCEV

        return {
            "Well-to-Tank": emisii_well,
            "Tank-to-Wheel": emisii_tank,
            "Total": emisii_well + emisii_tank
        }


# ---- INTERFAȚA UTILIZATOR ----
st.title('Analiză Well-to-Wheel')

# 1. Selectare țară cu afișare mix energetic
tara_selectata = st.selectbox("Locație pentru analiză:", options=list(tari.keys()))
st.write(f"**Pondere generare energie electrica pentru {tara_selectata}:**")
for sursa, procent in tari[tara_selectata].items():
    st.write(f"- {sursa}: {procent}% (emisii: {coef_emisii[sursa]} CO₂/kWh)")

# 2. Selectare vehicule pentru comparație
st.header("Vehicule pentru comparație")

cols = st.columns(4)
vehicule_selectate = {}

with cols[0]:  # HEV
    st.subheader("HEV")
    if st.checkbox("Adaugă HEV", key="hev_check"):
        model = st.selectbox("Selectează autovehicul HEV", options=list(modele_vehicule["HEV"].keys()))
        vehicule_selectate["HEV"] = {"model": model}
        
        # Afișare specificații tehnice
        specs = specs_tehnice["HEV"][model]
        st.write("**Specificații tehnice vehicul selectat:**")
        st.write(f"- An fabricație: {specs['An fabricatie']}")
        st.write(f"- Consum termic: {specs['Consum termic']} l/100km")
        st.write(f"- Consum electric: {specs['Consum electric']} kWh/100km")
        st.write(f"- Consum mixt: {specs['Consum mixt']} l/100km")
        st.write(f"- Cilindree: {specs['Cilindree']} cm³")
        st.write(f"- Greutate totală: {specs['Greutate totala']} kg")
        st.write(f"- Putere maximă: {specs['Putere maxima']} kW")
        st.write(f"- Cuplu maxim: {specs['Cuplu maxim']} Nm")
        st.markdown('</div>', unsafe_allow_html=True)

with cols[1]:  # PHEV
    st.subheader("PHEV")
    if st.checkbox("Adaugă PHEV", key="phev_check"):
        model = st.selectbox("Selectează autovehicul PHEV", options=list(modele_vehicule["PHEV"].keys()))
        vehicule_selectate["PHEV"] = {"model": model}
        
        # Afișare specificații tehnice
        specs = specs_tehnice["PHEV"][model]
        st.write("**Specificații tehnice vehicul selectat:**")
        st.write(f"- An fabricație: {specs['An fabricatie']}")
        st.write(f"- Consum termic: {specs['Consum termic']} l/100km")
        st.write(f"- Consum electric: {specs['Consum electric']} kWh/100km")
        st.write(f"- Consum mixt: {specs['Consum mixt']} l/100km")
        st.write(f"- Cilindree: {specs['Cilindree']} cm³")
        st.write(f"- Capacitate baterie: {specs['Capacitate baterie']} kWh")
        st.write(f"- Greutate totală: {specs['Greutate totala']} kg")
        st.write(f"- Putere maximă: {specs['Putere maxima']} kW")
        st.write(f"- Cuplu maxim: {specs['Cuplu maxim']} Nm")
        st.markdown('</div>', unsafe_allow_html=True)

with cols[2]:  # BEV
    st.subheader("BEV")
    if st.checkbox("Adaugă BEV", key="bev_check"):
        model = st.selectbox("Selectează autovehicul BEV", options=list(modele_vehicule["BEV"].keys()))
        vehicule_selectate["BEV"] = {"model": model}
        
        # Afișare specificații tehnice
        specs = specs_tehnice["BEV"][model]
        st.write("**Specificații tehnice vehicul selectat:**")
        st.write(f"- An fabricație: {specs['An fabricatie']}")
        st.write(f"- Consum: {specs['Consum']} kWh/100km")
        st.write(f"- Capacitate baterie: {specs['Capacitate baterie']} kWh")
        st.write(f"- Greutate totală: {specs['Greutate totala']} kg")
        st.write(f"- Putere maximă: {specs['Putere maxima']} kW")
        st.write(f"- Cuplu maxim: {specs['Cuplu maxim']} kW")
        st.write(f"- Autonomie: {specs['Autonomie']} km")
        st.markdown('</div>', unsafe_allow_html=True)

with cols[3]:  # FCEV
    st.subheader("FCEV")
    if st.checkbox("Adaugă FCEV", key="fcev_check"):
        model = st.selectbox("Selectează autovehicul FCEV", options=list(modele_vehicule["FCEV"].keys()))
        
        tip_hidrogen = st.radio("Tip hidrogen", 
                                options=list(emisii_hidrogen.keys()),  
                                key=f"hidrogen_{model}")
        
        vehicule_selectate["FCEV"] = {
            "model": model,
            "tip_hidrogen": tip_hidrogen
        }
        
        # Afișează emisiile per kg H₂
        st.markdown(f" **Emisii CO₂ hidrogen {tip_hidrogen}:** {emisii_hidrogen[tip_hidrogen]} g CO₂ / kg H₂")

        # Afișare specificații tehnice
        specs = specs_tehnice["FCEV"][model]
        st.write("**Specificații tehnice vehicul selectat:**")
        st.write(f"- An fabricație: {specs['An fabricatie']}")
        st.write(f"- Consum: {specs['Consum']} kg/100km")
        st.write(f"- Capacitate rezervor hidrogen: {specs['Capacitate rezervor hidrogen']} kg")
        st.write(f"- Greutate totală: {specs['Greutate totala']} kg")
        st.write(f"- Putere maximă: {specs['Putere maxima']} kW")
        st.write(f"- Cuplu maxim: {specs['Cuplu maxim']} Nm")
        st.write(f"- Autonomie: {specs['Autonomie']} km")
        st.markdown('</div>', unsafe_allow_html=True)

# 3. Parametri comuni
distanta = st.slider("Distanță parcursă [km]", 10, 500, 100, key="distanta_comp")

# 4. Calcule și afișare rezultate
if vehicule_selectate:
    st.header("Rezultate emisii CO₂")
    
    # Calcul emisii pentru fiecare vehicul
    rezultate = {}
    for tip_vehicul, config in vehicule_selectate.items():
        emisii = calculeaza_emisii(
            tip_vehicul=tip_vehicul,
            model=config["model"],
            tara=tara_selectata,
            distanta=distanta,
            **{k:v for k,v in config.items() if k != "model"}
        )
        rezultate[f"{tip_vehicul} - {config['model']}"] = emisii
    
    # Creare DataFrame pentru afișare
    df = pd.DataFrame.from_dict(rezultate, orient='index')
    st.table(
    df.style
    .format("{:.0f} gCO₂")
    .set_properties(**{
        'background-color': 'white',
        'color': 'black',
        'text-align': 'center'  
    })
)
    # Grafic comparație
    fig = go.Figure()
    
    # Culori distincte pentru fiecare vehicul
    culori = px.colors.qualitative.Plotly
    
    for i, (vehicul, emisii) in enumerate(rezultate.items()):
        fig.add_trace(go.Bar(
            x=["Well-to-Tank", "Tank-to-Wheel", "Well-to-Wheel"],
            y=[emisii["Well-to-Tank"], emisii["Tank-to-Wheel"], emisii["Total"]],
            name=vehicul,
            marker_color=culori[i % len(culori)],
            text=[f"{val:.0f}g" for val in [emisii["Well-to-Tank"], emisii["Tank-to-Wheel"], emisii["Total"]]],
            textposition='inside',
            textfont=dict(color='black')
        ))
    
    fig.update_layout(
        barmode='group',
        xaxis_title=f"Comparație emisii CO₂ Well-to-Wheel pe distanța de {distanta}km în {tara_selectata}",
   	xaxis_title_font=dict(color='black', size=30),        
        yaxis_title="Emisii CO₂ [g]",
   	yaxis_title_font=dict(color='black', size=20),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='black', size=17),
 	xaxis=dict(
        	tickfont=dict(color='black', size=20)
    	),
    	yaxis=dict(
       		tickfont=dict(color='black', size=16)
    	),
        legend=dict(
            font=dict(color='black', size=17),
            orientation="h",
            yanchor="bottom",
            y=1,
            xanchor="right",
            x=1
        ),
        height=600,
        margin=dict(l=50, r=50, b=100, t=100, pad=4)
    )
    
    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("Niciun vehicul selectat")

st.markdown(
    """
    <div style="
        display: flex;
        justify-content: center;
        margin: 50px 0 20px 0;
        width: 100%;
    ">
    """, 
    unsafe_allow_html=True
)

try:
    st.image("sigla_ARMM.png", width=150)
except:
    st.warning("Sigla ARMM nu a fost găsită")

st.markdown("</div>", unsafe_allow_html=True)