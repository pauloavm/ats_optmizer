import PyPDF2
import docx

def ler_pdf(arquivo):
    leitor = PyPDF2.PdfReader(arquivo)
    texto = ""
    for pagina in leitor.pages:
        texto += pagina.extract_text()
    return texto

def ler_docx(arquivo):
    doc = docx.Document(arquivo)
    return "\n".join([paragrafo.text for paragrafo in doc.paragraphs])