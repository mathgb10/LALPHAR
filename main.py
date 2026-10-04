from playwright.sync_api import sync_playwright

import os

import time

from rich import print
from dotenv import load_dotenv

import json

# Carrega .env
load_dotenv()

# Configurações
URL = os.getenv('SITE')
ARQ = os.getenv("ARQUIVO")

# Validação de .env
def validacao_env():
    if not URL or not ARQ:
        if not URL and not ARQ:
            print(f'[bold red]Váriaveis de Ambiente não configuradas[/]')
        if not URL:
            print(f'[bold red]Váriavel de URL não configurada[/]')
        if not ARQ:
            print(f'[bold red]Váriavel de ARQUIVO não configurada[/]')

        raise RuntimeError(".env não configurado")

# Função que lê o arquivo com as buscas e os retorna
def leitura_arq():
    # Abre o arquivo em leitura
    with open(ARQ,'r',encoding='utf-8') as arq:
        # Lê as linhas do arquivo 
        linhas = arq.readlines()
        temp_lista = []

        # Removo o \n no final das linhas e adiciono a lista temporária
        for i in range(len(linhas)):
            temp_lista.append(linhas[i].replace('\n',''))

        # Caso a lista esteja vazia, retorno um erro
        if not temp_lista:
            print(f'[bold red]Arquivo de dicionário vazio[/]')
            raise RuntimeError("Dicionário não configurado")
        
        return temp_lista

# Abre o navegador no site definido
def abrir_site(lista):
    with sync_playwright() as play:
        # Abro o navegador e a página
        navegador = play.chromium.launch(headless=False)
        pagina = navegador.new_page()
        pagina.goto(URL)
        # Espero a página carregar
        pagina.wait_for_load_state("domcontentloaded")

        # Chamo a função que encontra a barra de pesquisa
        barra_pesquisa(pagina,lista)

        # Provisório para não fechar
        print(f"Script rodou para finalizar pressione [bold yellow]ENTER[/]...")
        input()
        navegador.close()

# Encontra a barra de pesquisa
def barra_pesquisa(pagina,lista):
    barra_pesq = pagina.locator('[class="form-control search-bar"]')

    # Se a barra for visivel, chamo a função de pesquisa
    if barra_pesq.is_visible():
        print(f"[bold green]Barra de pesquisa encontrada[/]")
        pesquisar(pagina,barra_pesq,lista)
    else:
        print(f"[bold red]Barra de pesquisa não encontrada[/]")
        print(f"[bold yellow]Talvez esteja escondida em um menu hamburger, vamos tentar encontrar...[/]")
        
        menu = pagina.locator('xpath=/html/body/nav/div/div[1]/button')
        
        if menu.is_visible():
            menu.click()
            pesquisar(pagina,barra_pesq,lista)
        else:
            print(f"[bold red]Menu não encontrada[/]")
            raise RuntimeError("Barra e menu não encontrados")

# Realiza a pesquisa e chama funções de verificação e escrita no .json
def pesquisar(pagina, barra, lista):
    btn = pagina.locator('[class="input-group-btn search-btn"]')

    if btn.is_visible():
        print("[bold green]Botão de pesquisar encontrado[/]")

        for p in lista:
            barra.fill(p)
            btn.click()
            pagina.wait_for_load_state("domcontentloaded")

            print(f"[bold green]Pesquisa {p} realizada com sucesso[/]")

            todos_links = []

            while True:
                links = conteudo(pagina)
                if links:
                    todos_links.extend(links)

                if not btn_proximo(pagina):
                    break

            if todos_links:
                print(
                    f"[bold blue]Verificando português em "
                    f"{len(todos_links)} resultados...[/]"
                )

                links_pt = check_portugues(pagina, todos_links)

                if links_pt:
                    add_json(p, links_pt)
                else:
                    print(
                        "[bold yellow]"
                        "Nenhum conteúdo em português encontrado"
                        "[/]"
                    )

            time.sleep(1)

    else:
        print("[bold red]Botão de pesquisar não encontrado[/]")
        raise RuntimeError("Botão de pesquisar não encontrado")

