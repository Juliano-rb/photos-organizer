# Documento de Requisitos do Sistema (SRS) — Final

## 1. Visão Geral do Produto

O **PhotoOrganizer** é uma aplicação utilitária desenvolvida em **Go**, projetada para organizar automaticamente fotos desordenadas. A ferramenta utiliza um modelo local de visão-linguagem (**SigLIP** via sidecar Python) para classificar o conteúdo das imagens, extrai metadados (EXIF) para cronologia e persiste todo o estado em um banco de dados **SQLite**. A interação ocorre por meio de uma **Web UI local** embutida no próprio executável, permitindo configurações, acompanhamento em tempo real e retomada de processos interrompidos.

## 2. Arquitetura do Sistema

O sistema é composto por três camadas principais:

1. **Frontend (Web UI):** Arquivos HTML/JS/CSS embutidos no executável via `go:embed`, rodando no navegador do usuário.
2. **Backend (Go CLI/Server):** Orquestrador principal, responsável pela varredura de disco, banco de dados SQLite, extração de EXIF, movimentação de arquivos e exposição da API HTTP/SSE para o Frontend.
3. **Sidecar de Inferência (Python):** Processo isolado gerenciado pelo Go que carrega o modelo SigLIP (via ONNX/DirectML ou PyTorch) e expõe um endpoint local para classificação rápida de imagens.

---

## 3. Requisitos Funcionais (RF)

### RF01: Interface e Inicialização (Web UI)

* **RF01.1:** Ao ser executada, a aplicação deve abrir automaticamente uma página no navegador padrão do sistema operacional.
* **RF01.2:** A interface web deve exibir e permitir a edição de:
  * Diretório alvo (pré-preenchido com o diretório atual de execução).
  * Diretório de destino.
  * Modo de operação: **Copiar** (padrão) ou **Mover**.
* **RF01.3:** A interface deve possuir uma tabela estática listando as categorias e tags suportadas pelo classificador visual.
* **RF01.4:** A interface deve possuir uma tabela reativa listando os arquivos já varridos e categorizados, lidos a partir do banco de dados.
* **RF01.5:** Deve existir um botão principal para iniciar/pausar o processamento.
* **RF01.6:** O status do processamento (varredura, classificação visual e operações de disco) deve ser reportado e atualizado na interface em tempo real.

### RF02: Descoberta e Varredura de Arquivos

* **RF02.1:** O sistema deve percorrer recursivamente o diretório alvo.
* **RF02.2:** Deve processar exclusivamente as seguintes extensões: `.jpg`, `.jpeg`, `.png`, `.heic`, `.webp`, `.dng`.
* **RF02.3:** Deve calcular o hash criptográfico `SHA-256` de cada arquivo antes do processamento para garantir deduplicação determinística.

### RF03: Extração de Metadados EXIF

* **RF03.1:** O sistema deve extrair as seguintes tags EXIF: `DateTimeOriginal`, `OffsetTime`, `Make`, `Model`, `GPSLatitude` e `GPSLongitude`.
* **RF03.2:** Em caso de ausência de metadados de data no EXIF, o sistema deve aplicar os seguintes fallbacks na ordem exata:
  1. Extração de data no nome do arquivo via Expressão Regular (ex: `IMG_20240512_...`).
  2. Data de modificação do arquivo no sistema de arquivos (`ModTime`).

### RF04: Classificação Visual Zero-Shot (SigLIP)

* **RF04.1:** A classificação deve ser executada pelo modelo SigLIP, comparando as imagens recebidas com embeddings de texto pré-computados (calculados uma única vez na inicialização do sidecar).
* **RF04.2:** O classificador deve avaliar a imagem contra a taxonomia exata abaixo e mapeá-la para o respectivo comportamento/diretório:

