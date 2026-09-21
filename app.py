import streamlit as st
from openai import OpenAI
from utils import ler_pdf, ler_docx

# Configuração do cliente OpenAI apontando para o seu 9Router local
client = OpenAI(
    base_url="http://192.168.68.107:20128/v1",
    api_key="sk-dummy" # O 9Router gerencia as chaves reais no painel dele
)

st.set_page_config(page_title="ATS AI Optimizer", layout="wide")
st.title("🎯 Otimizador de Currículo ATS (Powered by 9Router)")

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Descrição da Vaga")
    vaga_texto = st.text_area("Cole os requisitos da vaga aqui:", height=300)

with col2:
    st.subheader("2. Seu Currículo Atual")
    arquivo_cv = st.file_uploader("Envie seu CV (PDF ou DOCX)", type=["pdf", "docx"])

if st.button("Analisar e Otimizar CV"):
    if vaga_texto and arquivo_cv:
        with st.spinner("Processando via 9Router..."):
            # Extração do texto
            if arquivo_cv.name.endswith('.pdf'):
                cv_texto = ler_pdf(arquivo_cv)
            else:
                cv_texto = ler_docx(arquivo_cv)

            # Engenharia de Prompt
            prompt_sistema = """
            Você é um especialista em ATS e recrutamento tech.
            Sua missão é comparar o CV do candidato com a vaga e reescrever o CV para aumentar o match.
            REGRA ABSOLUTA: NÃO INVENTE NENHUMA EXPERIÊNCIA, FERRAMENTA OU FORMAÇÃO QUE NÃO ESTEJA NO CV ORIGINAL.
            Apenas destaque, reorganize e utilize sinônimos adequados para dar match com a vaga.

            Retorne EXATAMENTE neste formato:
            SCORE ORIGINAL: [0-100]%
            SCORE ADAPTADO: [0-100]%
            JUSTIFICATIVA: [Breve explicação das mudanças]
            ---CV_INICIO---
            [Texto completo do novo CV em Markdown]
            ---CV_FIM---
            """

            try:
                # Chamada para o 9Router
                resposta = client.chat.completions.create(
                    model="auto", # O 9Router vai decidir o melhor modelo baseado na sua config
                    messages=[
                        {"role": "system", "content": prompt_sistema},
                        {"role": "user", "content": f"VAGA:\n{vaga_texto}\n\nCV ORIGINAL:\n{cv_texto}"}
                    ],
                    temperature=0.2
                )

                resultado = resposta.choices[0].message.content
                st.success("Otimização concluída!")
                st.markdown(resultado.split("---CV_INICIO---")[0]) # Mostra os scores

                cv_otimizado = resultado.split("---CV_INICIO---")[1].split("---CV_FIM---")[0]

                # Fase 4: Exportação (Botão de Download em Markdown)
                st.download_button(
                    label="💾 Baixar CV Otimizado (Markdown)",
                    data=cv_otimizado,
                    file_name="cv_otimizado.md",
                    mime="text/markdown"
                )

            except Exception as e:
                st.error(f"Erro na comunicação com o 9Router: {e}")
    else:
        st.warning("Preencha a vaga e envie o currículo.")