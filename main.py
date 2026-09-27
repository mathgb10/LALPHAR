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
    with open(ARQ,'r',encoding='utf-8') as arq:
        linhas = arq.readlines()
        temp_lista = []

        for i in range(len(linhas)):
            temp_lista.append(linhas[i].replace('\n',''))

        if not temp_lista:
            print(f'[bold red]Arquivo de dicionário vazio[/]')
            raise RuntimeError("Dicionário não configurado")
        
        return temp_lista

# Abre o navegador no site definido
def abrir_site(lista):
    with sync_playwright() as play:
        navegador = play.chromium.launch(headless=False)
        pagina = navegador.new_page()
        pagina.goto(URL)
        pagina.wait_for_load_state("domcontentloaded")

        barra_pesquisa(pagina,lista)

        # Provisório para não fechar
        print(f"Script rodou para finalizar pressione [bold yellow]ENTER[/]...")
        input()
        navegador.close()

# Encontra a barra de pesquisa
def barra_pesquisa(pagina,lista):
    barra_pesq = pagina.locator('[class="form-control search-bar"]')

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

# Realiza a pesquisa
def pesquisar(pagina,barra,lista):
    btn = pagina.locator('[class="input-group-btn search-btn"]')
    
    if btn.is_visible():
        print("[bold green]Botão de pesquisar encontrado[/]")
        
        for p in lista:
            barra.fill(p)
            btn.click()
            pagina.wait_for_load_state("domcontentloaded")

            print(f"[bold green]Pesquisa {p} realizada com sucesso[/]")
            conteudo(pagina)
            time.sleep(1)
    else:
        print("[bold red]Botão de pesquisar não encontrado[/]")
        raise RuntimeError("Botão de pesquisar não encontrado")

# Válida o conteudo
def conteudo(pagina):
    linha_tab = pagina.locator("tbody>tr")

    # Se a tabela existir
    if linha_tab.count() > 0:
        print(f"[bold green]Foram encontrados nessa página: {linha_tab.count()} itens[/]")
        temp_links = []

        for l in range(linha_tab.count()):
            linha = linha_tab.nth(l)
            celula = linha.locator("td").nth(1)
            link = celula.locator("a:not(.comments)")
            # print(link.get_attribute('href'))
            temp_links.append(link.get_attribute('href'))
            
        print(f"[bold green]Todos os links foram adicionados a lista.[/]")
        print(f"[bold blue]{temp_links}[/]")
        # Escreve no arquivo
        with open('content\\data.json','a',encoding='utf-8') as arq:
            json.dump(temp_links,arq,ensure_ascii=False,indent=4)
            
    else:
        print(f"[bold red]Nenhum conteúdo encontrado[/]")

# Inicia todo o projeto
def start():
    validacao_env()
    lista = leitura_arq()

    print(f"""
    {100*'='}
    As buscas serão realizadas baseadas nas seguintes informações:
    Site: [bold blue]{URL}[/]
    Arquivo: [bold blue]{ARQ}[/]
    Buscas: [bold blue]{lista}[/]
    {100*'='}
    """)

    for i in range(3,0,-1):
        print(f"[bold yellow]Abrindo o site em: {i}s[/]")
        time.sleep(1)

    abrir_site(lista)

start()