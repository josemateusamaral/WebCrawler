from bs4 import BeautifulSoup
from lxml import etree

#funcao para utilizar o XPATH com o BeautifulSoup
def findXpath(xpath,dom):
    elemento = dom.xpath(xpath)
    if len(elemento) == 0:
        return None
    return etreeToSoup(elemento[0])

# funcao para converter um elementro do etree do lxml em um elemento do BeautifulSoup4
def etreeToSoup(elemento):
    return BeautifulSoup(etree.tostring(elemento, pretty_print=True).decode('utf-8'),'html.parser')