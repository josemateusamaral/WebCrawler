from bs4 import BeautifulSoup
from lxml import etree
from includes.utils import *
import time

# achar tabela na pagina de marcar usa
def findTablePatentes(nomeTabela,dom):
    for i in range(50):
        try:
            if findXpath(f'/html/body/form/div[2]/div/div[{i}]/div',dom).find('label').find('font').text.strip() == nomeTabela:
                return findXpath(f'/html/body/form/div[2]/div/div[{i}]/div/div/table/tbody',dom)
        except: pass
    return None

#funcao para extrair os dados de um patente
def extrairDadosPatente(pagina,resposta):

    #print("pagina:",pagina)
    #converter pagina para o formato do beautifulsoup4
    soup = BeautifulSoup(pagina, 'html.parser')
    body = soup.find('body')
    dom = etree.HTML(str(body))



    #extrair dados gerais
    table = findXpath("/html/body/form/div[2]/div/table[2]",dom)
    colunas = table.find_all('tr')
    numeroPedido = colunas[1].find_all('td')[1].get_text(strip=True)
    dataDeposito = colunas[2].find_all('td')[1].get_text(strip=True)
    dataPublicacao = colunas[3].find_all('td')[1].get_text(strip=True)
    dataConcessao = colunas[4].find_all('td')[1].get_text(strip=True)
    nomeDepositante = colunas[5].find_all('td')[1].get_text(strip=True)
    dadosGerais = {
        "numeroPedido":numeroPedido,
        "dataDeposito":dataDeposito,
        "dataPublicacao":dataPublicacao,
        "dataConcessao":dataConcessao,
        "nomeDepositante":nomeDepositante
    }
    resposta["dadosGerais"] = dadosGerais



    #extrair peticoes
    peticoes = {}
    table = findTablePatentes("Petições",dom)
    
    #servicoes
    '''
    servicos = {}
    descricaoServicos = findXpath("/html/body/form/div[2]/div/div[6]/div/div/table/tbody/tr[2]/td[1]",dom).find("font").get_text(strip=True)
    altPagamento = str(findXpath("/html/body/form/div[2]/div/div[6]/div/div/table/tbody/tr[2]/td[2]/font/font/a/img",dom))
    pagamentoServicos = ""
    dentro = False
    for i in altPagamento:
        if i == '"' and not dentro: dentro = True
        elif i == '"' and dentro: break
        if dentro and i != '"': pagamentoServicos += i
    protocolo = findXpath("/html/body/form/div[2]/div/div[6]/div/div/table/tbody/tr[2]/td[3]/font",dom).get_text(strip=True)
    data = findXpath("/html/body/form/div[2]/div/div[6]/div/div/table/tbody/tr[2]/td[4]/font",dom).get_text(strip=True)
    imagem1 = findXpath("/html/body/form/div[2]/div/div[6]/div/div/table/tbody/tr[2]/td[5]/font",dom).get_text(strip=True)
    imagem2 = findXpath("/html/body/form/div[2]/div/div[6]/div/div/table/tbody/tr[2]/td[6]/font",dom).get_text(strip=True)
    imagem3 = findXpath("/html/body/form/div[2]/div/div[6]/div/div/table/tbody/tr[2]/td[7]/font",dom).get_text(strip=True)
    cliente = findXpath("/html/body/form/div[2]/div/div[6]/div/div/table/tbody/tr[2]/td[8]/font",dom).get_text(strip=True)
    servicos["descricao-servico"] = descricaoServicos
    servicos["pagamento-servico"] = pagamentoServicos
    servicos["protocolo"] = protocolo
    servicos["data"] = data
    servicos["imagem1"] = imagem1
    servicos["imagem2"] = imagem2
    servicos["imagem3"] = imagem3
    servicos["cliente"] = cliente
    peticoes["servicos"] = servicos
    
    resposta["peticoes"] = peticoes

    '''

    #publicacoes
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

    #print(data)

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