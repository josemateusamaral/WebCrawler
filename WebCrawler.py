import requests
from bs4 import BeautifulSoup
import json
import os
from lxml import etree
import time

#includes dos servicos
from includes.marca import *
from includes.patente import *
from includes.utils import *

#linkServico
linksServicos = {
    "marca":"/pePI/servlet/MarcasServletController",
    "patente":"/pePI/servlet/PatenteServletController"
}

#função principal que recebe a requisicao da API e retorna um dicionario que pode ser convertido em JSON
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
        proxy = {
            "http": 'http://207.188.6.20:3128'
        }
        session.get("https://busca.inpi.gov.br/pePI/servlet/LoginController?action=login",verify=False)
        time.sleep(1)

    if servico == "marca":

        #fazer um request post para o servidor pedindo a pagina de marcas
        formulario = {
            'NumPedido': id,
            'NumGRU': '', 
            'NumProtocolo': '', 
            'NumInscricaoInternacional': '', 
            'Action': 'searchMarca',
            'tipoPesquisa': 'BY_NUM_PROC'
        }
        marca = {}
        if not cached:
            pagina = session.post("https://busca.inpi.gov.br" + linksServicos[servico], data=formulario,verify=False)
            time.sleep(1)

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
            with open(f"cache_paginas/{servico}_{id}.html","wb") as file:
                print("gravando pagina de dados...")
                file.write(pagina.content)
            resposta = extrairDadosMarca(pagina.content,resposta)
        else:
            with open(f"cache_paginas/{servico}_{id}.html","rb") as file:
                resposta = extrairDadosMarca(file.read(),resposta)

    
    elif servico == "patente":
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
        print("link patente:",linkPatente)
        if not cached:
            pagina = session.post("https://busca.inpi.gov.br" + linkPatente,verify=False)
            with open(f"cache_paginas/{servico}_{id}.html","wb") as file:
                file.write(pagina.content)
            resposta = extrairDadosPatente(pagina.content,resposta)
        else:
            with open(f"cache_paginas/{servico}_{id}.html","rb") as file:
                resposta = extrairDadosPatente(file.read(),resposta)

    return resposta


#marcas: 002489937 - 926148915
#patentes: BR1020230073581
resposta = WebCrawler("patente/BR1020230073581",True)
with open("response.json","w") as file:
    json.dump(resposta,file)




