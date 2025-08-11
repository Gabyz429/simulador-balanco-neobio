
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Simulador de Proteína no DDGS", page_icon="🧪", layout="wide")

# ---- Helpers ----
def calc_ddgs(
    wdg_flow_th, wdg_solids_pct, wdg_protein_ds_pct,
    syrup_flow_th, syrup_solids_pct, syrup_protein_ds_pct,
    syrup_cut_pct, ddgs_final_moist_pct, ds_losses_pct
):
    # Convert percentages
    S_wdg = wdg_solids_pct / 100.0
    PB_wdg = wdg_protein_ds_pct / 100.0
    S_cds = syrup_solids_pct / 100.0
    PB_cds = syrup_protein_ds_pct / 100.0
    cut = 1.0 - (syrup_cut_pct / 100.0)
    H = ddgs_final_moist_pct / 100.0
    losses = ds_losses_pct / 100.0

    # DS and protein of each stream
    ds_wdg = wdg_flow_th * S_wdg
    prot_wdg = ds_wdg * PB_wdg

    ds_cds_base = syrup_flow_th * S_cds
    ds_cds = ds_cds_base * cut  # applying cut on as-fed (equivalent if solids% stays the same)
    prot_cds = ds_cds * PB_cds

    ds_in = ds_wdg + ds_cds
    ds_out = ds_in * (1.0 - losses)  # DS out of dryer
    prot_tot = prot_wdg + prot_cds  # assuming no protein loss

    # Outputs
    ddgs_ds_th = ds_out
    ddgs_af_th = ddgs_ds_th / (1.0 - H) if (1.0 - H) > 0 else float("nan")
    pb_ds_pct = (prot_tot / ddgs_ds_th) * 100.0 if ddgs_ds_th > 0 else float("nan")
    pb_af_pct = (prot_tot / ddgs_af_th) * 100.0 if ddgs_af_th > 0 else float("nan")

    return {
        "ds_wdg_th": ds_wdg,
        "prot_wdg_th": prot_wdg,
        "ds_cds_th": ds_cds,
        "prot_cds_th": prot_cds,
        "ddgs_ds_th": ddgs_ds_th,
        "ddgs_af_th": ddgs_af_th,
        "prot_tot_th": prot_tot,
        "pb_ds_pct": pb_ds_pct,
        "pb_af_pct": pb_af_pct,
        "ds_losses_th": ds_in - ds_out,
        "ds_in_th": ds_in,
    }

# ---- Sidebar inputs ----
st.sidebar.title("Entradas")
st.sidebar.caption("Use os campos abaixo para simular cenários.")

with st.sidebar:
    st.subheader("Bolo úmido (WDG)")
    wdg_flow_th = st.number_input("Vazão WDG (t/h)", min_value=0.0, value=50.0, step=0.5)
    wdg_solids_pct = st.number_input("Sólidos WDG (%)", min_value=0.0, max_value=100.0, value=38.0, step=0.1)
    wdg_protein_ds_pct = st.number_input("Proteína WDG (em DS, %)", min_value=0.0, max_value=100.0, value=24.0, step=0.1)

    st.subheader("Xarope sem óleo (CDS)")
    syrup_flow_th = st.number_input("Vazão Xarope (t/h)", min_value=0.0, value=26.0, step=0.5)
    syrup_solids_pct = st.number_input("Sólidos Xarope (%)", min_value=0.0, max_value=100.0, value=30.0, step=0.1)
    syrup_protein_ds_pct = st.number_input("Proteína Xarope (em DS, %)", min_value=0.0, max_value=100.0, value=35.0, step=0.1)

    st.subheader("Operação do secador")
    syrup_cut_pct = st.number_input("Redução de xarope (%)", min_value=0.0, max_value=100.0, value=30.0, step=1.0)
    ddgs_final_moist_pct = st.number_input("Umidade final do DDGS (%)", min_value=0.0, max_value=40.0, value=12.0, step=0.5)
    ds_losses_pct = st.number_input("Perdas de DS no secador/ciclones (%)", min_value=0.0, max_value=20.0, value=0.0, step=0.1)

st.title("🧪 Simulador de Proteína no DDGS")
st.write("Modelo simples em base de sólidos. Ajuste as entradas na barra lateral e veja os resultados.")

# ---- Run calc ----
res = calc_ddgs(
    wdg_flow_th, wdg_solids_pct, wdg_protein_ds_pct,
    syrup_flow_th, syrup_solids_pct, syrup_protein_ds_pct,
    syrup_cut_pct, ddgs_final_moist_pct, ds_losses_pct
)

# ---- Header metrics ----
col1, col2, col3, col4 = st.columns(4)
col1.metric("DDGS (t/h, as-fed)", f"{res['ddgs_af_th']:.2f}")
col2.metric("DS no DDGS (t/h)", f"{res['ddgs_ds_th']:.2f}")
col3.metric("Proteína no DDGS (% DS)", f"{res['pb_ds_pct']:.2f}%")
col4.metric("Proteína no DDGS (% as-fed)", f"{res['pb_af_pct']:.2f}%")

# ---- Details ----
st.subheader("Detalhamento do balanço")
df = pd.DataFrame([
    ["WDG", wdg_flow_th, wdg_solids_pct, res["ds_wdg_th"], wdg_protein_ds_pct, res["prot_wdg_th"]],
    ["Xarope (após corte)", syrup_flow_th * (1.0 - syrup_cut_pct/100.0), syrup_solids_pct, res["ds_cds_th"], syrup_protein_ds_pct, res["prot_cds_th"]],
], columns=["Corrente", "Vazão (t/h AF)", "Sólidos (%)", "DS (t/h)", "PB em DS (%)", "Proteína (t/h)"])
st.dataframe(df, use_container_width=True)

st.caption(
    "AF = as-fed (como alimentado). DS = base seca. "
    "O corte de xarope é aplicado à vazão as-fed; se a % de sólidos do xarope variar com o corte, ajuste manualmente."
)

# ---- Scenario: sem xarope ----
st.subheader("Cenário comparativo: sem xarope")
res_sem = calc_ddgs(
    wdg_flow_th, wdg_solids_pct, wdg_protein_ds_pct,
    syrup_flow_th, syrup_solids_pct, syrup_protein_ds_pct,
    100.0, ddgs_final_moist_pct, ds_losses_pct
)

colA, colB, colC, colD = st.columns(4)
colA.metric("DDGS (t/h) sem xarope", f"{res_sem['ddgs_af_th']:.2f}")
colB.metric("Proteína (% as-fed) sem xarope", f"{res_sem['pb_af_pct']:.2f}%")
colC.metric("Δ DDGS (t/h)", f"{res['ddgs_af_th'] - res_sem['ddgs_af_th']:+.2f}")
colD.metric("Δ Proteína (% as-fed)", f"{res['pb_af_pct'] - res_sem['pb_af_pct']:+.2f} pp")

# ---- Notes ----
with st.expander("Assunções e notas"):
    st.markdown(\"\"\"
    - Balanço em base de sólidos; proteína é considerada conservativa (sem degradação térmica).
    - Perdas de **sólidos** podem ser colocadas como % do total de DS alimentado ao secador.
    - A redução de xarope é aplicada na **vazão as-fed** e, por padrão, assume a mesma % de sólidos do xarope.
    - Ajuste conforme os dados reais de laboratório (PB em DS das correntes, sólidos, umidade final).
    - Unidades: t/h para fluxos, % para frações mássicas.
    \"\"\")
