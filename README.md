## Ferramentas de coleta e processamento de dados para o Twitter

As quatro ferramentas estão disponíveis junto à jupyter notebooks que servirão de guias de uso.

Caso não seja familiar com notebooks os links abaixo podem ser úteis:

- https://jupyter.org/
- https://jupyter-notebook-beginner-guide.readthedocs.io/en/latest/what_is_jupyter.html
- https://medium.com/horadecodar/como-instalar-o-jupyter-notebook-windows-e-linux-20701fc583c

### Timeline Bot

Bot feito através do Selenium que coleta conteúdo de tweets da timeline da conta autenticada. Múltiplos bots podem ser executados ao mesmo tempo, mas é preciso se ter cuidado com o uso de memória. Os campos escolhidos para extração são explicados com mais detalhes no guia.

### Crawler via Twitter API

Simula um usuário e coleta dados da timeline de forma similar à ferramenta anterior, a diferença é no acesso pela API do Twitter em vez de web scraping.

### Web Scraper Search API

Coleta tweets nos últimos 7 dias de acordo com os termos de busca escolhidos, que podem ser inclusive hashtags.


### Pré-processamento

Possui algumas funções de pré-processamento como stemização, lematização e outros filtros de texto. Ainda em andamento, mas funcional.
