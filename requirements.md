# **Documento de Requisitos do Sistema (SRS) — Versão Final Revisada**

## **1\. Visão Geral do Produto**

O **PhotoOrganizer** é uma aplicação utilitária em **Go**, projetada para organizar automaticamente fotos desordenadas. A ferramenta utiliza um modelo local de visão-linguagem (**SigLIP** via sidecar Python) para classificar o conteúdo das imagens, extrai metadados (EXIF) para cronologia e persiste todo o estado em um banco de dados **SQLite**. A interação ocorre por meio de uma **Web UI local** embutida, operando em duas fases: a aplicação primeiro indexa e classifica os arquivos, depois apresenta um painel interativo para o usuário aprovar a estrutura de pastas e as categorias dinâmicas antes de mover os arquivos no disco.

## **2\. Arquitetura do Sistema**

O sistema é composto por três camadas:

> 1. **Frontend (Web UI):** Arquivos HTML/JS/CSS embutidos no executável via go:embed, rodando no navegador do usuário.  
> 2. **Backend (Go CLI/Server):** Orquestrador principal. Gerencia varredura, persistência SQLite, extração EXIF, regras de planejamento dinâmico de pastas, e expõe a API HTTP/SSE.  
> 3. **Sidecar de Inferência (Python):** Processo isolado que carrega o modelo SigLIP e expõe um endpoint local para classificação rápida de imagens.

## **3\. Requisitos Funcionais (RF)**

### **RF01: Interface e Fluxo de Execução (Web UI)**

> * **RF01.1:** Ao ser iniciada, a aplicação deve abrir o navegador padrão exibindo a tela inicial.  
> * **RF01.2:** A tela inicial deve permitir a definição de:  
  * Diretório de Origem (pré-preenchido com o local de execução).  
  * Diretório de Destino.  
  * Modo de operação: **Copiar** ou **Mover**.  
  * Configuração opcional: "Agrupar documentos/utilitários por Mês/Ano" (Toggle On/Off).  
> * **RF01.3 (Fluxo Fase 1):** Ao clicar em "Iniciar Indexação", o sistema processará a varredura e inferência visual sem alterar os arquivos. O progresso será mostrado em tempo real na interface.  
> * **RF01.4 (Fluxo Fase 2 \- Aprovação):** Concluída a indexação, o frontend exibirá o **Painel de Decisão**. O sistema listará todas as tags encontradas, agregadas por volume de arquivos.  
> * **RF01.5:** No Painel de Decisão, o usuário poderá marcar/desmarcar quais tags genéricas (ex: cat, food\_meal, selfie) devem gerar subpastas exclusivas no diretório de destino. Tags com volume alto de arquivos (limiar a ser definido, ex: \> 10\) devem vir marcadas por padrão.  
> * **RF01.6:** Um botão "Confirmar e Organizar" aplicará as movimentações físicas baseadas nas regras escolhidas.

### **RF02: Descoberta e Varredura de Arquivos**

> * **RF02.1:** O sistema percorrerá recursivamente o diretório de origem.  
> * **RF02.2:** Extensões suportadas: .jpg, .jpeg, .png, .heic, .webp, .dng.  
> * **RF02.3:** Hash criptográfico (SHA-256) será calculado para cada arquivo para garantir deduplicação determinística.

### **RF03: Extração de Metadados EXIF**

> * **RF03.1:** Tags a extrair: DateTimeOriginal, OffsetTime, Make, Model, GPSLatitude, GPSLongitude.  
> * **RF03.2:** Fallbacks para arquivos sem DateTimeOriginal, na ordem:  
  1. Regex de data no nome do arquivo (ex: IMG\_20260115\_...).  
  2. Data de modificação no sistema de arquivos (ModTime).

### **RF04: Classificação Visual Zero-Shot (SigLIP)**

> * **RF04.1:** A classificação via modelo SigLIP usará embeddings de texto pré-computados na inicialização do sidecar.  
> * **RF04.2:** Taxonomia de categorias e comportamentos associados ao planejamento lógico:

