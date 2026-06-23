# 🏭 Controle de Estoque — Almoxarifado

> **Sistema interno de gestão de estoque para o Almoxarifado da Maia e Borba S/A**  
> Atualmente focado no controle de **itens de higiene e limpeza** (papel higiênico, papel toalha e sabonete líquido), com visão de expansão para um **sistema profissional multi-item de gestão de estoque**.

---

## 📋 Visão Geral

Este sistema automatiza os processos manuais do almoxarifado:

- **Pedidos semanais** — Calcula a necessidade de reposição com base no estoque atual vs. níveis mínimo e ideal, extrai pedidos de compra por e-mail, e dispara automaticamente o e-mail de solicitação ao fornecedor.
- **Relatórios mensais** — Gera relatórios em PDF detalhando todas as saídas do período, separados por centro de custo (Shopping / Terminal), com valores unitários e totais, e os envia por e-mail com os PDFs anexados.
- **Registro manual de movimentações** — Interface web (Flask) para registrar saídas e recebimentos de materiais, incluindo divisão automática para reposição do subsolo.

---

## 🧱 Stack Tecnológica

| Camada       | Tecnologia                                         |
|--------------|----------------------------------------------------|
| **Linguagem** | Python 3.12+                                      |
| **CLI**       | Terminal interativo com `pyfiglet`                 |
| **Web Server**| Flask + Flask-SocketIO + Eventlet                  |
| **Banco**     | SQLite (via `sqlite3`)                             |
| **PDF**       | ReportLab                                          |
| **E-mail**    | Selenium (Firefox) — automação do Webmail Locaweb  |
| **Frontend**  | Jinja2 + Tailwind CSS (CDN)                        |
| **Ícones**    | Lucide (via CDN)                                   |

---

## 🧩 Estrutura do Projeto

```
├── higienicos.py                  # CLI principal (pedidos + relatórios)
├── server.py                      # Servidor web Flask (registro manual)
├── .gitignore
├── README.md
│
├── modules/
│   ├── __init__.py                # Exporta módulos: DBCore, WebmailCore, PDFManipulator
│   │
│   ├── DBCore/
│   │   ├── __init__.py            # Classe `start` — toda camada de dados
│   │   └── db.sqlite              # Banco SQLite (NÃO versionado)
│   │
│   ├── PDFManipulator/
│   │   ├── __init__.py            # Classe `start` — geração de relatórios PDF
│   │   └── pdf_files/             # PDFs gerados anexados aos e-mails
│   │
│   └── WebmailCore/
│       ├── __init__.py            # Classe `start` — automação do webmail
│       ├── att.png                # Logotipo para assinatura de e-mail
│       ├── PedidoEmail_template.html      # Template HTML para e-mail de pedido
│       └── RelatorioEmail_template.html   # Template HTML para e-mail de relatório
│
├── static/
│   └── js/
│       └── insert.js              # JS de envio do formulário de movimentação
│
└── templates/
    └── insert.html                # Página de registro manual de movimentações
```

---

## ⚙️ Funcionalidades Atuais

### 1. 📦 Pedido Semanal de Reposição (`higienicos.py` — opção 1)

1. Conecta ao webmail e busca o e-mail de pedido de compra do Edielson.
2. Extrai os valores de compra (papel higiênico, toalha, sabonete) para os centros de custo COMLI (Shopping) e TR1 (Terminal).
3. Atualiza o estoque da R3 com as compras encontradas.
4. Calcula a necessidade de cada item:
   - `necessidade = max(0, min(ideal - atual, disponível_R3))` se >= mínimo, senão 0.
5. Exibe prévia no terminal e permite ajuste manual dos valores.
6. Envia e-mail para a R3 Suprimentos com os valores a entregar.
7. Registra a compra no banco de dados.

### 2. 📊 Relatório Mensal de Saídas (`higienicos.py` — opção 2)

1. Define o período (mês anterior ou atual) automaticamente.
2. Consulta todas as movimentações do período no banco de dados.
3. Gera 3 PDFs:
   - **Relatório COMLI** (saídas do Shopping)
   - **Relatório TR1** (saídas do Terminal)
   - **Relatório Total** (consolidado)
4. Cada relatório contém:
   - Cabeçalho com período, data e página
   - Itens agrupados com data, nota fiscal, unidade, quantidade, valor unitário e valor total
   - Totais por item e total geral do centro de custo
   - Responsável por cada movimentação
5. Busca o e-mail de compra para atualizar o estoque total.
6. Envia e-mail com os 3 PDFs anexados e tabela consolidada no corpo do e-mail.

### 3. 🌐 Interface Web de Registro (`server.py`)

Formulário para registrar movimentações manuais:
- **Saída para Shopping / Terminal** — registra saída no centro de custo selecionado.
- **Reposição do Subsolo** — divide automaticamente os valores entre COMLI e TR1 alternando a cada registro.
- **Recebimento de Mercadoria** — valida contra notas fiscais pendentes e atualiza o estoque.

---

## 🗄️ Modelo de Dados

