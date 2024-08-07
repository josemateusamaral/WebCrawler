import requests
from bs4 import BeautifulSoup
import json
import os
from lxml import etree

#linkServico
linksServicos = {
    "marca":"/pePI/servlet/MarcasServletController"
}


# achar tabela na pagina de marcar usa
def findTableMarcas(nomeTabela,dom):
    for i in range(50):
        try:
            if findXpath(f'/html/body/form/div[2]/div/div[{i}]/div',dom).find('label').find('font').text.strip() == nomeTabela:
                return findXpath(f'/html/body/form/div[2]/div/div[{i}]/div/div/table/tbody',dom)
        except: pass
    return None


#funcao para utilizar o XPATH com o BeautifulSoup
def findXpath(xpath,dom):
    return BeautifulSoup(etree.tostring(dom.xpath(xpath)[0], pretty_print=True).decode('utf-8'),'html.parser')


#função para extrair os dados de marca de um arquivo HTML
def extrairDadosMarca(pagina,resposta):

    #converter pagina para o formato do beautifulsoup4
    soup = BeautifulSoup(pagina, 'html.parser')
    body = soup.find('body')
    dom = etree.HTML(str(body))



    #extrair dados gerais
    table = soup.find_all('table')[1]
    if table:
        data = {}
        rows = table.find_all('tr')
        for row in rows:
            try:
                cols = row.find_all('td')
                if len(cols) == 2:
                    key = cols[0].find('font', class_='normal').text.strip()
                    value = cols[1].find('font', class_='normal').text.strip()
                    data[key] = value
            except:
                pass
        resposta["dados-gerais"] = data
    else:
        print('Tabela de dados gerais não encontrada...')



    #extrair classificação
    classeNice = findXpath('/html/body/form/div[2]/div/div[3]/div/div/table/tbody/tr/td[1]',dom)
    situacao = findXpath('/html/body/form/div[2]/div/div[3]/div/div/table/tbody/tr/td[2]',dom)
    especificacao = findXpath('/html/body/form/div[2]/div/div[3]/div/div/table/tbody/tr/td[3]',dom)
    classificação = {
        "classe-nice":classeNice.find('font').get_text(strip=True),
        "situacao":situacao.get_text(strip=True),
        "especificacao":especificacao.get_text(strip=True)
    }
    resposta["classificacao"] = classificação
    


    #extrair titulares
    table = findXpath('/html/body/form/div[2]/div/div[4]/div/div/table/tbody',dom)
    linhas = table.find_all("tr")
    titulares = []
    for linha in linhas:
        try:
            coluna = linha.find_all("td")
            titulares.append({
                "indice":coluna[0].text.strip(),
                "nome":coluna[1].text.strip()
            })
        except: pass
    resposta["titulares"] = titulares

    

    #extrair representante legal
    table = findTableMarcas("Representante Legal",dom)
    linha = table.find("tr")
    if linha != None:
        posicao = linha.find_all('td')[0].text.strip()
        nome = linha.find_all('td')[1].text.strip()
        representanteLegal = {
            "posicao":posicao,
            "nome":nome
        }
        resposta["representante-legal"] = representanteLegal
    else:
        resposta["representante-legal"] = {}



    #extrair datas
    table = findXpath('/html/body/form/div[2]/div/div[6]/div/div/table/tbody',dom)
    linha = table.find("tr").find_all('th')
    datas = {
        "deposito":linha[0].text.strip(),
        "concessao":linha[1].text.strip(),
        "vigencia":linha[2].text.strip()
    }
    resposta["datas"] = datas

    

    #extrair prazos para prorrogação
    table = findTableMarcas("Prazos para prorrogação de registro de marca",dom)
    if table != None:
        linhas = table.find_all("tr")
        prazos = {
            "Inicio":{
                "ordinario":linhas[0].find_all("td")[1].text.strip(),
                "extraordinario":linhas[0].find_all("td")[2].text.strip(),
            },
            "Fim":{
                "ordinario":linhas[1].find_all("td")[1].text.strip(),
                "extraordinario":linhas[1].find_all("td")[2].text.strip(),
            }
        }
        resposta["prazos"] = prazos



    #peticoes
    table = findTableMarcas("Petições",dom)
    linhas = table.find_all("tr")
    peticoes = []
    for index,i in enumerate(linhas):
        
        colunas = i.find_all('td')
        if len(colunas) < 4:
            continue
            
        peticoes.append({
            "protocolo":colunas[5].text.strip(),
            "data":colunas[6].text.strip(),
            "img":colunas[7].text.strip(),
            "servico":colunas[9].find('a').text.strip(),
            "cliente":colunas[14].text.strip(),
            "delivery":colunas[15].text.strip(),  
            "data2":colunas[16].text.strip()            
        })
    resposta["peticoes"] = peticoes



    #extrair as publicacoes
    table = findTableMarcas("Publicações",dom)
    linhas = table.find_all("tr")
    publicacoes = []
    ok = False
    for index,i in enumerate(linhas):
        
        colunas = i.find_all('td')
        if len(colunas) < 4:
            continue    
        
        if len(colunas) == 10:
            rpi = colunas[0].text.strip()
            data_rpi = colunas[1].text.strip()
            despacho = colunas[2].find('font').text.strip()
            certificado = colunas[7].get_text(strip=True)
            interior = colunas[8].find('font').text.strip()
            complemento_despacho = colunas[9].text.strip()
        else:
            rpi = colunas[0].text.strip()
            data_rpi = colunas[1].text.strip()
            despacho = colunas[2].find('font').text.strip()
            certificado = colunas[3].get_text(strip=True)
            interior = colunas[4].find('font').text.strip()
            complemento_despacho = colunas[5].text.strip()

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


