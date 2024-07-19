import requests
from bs4 import BeautifulSoup


#linkServico
linksServicos = {
    "marca":"/pePI/servlet/MarcasServletController"
}


def WebCrawler(requestAPI):

    #pedido
    pedido = requestAPI.split("/")
    servico = pedido[0]
    id = pedido[1]
    if servico not in linksServicos:
        print("ERRO: A busca desse servico ainda não foi implementada...")
        return 


    #entrar como convidado
    session = requests.session()
    session.get("https://busca.inpi.gov.br/pePI/servlet/LoginController?action=login")
    resposta = {}

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
        pagina = session.post("https://busca.inpi.gov.br" + marca["linkDetalhes"])
        soup = BeautifulSoup(pagina.content, 'html.parser')
        

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
        table = soup.find_all('table')[2]
        colunas = table.find_all("td")
        with open("table.html","w") as file:
            file.write(str(colunas))
        classificação = {
            "classe-nice":colunas[0].find("a").text.strip(),
            "situacao":colunas[5].text.strip(),
            "especificacao":colunas[10].text.strip()
        }
        resposta["classificacao"] = classificação


        #extrair titulares
        table = soup.find_all('table')[7]
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
        # OBS: Essa tabela ainda não foi implementada pois faltam dados


        #extrair datas
        table = soup.find_all('table')[9]
        linha = table.find_all("tr")[4].find_all("th")
        datas = {
            "deposito":linha[0].text.strip(),
            "concessao":linha[1].text.strip(),
            "vigencia":linha[2].text.strip()
        }
        resposta["datas"] = datas


        #extrair prazos para prorrogação
        table = soup.find_all('table')[12]
        linhas = table.find_all("tr")
        prazos = {
            "Inicio":{
                "ordinario":linhas[1].find_all("td")[1].text.strip(),
                "extraordinario":linhas[1].find_all("td")[2].text.strip(),
            },
            "Fim":{
                "ordinario":linhas[2].find_all("td")[1].text.strip(),
                "extraordinario":linhas[2].find_all("td")[2].text.strip(),
            }
        }
        resposta["prazos"] = prazos


        #peticoes
        table = soup.find_all('table')[15]
        linhas = table.find("tbody").find_all("tr")
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
        resposta["prazos"] = prazos
        

        #publicacoes
        table = soup.find_all('table')[30].find('tbody').find_all('tr')
        publicacoes = []
        ok = False
        for index,i in enumerate(table):
            
            colunas = i.find_all('td')
            if len(colunas) < 4:
                continue

            if not ok:
                ok = not ok
                for ind,cada in enumerate(colunas):
                    print(f"index - {ind}:",cada.text.strip())

            publicacoes.append({
                "rpi":colunas[0].text.strip(),
                "data-rpi":colunas[1].text.strip(),
                "despacho":colunas[2].text.strip(),
                "certificado":colunas[3].text.strip(),
                "interior":colunas[4].text.strip(),
                "complemento-despacho":colunas[5].find('font').text.strip()            
            })
        resposta["prazos"] = prazos


WebCrawler("marca/926148915")