# Válido se existem outras páginas e o botão próximo
def btn_proximo(pagina):
    proximo = pagina.locator('li.next')
    if proximo.count() == 0:
        print(f"[bold yellow]Botão próximo não encontrado[/]")
        return False

    # Se o botão estiver desabilitado, retorno false
    if "disabled" in proximo.get_attribute('class'):
        print(f"[bold yellow]Botão próximo desabilitado[/]")
        return False

    link = proximo.locator('a')

    if link.count() == 0:
        return False
    
    link.click()
    pagina.wait_for_load_state("domcontentloaded")
    return True

# Válida o conteudo
def conteudo(pagina):
    linha_tab = pagina.locator("tbody>tr")
    
    # Se a tabela existir
    if linha_tab.count() > 0:
        print(f"[bold green]Foram encontrados nessa página: {linha_tab.count()} itens[/]")
        temp_links = []

        # Vou percorrer cada linha da tabela e pegar o link do item
        for l in range(linha_tab.count()):
            linha = linha_tab.nth(l)
            celula = linha.locator("td").nth(1)
            # :not é para evitar o item com a classe comments
            link = celula.locator("a:not(.comments)")
            # print(link.get_attribute('href'))
            # Adiciono o link a lista temporaria
            temp_links.append(link.get_attribute('href'))
            
        print(f"[bold green]Todos os links foram adicionados a lista.[/]")
        print(f"[bold blue]{temp_links}[/]")
        return temp_links
            
    else:
        print(f"[bold red]Nenhum conteúdo encontrado[/]")
        return False

# Válida e escreve no .json
def add_json(nome, dados):
    # Lê o que já existe no arquivo
    with open('content\\data.json', 'r', encoding='utf-8') as arq:
        objeto = json.load(arq)

    # Verifica se a busca já existe
    if nome in objeto:
        print(f'[bold red]Já possuímos dados de: {nome}[/]')
        novos = 0

        # Verifica cada link individualmente
        for link in dados:
            if link not in objeto[nome]:
                objeto[nome].append(link)
                novos += 1

        if novos == 0:
            print('[bold yellow]Não há novos dados para adicionarmos[/]')
        else:
            print(f'[bold green]Adicionamos {novos} dados novos ao .json[/]')

    else:
        objeto[nome] = dados
        print(f'[bold green]Adicionamos os dados ao .json[/]')

    # Salva o resultado
    with open('content\\data.json', 'w', encoding='utf-8') as arq:
        json.dump(objeto, arq, ensure_ascii=False, indent=4)

# Verifica se existe português na página
def check_portugues(pagina,links):
    links_pt = []
    # Palavras que seram procuradas
    contexto = ["pt-br","ptbr","portuguese","português","brazilian","brasil","brazil"]

    for l in links:
        pagina.goto(URL + l)
        pagina.wait_for_load_state("domcontentloaded")
        
        txt = pagina.locator("body").inner_text().lower()
        encontrado = False

        for c in contexto:
            if c in txt:
                links_pt.append(l)
                print(f"[bold green]Português encontrado: {c}[/]")
                encontrado = True
                break

        if not encontrado:
            print("[bold red]Português não encontrado[/]")

    return links_pt

# Inicia todo o projeto
def start():
    # Limpa o terminal
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear') 

    validacao_env()
    lista = leitura_arq()

    print(f"""
    {99*'='}
    As buscas serão realizadas baseadas nas seguintes informações:
    Site: [bold blue]{URL}[/]
    Arquivo: [bold blue]{ARQ}[/]
    Buscas: [bold blue]{lista}[/]
    {99*'='}
    """)

    for i in range(3,0,-1):
        print(f"[bold yellow]Abrindo o site em: {i}s[/]")
        time.sleep(1)

    abrir_site(lista)

start()