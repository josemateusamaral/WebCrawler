from bs4 import BeautifulSoup
from lxml import etree
from includes.utils import *

#funcao para extrair os dados de um patente
def extrairDadosPatente(pagina,resposta):
    #converter pagina para o formato do beautifulsoup4
    soup = BeautifulSoup(pagina, 'html.parser')
    body = soup.find('body')
    dom = etree.HTML(str(body))

    #extrair dados gerais
    # dadosGerais = {
    #     "data-deposito":findXpath("/html/body/form/div[2]/div/table[2]/tbody/tr[3]/td[2]/font",dom).text.strip(),
    #     "data-publicacao":findXpath("/html/body/form/div[2]/div/table[2]/tbody/tr[4]/td[2]/font",dom).text.strip(),
    #     "data-concecao":findXpath("/html/body/form/div[2]/div/table[2]/tbody/tr[5]/td[2]/font",dom).text.strip(),
    #     "nome-depositante":findXpath("/html/body/form/div[2]/div/table[2]/tbody/tr[6]/td[2]/font",dom).text.strip()
    # }
    # resposta["dados-gerais"] = dadosGerais

    deposito = findXpath("/html/body/form/div[2]/div/table[2]/tbody",dom)
    print(deposito)


    return resposta