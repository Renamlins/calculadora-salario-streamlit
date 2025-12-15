import streamlit as st
import pandas as pd

# Configuração da Página
st.set_page_config(page_title="Calculadora de Salário Líquido", page_icon="💰")

# Título e Estilo
st.title("💰 Calculadora de Salário Líquido & 13º")
st.write("Simule seus descontos mensais e previsões de Décimo Terceiro (CLT).")

# --- BARRA LATERAL (INPUTS) ---
with st.sidebar:
    st.header("📝 Dados Financeiros")
    salario_bruto = st.number_input("Salário Bruto (R$)", min_value=0.0, value=3000.00, step=100.00)
    dependentes = st.number_input("Número de Dependentes", min_value=0, value=0, step=1)
    
    st.subheader("Outros Descontos (Opcional)")
    desc_vr = st.number_input("Vale Refeição (R$)", min_value=0.0, value=0.0)
    desc_vt = st.number_input("Vale Transporte (R$)", min_value=0.0, value=0.0)
    desc_plano = st.number_input("Plano de Saúde (R$)", min_value=0.0, value=0.0)

# --- FUNÇÕES DE CÁLCULO (Regras 2024/2025) ---

def calcular_inss(bruto):
    # Tabela Progressiva INSS 2024
    teto = 7786.02
    faixas = [
        (1412.00, 0.075),
        (2666.68, 0.09),
        (4000.03, 0.12),
        (7786.02, 0.14)
    ]
    
    desconto = 0.0
    base_anterior = 0.0
    
    salario_calc = min(bruto, teto)
    
    for limite, aliquota in faixas:
        if salario_calc > base_anterior:
            base_faixa = min(salario_calc, limite) - base_anterior
            desconto += base_faixa * aliquota
            base_anterior = limite
        else:
            break
            
    return desconto

def calcular_irrf(base_calculo):
    # Tabela IRRF (Dedução simplificada não aplicada aqui para fins didáticos, usando padrão)
    # Faixas de Renda x Alíquota x Dedução
    faixas_ir = [
        (2259.20, 0.0, 0.0),
        (2826.65, 0.075, 169.44),
        (3751.05, 0.15, 381.44),
        (4664.68, 0.225, 662.77),
        (float('inf'), 0.275, 896.00)
    ]
    
    imposto = 0.0
    for limite, aliquota, deducao in faixas_ir:
        if base_calculo <= limite:
            imposto = (base_calculo * aliquota) - deducao
            break
        elif limite == float('inf'): # Acima da última faixa
            imposto = (base_calculo * aliquota) - deducao
            
    return max(0.0, imposto)

# --- BOTÃO CALCULAR ---
if st.button("Calcular Agora 🚀"):
    
    # 1. CÁLCULO MENSAL
    inss_mensal = calcular_inss(salario_bruto)
    deducao_dependente = dependentes * 189.59
    base_irrf_mensal = salario_bruto - inss_mensal - deducao_dependente
    irrf_mensal = calcular_irrf(base_irrf_mensal)
    
    total_descontos = inss_mensal + irrf_mensal + desc_vr + desc_vt + desc_plano
    salario_liquido = salario_bruto - total_descontos
    
    # 2. CÁLCULO 13º SALÁRIO
    # 1ª Parcela: 50% do bruto (sem descontos, geralmente pagos em Nov)
    decimo_primeira = salario_bruto / 2
    
    # 2ª Parcela: Bruto - INSS(sobre total) - IRRF(sobre total) - Valor 1ª Parcela
    inss_13 = calcular_inss(salario_bruto) # INSS é calculado sobre o valor CHEIO do 13º
    base_irrf_13 = salario_bruto - inss_13 - deducao_dependente
    irrf_13 = calcular_irrf(base_irrf_13) # IRRF exclusivo na fonte sobre o 13º (tributação exclusiva)
    
    decimo_segunda = salario_bruto - inss_13 - irrf_13 - decimo_primeira

    # --- EXIBIÇÃO DOS RESULTADOS ---
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📅 Cálculo Mensal")
        st.markdown(f"**Salário Bruto:** R$ {salario_bruto:,.2f}")
        st.markdown(f"➖ INSS: R$ {inss_mensal:,.2f}")
        st.markdown(f"➖ IRRF: R$ {irrf_mensal:,.2f}")
        st.markdown(f"➖ Outros (VR/VT/Saúde): R$ {desc_vr + desc_vt + desc_plano:,.2f}")
        st.success(f"**💰 Salário Líquido: R$ {salario_liquido:,.2f}**")

    with col2:
        st.subheader("🎄 Décimo Terceiro (Previsão)")
        
        st.info(f"**1ª Parcela (Nov):** R$ {decimo_primeira:,.2f}")
        st.markdown("*50% do bruto, sem descontos.*")
        
        st.warning(f"**2ª Parcela (Dez):** R$ {decimo_segunda:,.2f}")
        
        with st.expander("Ver detalhe dos descontos do 13º"):
            st.write(f"O desconto ocorre cheio na 2ª parcela:")
            st.write(f"➖ INSS s/ 13º Total: R$ {inss_13:,.2f}")
            st.write(f"➖ IRRF s/ 13º Total: R$ {irrf_13:,.2f}")
            st.write(f"➖ Dedução da 1ª Parcela: R$ {decimo_primeira:,.2f}")

    # Gráfico simples de distribuição
    st.divider()
    st.subheader("Para onde vai seu salário?")
    dados_grafico = {
        'Categoria': ['Líquido', 'INSS', 'IRRF', 'Outros'],
        'Valor': [salario_liquido, inss_mensal, irrf_mensal, desc_vr + desc_vt + desc_plano]
    }
    st.bar_chart(pd.DataFrame(dados_grafico).set_index('Categoria'))

else:
    st.info("Preencha os dados na barra lateral e clique em calcular.")