### `stock`
| Coluna       | Tipo    | Descrição                              |
|--------------|---------|----------------------------------------|
| `id`         | INTEGER | PK — 1212/1213/1214 (R3), 1322/1323/1324 (ALMOX) |
| `name`       | TEXT    | Nome do item                           |
| `quantity`   | REAL    | Quantidade atual                       |
| `unityType`  | TEXT    | BOX / ROL / GAL                        |
| `unityPrice` | REAL    | Preço unitário                         |
| `minimum`    | REAL    | Estoque mínimo                         |
| `ideal`      | REAL    | Estoque ideal                          |
| `place`      | TEXT    | ALMOX ou R3                            |

### `movements`
| Coluna         | Tipo    | Descrição                     |
|----------------|---------|-------------------------------|
| `id`           | INTEGER | PK auto-increment             |
| `date`         | TEXT    | Data da movimentação (DD/MM/AA) |
| `hig`          | REAL    | Quantidade de papel higiênico |
| `toa`          | REAL    | Quantidade de papel toalha    |
| `sab`          | REAL    | Quantidade de sabonete        |
| `responsible`  | TEXT    | Responsável pela retirada     |
| `cc`           | TEXT    | Centro de custo (COMLI/TR1)   |
| `toUnderground`| INTEGER | Flag de reposição do subsolo |

### `purchases`
| Coluna           | Tipo    | Descrição                          |
|------------------|---------|------------------------------------|
| `id`             | INTEGER | PK auto-increment                  |
| `toPlace`        | TEXT    | ALMOX ou R3                        |
| `hig` / `toa` / `sab` | REAL | Quantidades compradas        |
| `date`           | TEXT    | Mês/ano referência                 |
| `received`       | INTEGER | Flag de recebimento                |
| `shippingNoteId` | TEXT    | Número da nota fiscal              |

---

## 🚀 Como Executar

### CLI (Pedidos / Relatórios)

```bash
python higienicos.py
```

### Servidor Web (Registro de Movimentações)

```bash
python server.py
```

Acesse: `http://127.0.0.1:5000`

### Dependências

```bash
pip install -r requirements.txt
```

---

## 🔮 Roadmap — Sistema Profissional de Gestão de Estoque

O sistema atual foi construído para atender uma necessidade específica (3 itens de higiene), mas a arquitetura foi desenhada para evoluir para um **sistema completo multi-item**. Abaixo estão as direções planejadas:

### 🏗️ Arquitetura

- [ ] **Banco de dados relacional genérico** — Substituir os campos fixos `hig`/`toa`/`sab` por um modelo normalizado com tabela de itens, movimentos por item, e categorias.
- [ ] **API REST estruturada** — Migrar de um CLI + Flask monólito para uma API com endpoints versionados (`/api/v1/`).
- [ ] **Autenticação e autorização** — Controle de acesso por nível de usuário (almoxarife, administrador, visualizador).

### 📦 Gestão de Itens

- [ ] **Cadastro dinâmico de itens** — CRUD completo de produtos com suporte a múltiplas unidades (peça, kg, litro, caixa, rolo, galão).
- [ ] **Múltiplos almoxarifados** — Suporte a diferentes locais de estocagem além de ALMOX e R3.
- [ ] **Categorias e grupos** — Classificação hierárquica de itens.
- [ ] **Código de barras / SKU** — Leitura e busca por código de barras.

### 📥 Movimentações

- [ ] **Tipos genéricos de movimento** — Entrada, saída, transferência, ajuste, inventário.
- [ ] **Ordem de compra integrada** — Fluxo completo: requisição → cotação → pedido → recebimento.
- [ ] **Nota fiscal eletrônica** — Leitura de XML de NF-e para entrada automática.
- [ ] **Transferência entre almoxarifados** — Com rastreabilidade de lote.

### 📊 Relatórios

- [ ] **Relatórios configuráveis** — Seleção de período, centro de custo, item, tipo de movimento.
- [ ] **Dashboard em tempo real** — Gráficos de giro de estoque, nível de serviço, rupturas.
- [ ] **Exportação multi-formato** — PDF, Excel, CSV, Google Sheets.

### 🤖 Automação

- [ ] **Regras de reposição inteligentes** — Algoritmo configurável por item (ponto de pedido, lote econômico, sazonalidade).
- [ ] **Integração com fornecedores** — EDI ou API para envio automático de pedidos.
- [ ] **Notificações** — Alertas de estoque crítico, pedidos atrasados, vencimentos.
- [ ] **Multie-mail** — Suporte a qualquer provedor (SMTP, Outlook, Gmail API) em vez de depender de Selenium + webmail específico.

### 🖥️ Frontend

- [ ] **SPA moderna** — React / Vue + TypeScript substituindo o formulário Jinja2 atual.
- [ ] **Modo offline** — Progressive Web App para uso em áreas sem internet.
- [ ] **Aplicativo mobile** — React Native ou Flutter para conferência de estoque com leitor de código de barras.

---

## 🧑‍💻 Desenvolvimento

Projeto mantido internamente por mim Almoxarife da Maia & Borba S.A.

```text
Autor:  Gustavo Ribeiro
GitHub: https://github.com/GugaSan4004/Controle-de-Estoque
```
