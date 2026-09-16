# **Documento de Requisitos do Sistema (SRS) — PhotoOrganizer**

## **1\. Visão Geral do Produto**

O **PhotoOrganizer** é uma aplicação utilitária desenvolvida em **Go**, projetada para organizar automaticamente fotos e imagens desordenadas. A ferramenta utiliza um modelo local de visão-linguagem (**SigLIP** via sidecar Python) para classificar o conteúdo visual das imagens, extrai metadados técnicos (EXIF) para estabelecer a cronologia correta e persiste todo o estado e indexação em um banco de dados **SQLite** embutido. A interação do usuário ocorre por meio de uma **Web UI local**, distribuída dentro do próprio executável, permitindo configurações, acompanhamento em tempo real e retomada de processos interrompidos de forma amigável e intuitiva.

## **2\. Arquitetura do Sistema**

O sistema é arquitetado em três camadas locais interconectadas:

> 1. **Frontend (Web UI):** Aplicação baseada em HTML/JS/CSS, embutida no binário Go. Roda diretamente no navegador padrão do usuário.  
> 2. **Backend (Go CLI/Server):** Orquestrador principal. Lida com a varredura do disco de forma concorrente, gerencia o banco de dados SQLite, extrai EXIF, executa a movimentação física dos arquivos e expõe uma API HTTP/SSE para comunicação em tempo real com o Frontend.  
> 3. **Sidecar de Inferência (Python):** Processo filho gerenciado pelo Go que carrega o modelo SigLIP (via ONNX/DirectML ou PyTorch nativo) na memória (VRAM/RAM) e expõe um endpoint local para classificação ultrarrápida (zero-shot) de imagens.

## **3\. Requisitos Funcionais (RF)**

### **RF01: Interface e Inicialização (Web UI)**

> * **RF01.1:** Ao ser executada via terminal ou duplo clique, a aplicação deve iniciar o servidor web e abrir automaticamente a interface no navegador padrão do sistema operacional.  
> * **RF01.2:** A interface web deve fornecer um formulário permitindo ao usuário visualizar e editar:  
  * **Diretório Alvo (Origem):** Pré-preenchido automaticamente com o caminho absoluto do diretório de onde o executável foi iniciado (os.Getwd()).  
  * **Diretório de Destino:** Onde a nova hierarquia será criada.  
  * **Modo de Operação:** Opção tipo *Radio Button* ou *Dropdown* entre **Copiar** (comportamento padrão e seguro) ou **Mover**.  
> * **RF01.3:** A interface deve exibir uma tabela ou lista referencial contendo as categorias visuais/tags que a IA é capaz de identificar (conforme taxonomia definida no RF04).  
> * **RF01.4:** A interface deve exibir uma **Tabela de Arquivos Processados**, reativa e alimentada pelo banco de dados, mostrando: Nome do arquivo original, Data extraída, Status (Varrido, Classificado, Movido) e Tags atribuídas.  
> * **RF01.5:** Deve haver controles claros de execução: botão **Iniciar**, **Pausar** e alternância para **Dry-Run** (modo simulação).  
> * **RF01.6:** O progresso geral da operação (arquivos varridos, classificados, movidos vs. total) deve ser reportado e atualizado na interface em tempo real sem necessidade de recarregar a página.

### **RF02: Descoberta e Varredura de Arquivos**

> * **RF02.1:** O sistema deve percorrer recursivamente todos os subdiretórios dentro do diretório alvo definido.  
> * **RF02.2:** O sistema deve filtrar e processar apenas arquivos de imagem com as seguintes extensões (case-insensitive): .jpg, .jpeg, .png, .heic, .webp, .dng.  
> * **RF02.3:** Imediatamente após a descoberta, o sistema deve calcular o hash criptográfico (SHA-256) do conteúdo do arquivo para garantir a identificação única e permitir a deduplicação determinística.

### **RF03: Extração de Metadados EXIF e Data**

> * **RF03.1:** O sistema deve ler o cabeçalho EXIF dos arquivos suportados e extrair prioritariamente: DateTimeOriginal, OffsetTime (fuso horário, se disponível), Make (Fabricante), Model (Modelo da câmera), GPSLatitude e GPSLongitude.  
> * **RF03.2:** Se a tag DateTimeOriginal não estiver presente ou for inválida, o sistema deve aplicar os seguintes *fallbacks* na ordem estrita:  
  1. **Regex no Nome do Arquivo:** Buscar padrões de data textuais comuns (ex: IMG\_20240512\_143000.jpg, WhatsApp Image 2024-05-12.jpeg, PXL\_20240512...).  
  2. **Data de Modificação (ModTime):** Utilizar a data de modificação (mtime) registrada no sistema de arquivos do sistema operacional.

### **RF04: Classificação Visual Zero-Shot (SigLIP)**