def WebCrawler(requestAPI,cached=False):

    resposta = {}

    #pedido
    pedido = requestAPI.split("/")
    servico = pedido[0]
    id = pedido[1]
    if servico not in linksServicos:
        print("ERRO: A busca desse servico ainda não foi implementada...")
        return 

    if f"{servico}_{id}.html" not in os.listdir("cache_paginas"):
        cached = False 

    #entrar como convidado
    if not cached:
        session = requests.session()
        session.get("https://busca.inpi.gov.br/pePI/servlet/LoginController?action=login")

    if servico == "marca":

        #fazer um request post para o servidor pedindo a pagina de marcas
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': "https://busca.inpi.gov.br" + linksServicos[servico]
        }
        formulario = {
            'NumPedido': id,
            'NumGRU': '', 
            'NumProtocolo': '', 
            'NumInscricaoInternacional': '', 
            'Action': 'searchMarca',
            'tipoPesquisa': 'BY_NUM_PROC'
        }
        if not cached:
            pagina = session.post("https://busca.inpi.gov.br" + linksServicos[servico], data=formulario, headers=headers)

            #extrair tabela de resultados da pesquisa
            soup = BeautifulSoup(pagina.content, 'html.parser')
            tabela_resultados = soup.find('table', width='780')
            marca = {}
            if tabela_resultados:
                linhas = tabela_resultados.find_all('tr')[1:]
                for linha in linhas:
                    celulas = linha.find_all('td')
                    if len(celulas) >= 8:
                        marca["numero"] = celulas[0].text.strip()
                        marca["linkDetalhes"] = celulas[0].find('a')['href'] if celulas[0].find('a') else None
                        marca["prioridade"] = celulas[1].text.strip()
                        marca["marca"] = celulas[3].text.strip()
                        marca["situacao"] = celulas[5].text.strip()
                        marca["titular"] = celulas[6].text.strip()
                        marca["classe"] = celulas[7].text.strip()
            if marca == {}:
                print("ERRO: Marca não encontrada...")
                return


        #pegar detalhes da marca
        if not cached:
            pagina = session.post("https://busca.inpi.gov.br" + marca["linkDetalhes"])
            with open("pagina.html","wb") as file:
                print("gravando pagina de dados...")
                file.write(pagina.content)
            resposta = extrairDadosMarca(pagina.content,resposta)
        else:
            with open(f"cache_paginas/{servico}_{id}.html","rb") as file:
                resposta = extrairDadosMarca(file.read(),resposta)

    return resposta


#marcas testadas: 002489937 - 926148915
resposta = WebCrawler("marca/002489937")
with open("response.json","w") as file:
    json.dump(resposta,file)

