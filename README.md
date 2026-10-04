# LALPHAR

## Visão Geral

É um projeto que consiste em pesquisar conteúdos predefinidos em um **dicionário**, até o momento o projeto foi pensado exclusivamente para ser usado no **Nyaa.si**, a ideia é:

1. Válida se as váriaveis de ambiente estão definidas
2. Válida se o arquivo de dicionário tem conteúdo
3. Acessa o site
4. Busca oque foi definido no dicionário no site
5. Tenta encontrar o conteúdo com legenda PT-BR
6. Se encontrar ele salva a URL em um .json

## Requisitos

- Python 3
- Playwright
- python-dotenv
- Rich

## Como usar

### 1. Clone o repositório
```
git clone https://github.com/mathgb10/lalphar .
```
### 2. Instale as dependências
```
pip install -r requirements.txt
```
### 3. Defina um arquivo de dicionário
### 4. Configure o .env
Exemplo:
```
SITE=https://nyaa.si
ARQUIVO=dicionario.txt
```

## Observação

Fiz este projeto com o intuito de melhorar minha afinidade com **Python** e aprender mais sobre bibliotecas que permitem automações.
O projeto ainda está em desenvolvimento, e novas funcionalidades e ajustes serão realizados.

---
```markdown
> MVP finalizado