| Chave Interna | Prompt Textual SigLIP | Classe | Comportamento Base |
| :---- | :---- | :---- | :---- |
| receipt\_invoice | "a photo of a paper receipt, bill, or tax invoice" | Utilitário | Pasta raiz /Comprovantes |
| document\_text | "a photograph of a printed document, contract, or form" | Utilitário | Pasta raiz /Texto |
| id\_card | "a photo of an identity card, driver license, or passport" | Utilitário | Pasta raiz /Identidade |
| screenshot | "a screenshot of a mobile phone screen or computer desktop" | Utilitário | Pasta raiz /Screenshots |
| handwritten\_notes | "a photo of a notebook page with handwriting or a whiteboard" | Utilitário | Pasta raiz /Anotacoes |
| birthday\_party | "a photo of a birthday party with cake or party decorations" | Evento | Subpasta MM-AAAA/Aniversario/ |
| wedding\_ceremony | "a photo of a wedding ceremony, bride, or wedding reception" | Evento | Subpasta MM-AAAA/Casamento/ |
| concert\_show | "a photo of a music concert, live stage performance, or festival" | Evento | Subpasta MM-AAAA/Show/ |
| sports\_event | "a photo of people playing sports or an athletic competition" | Evento | Subpasta MM-AAAA/Esportes/ |
| barbecue\_party | "a photo of a barbecue gathering, churrasco, or outdoor grill party" | Evento | Subpasta MM-AAAA/Churrasco/ |
| beach\_ocean | "a photo of a beach, ocean shore, and sea" | Ambiente | Subpasta MM-AAAA/Praia/ |
| hiking\_nature | "a photo of a hiking trail, mountains, or green forest" | Ambiente | Subpasta MM-AAAA/Natureza/ |
| cityscape\_street | "a photo of city streets, urban architecture, and buildings" | Ambiente | Subpasta MM-AAAA/Cidade/ |
| sunset\_sunrise | "a scenic photograph of a sunset or sunrise in the sky" | Ambiente | Subpasta MM-AAAA/PorDoSol/ |
| pool\_resort | "a photo of a swimming pool or vacation resort" | Ambiente | Subpasta MM-AAAA/Piscina/ |
| home\_indoor | "a photo taken indoors inside a house, bedroom, or living room" | Ambiente | Subpasta MM-AAAA/Casa/ |
| selfie | "a close-up selfie photograph of a person" | Genérico | Seleção dinâmica pelo usuário |
| group\_portrait | "a group photo of friends or family posing together" | Genérico | Seleção dinâmica pelo usuário |
| baby\_child | "a photograph of a baby, toddler, or young child" | Genérico | Seleção dinâmica pelo usuário |
| portrait\_person | "a portrait photograph of a single person" | Genérico | Seleção dinâmica pelo usuário |
| cat | "a close-up photo of a domestic cat" | Genérico | Seleção dinâmica pelo usuário |
| dog | "a photo of a domestic dog or puppy" | Genérico | Seleção dinâmica pelo usuário |
| birds\_wildlife | "a photo of birds, farm animals, or wildlife" | Genérico | Seleção dinâmica pelo usuário |
| food\_meal | "a close-up food photo of a cooked meal on a plate" | Genérico | Seleção dinâmica pelo usuário |
| drinks\_coffee | "a photo of a cup of coffee, cocktails, or beverages on a table" | Genérico | Seleção dinâmica pelo usuário |
| vehicles | "a photograph of a car, motorcycle, or vehicle" | Genérico | Seleção dinâmica pelo usuário |
| plants\_garden | "a close-up photo of house plants, flowers, or a garden" | Genérico | Seleção dinâmica pelo usuário |
| crafts\_art | "a photo of handmade pottery, ceramics, crafts, or art" | Genérico | Seleção dinâmica pelo usuário |

> * **RF04.3:** Limiares de Decisão (Sigmoid Score):  
  * Utilitários: Considerado positivo se score \>= 0.60.  
  * Eventos/Ambientes/Genéricos: Considerado positivo se score \>= 0.35.

### **RF05: Persistência e Indexação (SQLite)**

> * **RF05.1:** Hashes, metadados EXIF e todas as tags de classificação serão gravados localmente em um banco SQLite (photo\_organizer.db).  
> * **RF05.2 (Retomada):** Arquivos cujo hash já exista no banco serão ignorados na etapa de inferência (SigLIP) em execuções subsequentes.

### **RF06: Regras de Roteamento (Criação de Pastas)**

As regras abaixo serão computadas com base nas preferências selecionadas pelo usuário na Web UI (RF01.2 e RF01.5):

> * **RF06.1 (Estrutura Base):** O agrupamento primário é sempre MM-AAAA (Mês-Ano).  
> * **RF06.2 (Utilitários):**  
  * Se o usuário desativou o agrupamento cronológico para documentos, o destino será rígido: Documentos/Comprovantes/{arquivo}.  
  * Se o usuário ativou o agrupamento cronológico, o destino incluirá a data: Documentos/Comprovantes/MM-AAAA/{arquivo}.  
> * **RF06.3 (Eventos e Ambientes):** Sempre criarão subpastas dentro do respectivo mês: MM-AAAA/Casamento/ ou MM-AAAA/Praia/.  
> * **RF06.4 (Genéricos):**  
  * Para as tags genéricas cujas checkboxes o usuário **marcou** no Painel de Decisão (ex: escolheu isolar os Gatos): o sistema criará a pasta MM-AAAA/Gato/ e moverá a foto.  
  * Para tags genéricas que o usuário **não marcou** (ou se a imagem não atingir limiar de nenhuma tag): a foto irá para o diretório padrão MM-AAAA/Geral/ ou MM-AAAA/.

### **RF07: Execução de Operações de Disco**

> * **RF07.1:** O cálculo do plano de diretórios (plan\_paths) ocorrerá inteiramente em memória e no banco de dados. A operação física no disco só ocorrerá após a aprovação do usuário na Fase 2\.  
> * **RF07.2 (Resolução de Colisões):**  
  * Hashes idênticos: abortar a cópia da imagem (tratar como duplicata no BD).  
  * Hashes diferentes com mesmo nome: anexar sufixo incremental no arquivo novo (nome\_1.jpg).

## **4\. Requisitos Não Funcionais (RNF)**

> * **RNF01 (Servidor Embutido):** Backend Go inicia servidor HTTP (porta primária 8080, ou a próxima livre) e abre o navegador automaticamente via pacote do sistema.  
> * **RNF02 (Zero-Dependency):** HTML/CSS/JS do painel da Fase 1 e Fase 2 devem estar empacotados dentro do binário (go:embed).  
> * **RNF03 (Concorrência e Streaming):** O pipeline em Go usará *goroutines* para indexação. A Web UI consumirá o status via *Server-Sent Events (SSE)*.  
> * **RNF04 (Gerenciamento do Sidecar Python):** O Go gerenciará o ciclo de vida do subprocesso SigLIP, monitorará o *healthcheck* local e emitirá *kill signals* na terminação do programa base.