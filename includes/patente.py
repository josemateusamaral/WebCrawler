from bs4 import BeautifulSoup
from lxml import etree
from includes.utils import *
import time

# achar tabela na pagina de marcar usa
def findTablePatentes(nomeTabela,dom):
    for i in range(50):
        try:
            if findXpath(f'/html/body/form/div[2]/div/div[{i}]/div',dom).find('label').find('font').get_text(strip=True) == nomeTabela:
                return findXpath(f'/html/body/form/div[2]/div/div[{i}]/div/div/table/tbody',dom)
        except: pass
    return None



#funcao para extrair os dados de um patente
def extrairDadosPatente(pagina,resposta):

    #converter pagina para o formato do beautifulsoup4
    soup = BeautifulSoup(pagina, 'html.parser')
    body = soup.find('body')
    dom = etree.HTML(str(body))



    #extrair dados gerais
    table = etree.HTML(str(findXpath("/html/body/form/div[2]/div/table[2]",dom)))
    linhas = table[0][0]
    dadosGerais = {}
    for index,linha in enumerate(linhas):
        if not index: continue
        coluna1 = BeautifulSoup(etree.tostring(linha[0], pretty_print=True).decode('utf-8'),'html.parser').get_text(strip=True)

        if coluna1 == '(30)Prioridade Unionista:':
            pais = BeautifulSoup(etree.tostring(linha[1][0][1][0], pretty_print=True).decode('utf-8'),'html.parser').get_text(strip=True)
            numero = BeautifulSoup(etree.tostring(linha[1][0][1][1], pretty_print=True).decode('utf-8'),'html.parser').get_text(strip=True)
            data = BeautifulSoup(etree.tostring(linha[1][0][1][2], pretty_print=True).decode('utf-8'),'html.parser').get_text(strip=True)
            dadosGerais[coluna1] = {
                "(33)pais":pais,
                "(32)data":data,
                "(31)numero":numero
            }

        elif coluna1 == '(51)Classificação IPC:':
            coluna2 = BeautifulSoup(etree.tostring(linha[1], pretty_print=True).decode('utf-8'),'html.parser')
            osA = coluna2.find_all('a')
            texto = ""
            for i in osA:
                textoLink = i.get_text(strip=True)
                if textoLink == "":
                    continue
                texto += textoLink
            dadosGerais[coluna1] = texto

        else:
            coluna2 = BeautifulSoup(etree.tostring(linha[1], pretty_print=True).decode('utf-8'),'html.parser').get_text(strip=True)
            dadosGerais[coluna1] = coluna2

    resposta["dadosGerais"] = dadosGerais



    #extrair peticoes
    peticoes = {}
    table = findTablePatentes("Petições",dom)
    tabela = 8
    for i in range(50):
        try:
            nome = findXpath(f"/html/body/form/div[2]/div/div[{i}]/div/div/table/tbody/tr[1]/td/label",dom).get_text(strip=True)
            if nome == "Serviços":
                tabela = i
                break
        except: pass
    tabelaOBJ =  etree.HTML(str(findXpath(f"/html/body/form/div[2]/div/div[{tabela}]/div/div/table",dom)))[0][0][1]
    atual = ""
    for index,linha in enumerate(tabelaOBJ):
        i = index
        coluna1 = etreeToSoup(linha[0]).get_text(strip=True)
        if len(linha[0]) == 1:
            atual = coluna1
            peticoes[atual] = []
            continue

        descricaoServicos = etreeToSoup(linha[0][0]).get_text(strip=True)
        #falta fazer o pagamentoServicos que fica na coluna 1 
        protocolo = etreeToSoup(linha[2][0]).get_text(strip=True)
        dataDados = etreeToSoup(linha[3][0]).get_text(strip=True)
        imagem1 = etreeToSoup(linha[4][0]).get_text(strip=True)
        imagem2 = etreeToSoup(linha[5][0]).get_text(strip=True)
        imagem3 = etreeToSoup(linha[6][0]).get_text(strip=True)
        cliente = etreeToSoup(linha[7][0]).get_text(strip=True)
        data = {}
        data["descricao"] = descricaoServicos
        #data["pagamento"] = pagamentoServicos
        data["protocolo"] = protocolo
        data["data"] = dataDados
        data["imagem1"] = imagem1
        data["imagem2"] = imagem2
        data["imagem3"] = imagem3
        data["cliente"] = cliente
        peticoes[atual].append(data)    
    
    resposta["peticoes"] = peticoes



    # estrair as anuidades
    tableIndex = 0
    for i in range(50):
        labelTable = findXpath(f"/html/body/form/div[2]/div/div[{i}]/div/label/font",dom)
        if labelTable == None:
            continue
        texto = labelTable.get_text(strip=True)
        if "Anuidades" in texto:
            tableIndex = i
            break    
    tabelaAnuidades = findXpath(f"/html/body/form/div[2]/div/div[{tableIndex}]/div/div/table",dom)
    anuidades = {}
    if tabelaAnuidades != None:
        arvoreTabela = etree.HTML(str(tabelaAnuidades))[0][0]
        cabecalhos = arvoreTabela[0][0]
        for index,i in enumerate(cabecalhos):
            if not len(i) or not index: continue

            #extrair ordinário
            inicioOrdinario = arvoreTabela[1][1][index]
            inicioOrdinarioSOUP = etreeToSoup(inicioOrdinario)
            colunas = inicioOrdinarioSOUP.find_all('td')
            inicioORD = colunas[1].get_text(strip=True)
            fimORD = colunas[2].get_text(strip=True)

            #extrair extraordinario
            inicioExtraordinario = arvoreTabela[1][2][index]
            inicioExtraordinarioSOUP = etreeToSoup(inicioExtraordinario)
            colunas = inicioExtraordinarioSOUP.find_all('td')
            inicioEXTRA = colunas[1].get_text(strip=True)
            fimEXTRA = colunas[2].get_text(strip=True)

            anuidades[etreeToSoup(i[0]).get_text(strip=True)] = {
                "ordinario":{
                    "inicio":inicioORD,
                    "fim":fimORD
                },
                "extraordinario":{
                    "inicio":inicioEXTRA,
                    "fim":fimEXTRA
                }
            }
    resposta["anuidades"] = anuidades
    


    #extrair publicacoes publicacoes
    table = findTablePatentes("Publicações",dom)
    linhas = table.find_all("tr")
    publicacoes = []
    ok = False
    for index,i in enumerate(linhas):
        
        colunas = i.find_all('td')
        if len(colunas) < 6:
            continue   
        
        rpi = colunas[0].text.strip()
        data_rpi = colunas[1].text.strip()
        despacho = colunas[2].find('font').text.strip()
        certificado = colunas[7].get_text(strip=True)
        interior = colunas[8].find('font').text.strip()
        complemento_despacho = colunas[9].text.strip()
            
        publicacoes.append({
            "rpi":rpi,
            "data-rpi":data_rpi,
            "despacho":despacho,
            "certificado":certificado,
            "interior":interior,
            "complemento-despacho":complemento_despacho            
        })
    resposta["publicacoes"] = publicacoes


    return resposta

