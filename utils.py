import PyPDF2
import re
import json

def converter_pdf_para_otimizado(arquivo_pdf, formato="markdown"):
    """
    Lê um PDF e converte para Markdown ou JSON estruturado usando heurística (Zero IA).
    Foco: Redução drástica de tokens para envio à OpenAI.
    """
    leitor = PyPDF2.PdfReader(arquivo_pdf)
    texto_completo = ""

    # Extração bruta
    for pagina in leitor.pages:
        texto_completo += pagina.extract_text() + "\n"

    linhas = texto_completo.split('\n')
    cv_estruturado = {"cabecalho": [], "secoes": {}}
    secao_atual = "cabecalho"

    # Palavras-chave comuns em currículos brasileiros
    keywords_secoes = [
        'EXPERIÊNCIA', 'EXPERIÊNCIAS', 'EDUCAÇÃO', 'FORMAÇÃO', 
        'RESUMO', 'IDIOMAS', 'COMPETÊNCIAS', 'HABILIDADES', 'CONQUISTAS'
    ]

    for linha in linhas:
        linha_limpa = linha.strip()
        if not linha_limpa:
            continue

        # Detecta nova seção (texto curto e em maiúsculas que bate com as keywords)
        linha_upper = linha_limpa.upper()
        is_secao = any(linha_upper == kw or linha_upper.startswith(kw) for kw in keywords_secoes)

        if is_secao and len(linha_limpa) < 35:
            secao_atual = linha_upper
            cv_estruturado["secoes"][secao_atual] = []
        else:
            if secao_atual == "cabecalho":
                cv_estruturado["cabecalho"].append(linha_limpa)
            else:
                if secao_atual not in cv_estruturado["secoes"]:
                    cv_estruturado["secoes"][secao_atual] = []
                cv_estruturado["secoes"][secao_atual].append(linha_limpa)

    # Retorno em JSON (se preferir estruturação rígida)
    if formato == "json":
        return json.dumps(cv_estruturado, ensure_ascii=False, indent=2)

    # Retorno em Markdown (Recomendado: Maior economia de tokens)
    md_linhas = []
    if cv_estruturado["cabecalho"]:
        md_linhas.append("### INFORMAÇÕES PESSOAIS")
        md_linhas.extend(cv_estruturado["cabecalho"])
        md_linhas.append("")

    for secao, conteudo in cv_estruturado["secoes"].items():
        md_linhas.append(f"### {secao}")
        for item in conteudo:
            # Padroniza bullet points nativos do PDF para o padrão Markdown
            if item.startswith('•') or item.startswith('-') or item.startswith('▪'):
                md_linhas.append(f"- {item[1:].strip()}")
            else:
                # Remove espaços duplos no meio do texto
                item_limpo = re.sub(r'\s+', ' ', item)
                md_linhas.append(item_limpo)
        md_linhas.append("")

    return "\n".join(md_linhas)