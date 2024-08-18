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

    session = requests.session()
    resposta = {}

    # pedido
    pedido = requestAPI.split("/")
    servico = pedido[0]
    id = pedido[1]
    if servico not in linksServicos:
        print("ERRO: A busca desse servico ainda não foi implementada...")
        return 

    # verificar a possibilidade de usar o cache
    if f"{servico}_{id}.html" not in os.listdir("cache_paginas"):
        cached = False 

    # entrar como convidado
    if not cached:
        session.get("https://busca.inpi.gov.br/pePI/servlet/LoginController?action=login",verify=False)
        time.sleep(1)

    # consultar marca
    if servico == "marca":
        resposta = consultarMarca(resposta,cached,session,linksServicos,servico,id)
    
    # consultar patente
    elif servico == "patente":
        resposta = consultarPatente(resposta,cached,session,linksServicos,servico,id)

    return resposta


#marcas: 002489937 - 926148915
#patentes: BR1020230073581 - BR1120230071364A2
resposta = WebCrawler("patente/BR1120230071364",True)
#resposta = WebCrawler("marca/926148915",True)
with open("response.json","w") as file:
    json.dump(resposta,file)