> * **RF04.1:** A classificação visual de cada arquivo único (por hash) deve ser executada pelo modelo SigLIP chamando o endpoint do Sidecar.  
> * **RF04.2:** Para garantir extrema performance, os *embeddings* de texto (prompts) devem ser computados pelo Sidecar apenas uma única vez durante a inicialização, e mantidos em memória.  
> * **RF04.3:** O classificador deve avaliar a imagem comparando-a estritamente com a seguinte taxonomia de categorias:

| Grupo | Chave Interna | Prompt Textual SigLIP | Destino / Comportamento |
| :---- | :---- | :---- | :---- |
| **Utilitário** | receipt\_invoice | "a photo of a paper receipt, bill, or tax invoice" | Documentos/Comprovantes/ |
| **Utilitário** | document\_text | "a photograph of a printed document, contract, or form" | Documentos/Texto/ |
| **Utilitário** | id\_card | "a photo of an identity card, driver license, or passport" | Documentos/Identidade/ |
| **Utilitário** | screenshot | "a screenshot of a mobile phone screen or computer desktop" | Screenshots/ |
| **Utilitário** | handwritten\_notes | "a photo of a notebook page with handwriting or a whiteboard" | Documentos/Anotacoes/ |
| **Eventos** | birthday\_party | "a photo of a birthday party with cake or party decorations" | Agrupador temático/evento |
| **Eventos** | wedding\_ceremony | "a photo of a wedding ceremony, bride, or wedding reception" | Agrupador temático/evento |
| **Eventos** | concert\_show | "a photo of a music concert, live stage performance, or festival" | Agrupador temático/evento |
| **Eventos** | sports\_event | "a photo of people playing sports or an athletic competition" | Agrupador temático/evento |
| **Eventos** | barbecue\_party | "a photo of a barbecue gathering, churrasco, or outdoor grill party" | Agrupador temático/evento |
| **Ambientes** | beach\_ocean | "a photo of a beach, ocean shore, and sea" | Agrupador temático/evento |
| **Ambientes** | hiking\_nature | "a photo of a hiking trail, mountains, or green forest" | Agrupador temático/evento |
| **Ambientes** | cityscape\_street | "a photo of city streets, urban architecture, and buildings" | Agrupador temático/evento |
| **Ambientes** | sunset\_sunrise | "a scenic photograph of a sunset or sunrise in the sky" | Agrupador temático/evento |
| **Ambientes** | pool\_resort | "a photo of a swimming pool or vacation resort" | Agrupador temático/evento |
| **Ambientes** | home\_indoor | "a photo taken indoors inside a house, bedroom, or living room" | Agrupador temático/evento |
| **Pessoas** | selfie | "a close-up selfie photograph of a person" | Tag de conteúdo |
| **Pessoas** | group\_portrait | "a group photo of friends or family posing together" | Tag de conteúdo |
| **Pessoas** | baby\_child | "a photograph of a baby, toddler, or young child" | Tag de conteúdo |
| **Pessoas** | portrait\_person | "a portrait photograph of a single person" | Tag de conteúdo |
| **Pets** | cat | "a close-up photo of a domestic cat" | Tag temática |
| **Pets** | dog | "a photo of a domestic dog or puppy" | Tag temática |
| **Pets** | birds\_wildlife | "a photo of birds, farm animals, or wildlife" | Tag temática |
| **Gastronomia** | food\_meal | "a close-up food photo of a cooked meal on a plate" | Tag temática |
| **Gastronomia** | drinks\_coffee | "a photo of a cup of coffee, cocktails, or beverages on a table" | Tag temática |
| **Hobbies/Misc** | vehicles | "a photograph of a car, motorcycle, or vehicle" | Tag temática |
| **Hobbies/Misc** | plants\_garden | "a close-up photo of house plants, flowers, or a garden" | Tag temática |
| **Hobbies/Misc** | crafts\_art | "a photo of handmade pottery, ceramics, crafts, or art" | Tag temática |

> * **RF04.4:** Limiares de Decisão (Sigmoid Score de 0 a 1):  
  * **Prioridade 1 (Isolamento de Utilitários):** Se o score de qualquer tag do grupo **Utilitário** for \>= 0.60, a foto recebe uma flag forte e pula a lógica de agrupamento padrão, sendo destinada imediatamente às pastas de Documentos/Screenshots.  
  * **Prioridade 2 (Marcação Geral):** Para as demais categorias dos grupos Eventos, Ambientes, Pessoas, Pets, Gastronomia e Hobbies, qualquer tag com score \>= 0.35 deve ser atribuída à imagem no banco de dados.

### **RF05: Persistência e Indexação (SQLite)**