def consultarPatente(resposta,cached,session,linksServicos,servico,id):
    #fazer um request post para o servidor pedindo a pagina de patentes
    linkPatente = None
    if not cached:

        formulario = {
            'NumPedido':id,
            'NumGru': '',
            'NumProtocolo': '',
            'FormaPesquisa': '',
            'ExpressaoPesquisa': '',
            'Coluna': '',
            'RegisterPerPage': '20',
            'Action': 'SearchBasico'
        }
        pagina = session.post("https://busca.inpi.gov.br" + linksServicos[servico], data=formulario,verify=False)
        time.sleep(1)
        with open(f"cache_paginas/{servico}_{id}.html","wb") as file:
            file.write(pagina.content)            

        #extrair tabela de resultados da pesquisa
        soup = BeautifulSoup(pagina.content, 'html.parser')
        body = soup.find('body')
        dom = etree.HTML(str(body))
        for i in soup.find_all('table')[0].find_all('font'):
            a = i.find('a')
            if a != None and a.text.strip() not in ["Início","Base Patentes"]:
                linkPatente = a.get('href')
                break

        if linkPatente == None:
            print("ERRO: Patente não encontrada...")
            return resposta
        
    #pegar detalhes da patente
    if not cached:
        pagina = session.post("https://busca.inpi.gov.br" + linkPatente,verify=False)
        with open(f"cache_paginas/{servico}_{id}.html","wb") as file:
            file.write(pagina.content)
        resposta = extrairDadosPatente(pagina.content,resposta)
    else:
        with open(f"cache_paginas/{servico}_{id}.html","rb") as file:
            resposta = extrairDadosPatente(file.read(),resposta)

    return resposta