| Chave Interna | Prompt Textual SigLIP | Comportamento de Roteamento |
| --- | --- | --- |
| `receipt_invoice` | `"a photo of a paper receipt, bill, or tax invoice"` | Isolamento documental: `Documentos/Comprovantes/` |
| `document_text` | `"a photograph of a printed document, contract, or form"` | Isolamento documental: `Documentos/Texto/` |
| `id_card` | `"a photo of an identity card, driver license, or passport"` | Isolamento documental: `Documentos/Identidade/` |
| `screenshot` | `"a screenshot of a mobile phone screen or computer desktop"` | Isolamento de sistema: `Screenshots/` |
| `handwritten_notes` | `"a photo of a notebook page with handwriting or a whiteboard"` | Isolamento documental: `Documentos/Anotacoes/` |
| `birthday_party` | `"a photo of a birthday party with cake or party decorations"` | Subpasta dinâmica: `MM-AAAA/Aniversario/` |
| `wedding_ceremony` | `"a photo of a wedding ceremony, bride, or wedding reception"` | Subpasta dinâmica: `MM-AAAA/Casamento/` |
| `concert_show` | `"a photo of a music concert, live stage performance, or festival"` | Subpasta dinâmica: `MM-AAAA/Show/` |
| `sports_event` | `"a photo of people playing sports or an athletic competition"` | Subpasta dinâmica: `MM-AAAA/Esportes/` |
| `barbecue_party` | `"a photo of a barbecue gathering, churrasco, or outdoor grill party"` | Subpasta dinâmica: `MM-AAAA/Churrasco/` |
| `beach_ocean` | `"a photo of a beach, ocean shore, and sea"` | Subpasta dinâmica: `MM-AAAA/Praia/` |
| `hiking_nature` | `"a photo of a hiking trail, mountains, or green forest"` | Subpasta dinâmica: `MM-AAAA/Natureza/` |
| `cityscape_street` | `"a photo of city streets, urban architecture, and buildings"` | Subpasta dinâmica: `MM-AAAA/Cidade/` |
| `sunset_sunrise` | `"a scenic photograph of a sunset or sunrise in the sky"` | Subpasta dinâmica: `MM-AAAA/PorDoSol/` |
| `pool_resort` | `"a photo of a swimming pool or vacation resort"` | Subpasta dinâmica: `MM-AAAA/Piscina/` |
| `home_indoor` | `"a photo taken indoors inside a house, bedroom, or living room"` | Subpasta dinâmica: `MM-AAAA/Casa/` |
| `selfie` | `"a close-up selfie photograph of a person"` | Tag no BD, sem subpasta (fica em `MM-AAAA/Geral/`) |
| `group_portrait` | `"a group photo of friends or family posing together"` | Tag no BD, sem subpasta (fica em `MM-AAAA/Geral/`) |
| `baby_child` | `"a photograph of a baby, toddler, or young child"` | Tag no BD, sem subpasta (fica em `MM-AAAA/Geral/`) |
| `portrait_person` | `"a portrait photograph of a single person"` | Tag no BD, sem subpasta (fica em `MM-AAAA/Geral/`) |
| `cat` | `"a close-up photo of a domestic cat"` | Tag no BD, sem subpasta (fica em `MM-AAAA/Geral/`) |
| `dog` | `"a photo of a domestic dog or puppy"` | Tag no BD, sem subpasta (fica em `MM-AAAA/Geral/`) |
| `birds_wildlife` | `"a photo of birds, farm animals, or wildlife"` | Tag no BD, sem subpasta (fica em `MM-AAAA/Geral/`) |
| `food_meal` | `"a close-up food photo of a cooked meal on a plate"` | Tag no BD, sem subpasta (fica em `MM-AAAA/Geral/`) |
| `drinks_coffee` | `"a photo of a cup of coffee, cocktails, or beverages on a table"` | Tag no BD, sem subpasta (fica em `MM-AAAA/Geral/`) |
| `vehicles` | `"a photograph of a car, motorcycle, or vehicle"` | Tag no BD, sem subpasta (fica em `MM-AAAA/Geral/`) |
| `plants_garden` | `"a close-up photo of house plants, flowers, or a garden"` | Tag no BD, sem subpasta (fica em `MM-AAAA/Geral/`) |
| `crafts_art` | `"a photo of handmade pottery, ceramics, crafts, or art"` | Tag no BD, sem subpasta (fica em `MM-AAAA/Geral/`) |

* **RF04.3:** Limiares de Decisão (Sigmoid Score):
  * Utilitários/Documentos: Prioridade máxima. Atribuído imediatamente se `score >= 0.60`.
  * Demais categorias: Atribuição de tag ou subpasta se `score >= 0.35`.

### RF05: Persistência e Indexação (SQLite)

* **RF05.1:** Todo o estado de varredura, arquivos processados, metadados EXIF e classificações visuais devem ser salvos em um banco de dados SQLite local.
* **RF05.2:** O sistema deve suportar tolerância a falhas e retomada (resume). Arquivos cujo hash criptográfico já constem no banco de dados não devem ser reprocessados no SigLIP e no EXIF.

### RF06: Roteamento e Agrupamento

* **RF06.1:** A estrutura de diretórios base será cronológica no formato `MM-AAAA`.
* **RF06.2:** Imagens categorizadas como utilitários, documentos ou screenshots devem ignorar o roteamento cronológico padrão e ser direcionadas para seus diretórios raízes específicos (`Documentos/` e `Screenshots/`), conforme mapeamento no RF04.2.
* **RF06.3:** Imagens com tags que geram subpastas dinâmicas (ex: `beach_ocean`, `birthday_party`) devem ser agrupadas dentro do diretório do mês correspondente (ex: `05-2026/Praia/`).
* **RF06.4:** Imagens com tags genéricas (ex: `cat`, `food_meal`) ou que não atinjam o limiar mínimo do modelo SigLIP devem ser direcionadas para o diretório `MM-AAAA/Geral/`.

### RF07: Execução de Operações de Disco

* **RF07.1:** O sistema deve oferecer suporte a modo simulação (*dry-run*), gerando as estimativas e caminhos na Web UI sem alterar arquivos no disco.
* **RF07.2:** Em caso de colisão de nomes no diretório de destino:
  * Se os arquivos tiverem hashes idênticos, o sistema registrará como duplicata e abortará a cópia.
  * Se os arquivos tiverem hashes diferentes, o sistema anexará um sufixo numérico incremental (`_1`, `_2`) ao arquivo novo.

---

## 4. Requisitos Não Funcionais (RNF)

* **RNF01 (Servidor Embutido e Porta Dinâmica):** O processo backend em Go inicializará um servidor HTTP na porta `8080`. Caso esteja indisponível, o sistema buscará automaticamente a próxima porta local livre.
* **RNF02 (Distribuição Zero-Dependency):** Os arquivos frontend devem ser incluídos no binário Go compilado usando a diretiva `go:embed`. O sistema não exigirá a instalação de servidores web externos.
* **RNF03 (Comunicação Assíncrona UI-Backend):** A transferência de informações de progresso do backend para a interface gráfica deve ser implementada via *Server-Sent Events (SSE)* ou *WebSockets*.
* **RNF04 (Concorrência):** O pipeline de processamento em Go deve utilizar *goroutines* independentes para I/O de disco, extração de EXIF e enfileiramento das requisições HTTP para o sidecar SigLIP.
* **RNF05 (Gerenciamento de Ciclo de Vida do Sidecar):** O executável em Go deve orquestrar a inicialização do processo Python do SigLIP, monitorar seu *healthcheck* e forçar seu encerramento via IPC/OS Signal quando a aplicação principal for fechada.