> * **RF05.1:** A aplicação deve criar e manter um arquivo SQLite local (ex: photo\_organizer\_index.db) preferencialmente na pasta onde o executável roda ou na raiz do destino.  
> * **RF05.2:** O esquema do banco deve ser capaz de armazenar a entidade do Arquivo (caminho atual, hash, tamanho, status do processamento), metadados EXIF associados e os scores de todas as tags visuais calculadas pelo SigLIP.  
> * **RF05.3:** O sistema deve garantir **Idempotência e Retomada (Resume):** Se o usuário pausar, fechar a janela, ou ocorrer uma falha de energia, na próxima execução a aplicação verifica os hashes no banco. Arquivos com o status "Classificado" não devem ser reenviados ao SigLIP e não devem ter o EXIF reprocessado.

### **RF06: Decisão de Destino e Agrupamento Lógico**

> * **RF06.1:** A estrutura de diretórios base no destino será estritamente cronológica, agrupada por mês e ano no formato MM-AAAA (ex: 05-2024/).  
> * **RF06.2 (Desvio de Utilitários):** Imagens flagradas pelo RF04.4 (Prioridade 1\) devem ser roteadas para fora do fluxo principal. Exemplo: Documentos/Comprovantes/{MM-AAAA}/ ou Screenshots/{MM-AAAA}/.  
> * **RF06.3 (Clustering Temático):** O sistema deve analisar as imagens de um mesmo MM-AAAA. Se detectar um adensamento de fotos próximas no tempo (ex: na mesma semana) contendo tags de Eventos ou Ambientes semelhantes (ex: várias fotos com a tag beach\_ocean ou birthday\_party), essas fotos devem ser alocadas em um subdiretório temático: MM-AAAA/{Tema}/.  
> * **RF06.4:** Fotos afetivas/gerais que não formam um cluster temático expressivo devem ser movidas para o diretório de fallback MM-AAAA/Geral/ ou ficar diretamente na raiz MM-AAAA/.

### **RF07: Execução de Operações de Disco**

> * **RF07.1:** O sistema deve suportar um modo **Dry-Run (Simulação)**, que executa toda a varredura, extração de EXIF, classificação no SigLIP e planejamento de agrupamento, populando a tabela da UI com a coluna "Caminho de Destino Planejado", mas *sem gravar ou modificar arquivos físicos*.  
> * **RF07.2 (Resolução de Conflitos):** Ao realizar a cópia ou movimentação, se o arquivo destino já existir com o mesmo nome:  
  * O sistema deve calcular o hash do arquivo no destino.  
  * Se os hashes (Origem e Destino) forem **idênticos**, registrar no banco como duplicata, ignorar a operação de movimentação para economizar espaço e marcar como "Ignorado (Duplicado)".  
  * Se os hashes forem **diferentes**, o sistema deve renomear a foto da origem no destino adicionando um sufixo numérico incremental (ex: IMG\_1234\_1.jpg, IMG\_1234\_2.jpg).

## **4\. Requisitos Não Funcionais (RNF)**

> * **RNF01 (Servidor Embutido e Porta Dinâmica):** O backend Go deve iniciar um servidor HTTP interno. Ao inicializar, deve tentar se acoplar (bind) na porta padrão (ex: 8080). Se a porta estiver em uso pelo sistema operacional, deve iterar e amarrar na próxima porta TCP livre, abrindo o navegador com a URL correta (http://localhost:\<porta\_livre\>).  
> * **RNF02 (Distribuição Zero-Dependency):** A aplicação deve ser compilada de forma que todos os ativos do frontend (arquivos HTML, CSS, JavaScript, ícones) sejam embutidos diretamente no binário final utilizando a diretiva padrão go:embed.  
> * **RNF03 (Comunicação Assíncrona UI-Backend):** Toda comunicação de status, progresso e logs do backend Go para o frontend Web deve ser realizada via **Server-Sent Events (SSE)** ou **WebSockets**. Requisições HTTP long-polling normais não devem ser utilizadas para evitar *timeouts* e melhorar a reatividade da UI.  
> * **RNF04 (Concorrência e Performance):** O backend Go deve empregar *goroutines* e *channels* (Worker Pools) isolando os gargalos: a varredura de I/O em disco deve rodar em paralelo ao processamento da fila de chamadas HTTP feitas ao sidecar do SigLIP.  
> * **RNF05 (Gerenciamento do Ciclo de Vida do Sidecar):** O processo principal em Go atua como supervisor do sidecar Python. O Go deve:  
  1. Executar o script do SigLIP (via os/exec) no boot.  
  2. Efetuar *Healthchecks* no endpoint do sidecar para só liberar a UI quando o modelo estiver carregado na VRAM.  
  3. Enviar um sinal de encerramento seguro (SIGTERM/Kill) para desligar o processo Python automaticamente quando o usuário fechar o servidor Go no terminal ou via UI.  
  4. Garantir que o Python sidecar suporte, por prioridade, DirectML (para AMD RX 6600 / Windows), ROCm (Linux) ou CPU fallback nativo.