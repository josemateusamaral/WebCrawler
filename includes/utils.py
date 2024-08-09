from bs4 import BeautifulSoup
from lxml import etree

#funcao para utilizar o XPATH com o BeautifulSoup
def findXpath(xpath,dom):
    elemento = dom.xpath(xpath)
    if not len(elemento):
        return None
    return BeautifulSoup(etree.tostring(elemento[0], pretty_print=True).decode('utf-8'),'html.parser')