from bs4 import BeautifulSoup
from lxml import etree

#funcao para utilizar o XPATH com o BeautifulSoup
def findXpath(xpath,dom):
    return BeautifulSoup(etree.tostring(dom.xpath(xpath)[0], pretty_print=True).decode('utf-8'),'html.parser')