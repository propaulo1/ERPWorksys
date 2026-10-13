# ERP Worksys — Arquitetura

Documento de referência da arquitetura do ERP da Worksys (engenharia elétrica e
telecomunicações). O plano de entregas por fases está em [ROADMAP.md](ROADMAP.md).

## 1. Contexto e premissas

| Item | Definição |
|---|---|
| Empresas atendidas | 2 CNPJs: uma no **Simples Nacional** e outra no **Lucro Presumido** (serviços) |
| Nota fiscal | **Não** é emitida pelo sistema (processo manual nas prefeituras). O ERP apenas **registra** a NF emitida (número, data, valor, retenções) para gerar contas a receber e provisionar impostos |
| Bancos | Itaú e Bradesco, nas duas empresas |
| Acesso | Interface web, inclusive celular dos técnicos de campo |
| Hospedagem | Servidores próprios: HP ProLiant DL380 G7, VMware ESXi 6.x, Xeon X5690 |
| Identidade visual | Inspirada em www.wsredes.com.br |

## 2. Restrição de hardware (Xeon X5690) e escolhas de software

O X5690 (Westmere, 2011) suporta SSE4.2 e POPCNT, mas **não suporta AVX/AVX2**.
Em nomenclatura atual ele é um processador **x86-64-v2**. Isso afeta várias escolhas:

| Componente | Situação no X5690 | Decisão |
|---|---|---|
| PostgreSQL 16/17 | Compilado para x86-64 genérico, roda sem AVX | **Usar** |
| Python 3.12/3.13 + Django | Sem dependência de AVX | **Usar** |
| MongoDB 5.0+ | Exige AVX, não inicia | Descartado |
| RHEL 10 / AlmaLinux 10 / Rocky 10 | Exigem x86-64-v3 (AVX2), não instalam | Descartado |
| Ubuntu Server 24.04 LTS / Debian 12 | Baseline x86-64, roda normalmente | **Usar** (Ubuntu 24.04 LTS recomendado) |
| Imagens Docker oficiais (postgres, python, nginx) | Baseline x86-64 | **Usar** |
| Bibliotecas de dados (pandas, numpy) | Baseline até x86-64-v2, rodam | Permitido |
| Polars (build padrão), TensorFlow, alguns bancos vetoriais | Exigem AVX/AVX2 | Evitar (ou usar builds "lts-cpu") |

Regra para o futuro: **qualquer nova dependência binária deve ser testada na VM de
homologação antes de ir para produção**, porque o erro típico é `Illegal instruction`
na inicialização.

## 3. Stack

- **Backend:** Python 3.13 + Django 5.2 LTS (suporte até abril/2028).
- **Banco de dados:** PostgreSQL 16.
- **Interface:** páginas renderizadas no servidor (Django templates) com CSS próprio
  e JavaScript leve (htmx quando houver interação dinâmica). Sem build de frontend,
  o que simplifica a manutenção em servidor próprio.
- **App de campo:** **PWA** (Progressive Web App) servida pelo próprio ERP. O técnico
  "instala" o atalho no celular pelo navegador, sem loja de aplicativos. Funciona com
  câmera (fotos), GPS e modo offline com envio posterior.
- **Servidor de aplicação:** Gunicorn atrás de Nginx (HTTPS).
- **Tarefas agendadas:** cron/systemd timers chamando comandos do Django
  (lembretes de follow-up, alertas de vencimento, backup). Fila assíncrona (Celery/Redis)
  só se houver necessidade real.
- **Implantação:** uma VM Ubuntu 24.04 no ESXi com Docker Compose
  (serviços `db`, `web`, `nginx`). Alternativa equivalente sem Docker: pacotes nativos
  + systemd.

### Por que um monólito Django

Uma equipe pequena, um servidor e módulos muito interligados (proposta → projeto →
cronograma → diário de obra → estoque → financeiro) favorecem um **monólito modular**:
um só código, um só banco, transações consistentes entre módulos, e o admin do Django
pronto para cadastros auxiliares. Cada módulo é um app Django separado, com
fronteiras claras, e pode ser extraído depois se necessário.

## 4. Visão de módulos

```
                         ┌───────────────────────────┐
                         │   Núcleo (core/accounts)  │
                         │ Empresas · Usuários ·     │
                         │ Perfis · Pessoas (cli/for)│
                         └─────────────┬─────────────┘
        ┌───────────────┬──────────────┼───────────────┬───────────────┐
        ▼               ▼              ▼               ▼               ▼
   ┌─────────┐    ┌───────────┐  ┌───────────┐   ┌──────────┐    ┌──────────┐
   │   CRM   │──▶ │ Pré-vendas│─▶│ Projetos /│──▶│  Campo   │    │ Suporte  │
   │ contatos│    │ propostas │  │ Engenharia│   │ OS · PWA │◀───│ chamados │
   │followup │    └─────┬─────┘  │ cronograma│   │ diário   │    └──────────┘
   └─────────┘          │        └─────┬─────┘   └────┬─────┘
                        │              │              │
                        ▼              ▼              ▼
                   ┌──────────────────────────────────────┐
                   │ Estoque (materiais · ferramentas ·   │
                   │ EPI individual/coletivo)             │
                   └──────────────────┬───────────────────┘
                                      ▼
                   ┌──────────────────────────────────────┐
                   │ Financeiro (2 empresas · conciliação │
                   │ Itaú/Bradesco · fluxo de caixa)      │
                   └──────────────────────────────────────┘
```

### 4.1 Núcleo (fase 0)
- **Empresa**: as duas empresas, com regime tributário, CNPJ, alíquotas de referência.
- **Usuário**: login por usuário/senha, perfis (administrador, financeiro, comercial,
  engenharia, almoxarifado, suporte, técnico de campo), empresas que cada usuário pode ver.
- **Empresa ativa**: o usuário escolhe no topo da tela em qual empresa está trabalhando,
  ou "Consolidado" nas telas que permitem visão conjunta.
- **Pessoas** (fase 1): cadastro único de clientes, fornecedores, contatos e colaboradores,
  compartilhado entre as empresas (um cliente pode comprar das duas).
- Auditoria: registro de quem criou/alterou cada documento relevante.

### 4.2 Financeiro
- **Plano de contas** e **centros de custo** (por obra/projeto, por área).
- **Contas bancárias** por empresa (Itaú e Bradesco).
- **Contas a pagar e a receber**, com parcelas, anexos (boleto, NF), vínculo opcional
  com projeto/obra e centro de custo.
- **Registro de NF emitida** (manual na prefeitura): gera o título a receber e as
  retenções (ISS, INSS, IR, PIS/COFINS/CSLL quando houver).
- **Provisão de impostos por regime**, para alimentar o fluxo de caixa:
  - *Simples Nacional:* DAS sobre faturamento conforme anexo e faixa da receita bruta
    dos últimos 12 meses (inclui cálculo do Fator R quando aplicável).
  - *Lucro Presumido (serviços):* PIS 0,65% e COFINS 3% mensais (cumulativo); IRPJ
    (presunção de 32%, 15% + adicional de 10%) e CSLL (presunção de 32%, 9%) trimestrais;
    ISS conforme município.
  - As alíquotas ficam em tabela parametrizável; o contador valida.
- **Transferências entre contas e entre empresas** (mútuos/intercompany) marcadas
  como tal, para não inflar receitas/despesas no consolidado.
- **Fluxo de caixa**:
  - *Realizado* (a partir dos lançamentos conciliados) e *previsto* (títulos em aberto
    + provisões de impostos + recorrências como folha e aluguel).
  - **Individual** por empresa e **consolidado** das duas, com eliminação das
    transferências entre elas.
  - Visões diária, semanal e mensal; saldo projetado por conta.
- **DRE gerencial** por empresa e consolidada (fase posterior).

### 4.3 Conciliação bancária (Itaú e Bradesco)

Hoje o extrato é copiado e colado manualmente. Opções, da mais simples à mais
automatizada:

| Opção | Como funciona | Custo / esforço | Plano |
|---|---|---|---|
| **1. Colar extrato** | Usuário cola o texto copiado do internet banking; o sistema interpreta as colunas (data, histórico, documento, valor, saldo) | Nenhum custo; mantém o hábito atual | **Fase 1** (transição) |
| **2. Arquivo OFX** | Itaú Empresas e Bradesco Net Empresa permitem exportar o extrato em OFX (formato "Money"). Usuário faz upload; o sistema importa sem duplicar (usa o FITID de cada lançamento) | Nenhum custo; formato padrão e confiável | **Fase 1** (principal) |
| **3. CNAB 240 de extrato** | O banco envia diariamente arquivo de extrato para conciliação (layout CNAB 240, segmento E), por VAN ou pelo internet banking | Requer contratar o serviço com o gerente; pode ter tarifa | Avaliar na fase 7 |
| **4. API do banco** | APIs de extrato do Itaú (devportal.itau.com.br) e Bradesco (developers.bradesco.com.br), com certificado digital e contrato | Contrato com cada banco, certificado, homologação | Avaliar na fase 7 |
| **5. Agregador Open Finance** | Serviço terceiro (ex.: Pluggy, Belvo) que lê as contas via Open Finance com consentimento | Mensalidade por conta conectada | Avaliar na fase 7 |

Recomendação: começar com **OFX + colar extrato** na fase 1, que já elimina a
digitação e permite conciliação automática. Automatizar a captura (opções 3 a 5) depois,
quando o restante do financeiro estiver em uso — a regra de conciliação é a mesma,
só muda a origem dos lançamentos. **Confirmar com os gerentes do Itaú e Bradesco**
quais dessas modalidades estão disponíveis nos planos atuais das duas empresas.

**Motor de conciliação:**
1. Importa lançamentos do extrato (sem duplicar).
2. Sugere pares automáticos com títulos/lançamentos do sistema por valor exato + data
   próxima (± N dias) + documento/CNPJ no histórico.
3. Regras configuráveis por histórico (ex.: "TAR PACOTE" → despesa bancária; "PIX
   RECEBIDO CNPJ X" → cliente X).
4. Usuário confirma, ajusta, divide (um crédito pagando várias parcelas) ou cria o
   lançamento a partir da linha do extrato.
5. Saldo conciliado do sistema deve bater com o saldo do extrato; divergência é sinalizada.

### 4.4 CRM
- Contas (empresas clientes) e contatos, origem do lead, segmento.
- Oportunidades em funil (prospecção → qualificação → proposta → negociação →
  ganho/perdido), com valor estimado e empresa do grupo que vai faturar.
- **Follow-ups**: próxima ação com data e responsável; painel "meus follow-ups de hoje";
  lembrete por e-mail; histórico de interações (ligação, visita, e-mail, WhatsApp).
- Motivo de perda para análise.

### 4.5 Pré-vendas (propostas)
- Proposta vinculada à oportunidade, com **revisões** (R0, R1, ...).
- Composição de custo: materiais (do cadastro de estoque/preços), mão de obra
  (horas × função), terceiros, despesas indiretas e **BDI**/margem; impostos conforme
  a empresa que vai faturar.
- Geração do documento da proposta (PDF) no modelo da Worksys.
- Proposta aceita → **gera o projeto** com escopo, orçamento e itens já preenchidos.
- **Seguir os modelos em Excel existentes** (campos, fórmulas, layout); importação
  das planilhas atuais quando possível.

### 4.6 Engenharia / Projetos
- Projeto (obra) com cliente, empresa executora, orçamento, responsável técnico.
- **EAP e cronograma** (atividades, duração, dependências, marcos), visualização em Gantt,
  linha de base x realizado.
- Quantitativos previstos por atividade (ex.: 1.200 m de cabo, 48 pontos de rede),
  base para medir avanço físico e produtividade.
- Medições/faturamento por etapa (gera previsão de recebimento no fluxo de caixa).
- Documentos do projeto (desenhos, ART, as-built) com controle de revisão.
- Custo realizado (materiais saídos do estoque, horas apontadas, despesas) x orçado.

### 4.7 Estoque (materiais, ferramentas e EPI)
- Almoxarifados (sede, obras, veículos).
- **Materiais de consumo:** entrada, saída para obra/OS, transferência, inventário,
  estoque mínimo, custo médio.
- **Ferramentas e equipamentos (patrimônio):** controle por número de série/patrimônio,
  **cautela** (empréstimo a técnico ou obra) com devolução, calibração e manutenção.
- **EPI individual:** entrega por colaborador com **Certificado de Aprovação (CA)**,
  data, quantidade, validade e troca; **ficha de EPI** assinada (exigência da NR-6).
- **EPC / EPI coletivo:** alocado à obra ou equipe, com inspeções.
- Reservas de material por projeto/atividade do cronograma.

### 4.8 Suporte técnico (chamados)
- Abertura de chamado por cliente/contrato/local, categoria e prioridade.
- **SLA** por contrato (tempo de atendimento e solução), alerta de vencimento.
- Atribuição a técnico, histórico de interações, anexos.
- Chamado que exige ida a campo → gera **OS de manutenção**.
- Portal ou e-mail para o cliente acompanhar (fase posterior).

### 4.9 Técnicos de campo

**Manutenção (OS):**
- OS com cliente, local, equipamento, defeito relatado.
- Apontamento pelo celular: chegada/saída (com GPS), horas, serviço executado,
  materiais usados (baixa no estoque), fotos antes/depois, assinatura do cliente.
- Fechamento da OS atualiza o chamado e gera o relatório para o cliente.

**Instalação (diário de obra no celular):**
- O técnico vê **as atividades do cronograma da obra atribuídas a ele/equipe** no dia.
- Para cada atividade: informa a quantidade executada (ex.: "120 m de cabo") ou o %
  concluído, com poucos toques; fotos; observações.
- Registro do dia: equipe presente, clima, ocorrências/impedimentos, materiais recebidos.
- **Funciona offline** e sincroniza quando houver sinal.
- O apontamento atualiza o avanço físico do cronograma em tempo real para a engenharia.

**Produtividade por técnico:**
- Horas apontadas x quantidades executadas por tipo de serviço (ex.: m/h, pontos/dia).
- Planejado x realizado por técnico, equipe e obra; OS concluídas e tempo médio.

## 5. Modelo multiempresa

- Todo documento financeiro, de projeto, de estoque e de OS pertence a **uma empresa**
  (`empresa_id`).
- Cadastros de pessoas (clientes, fornecedores, colaboradores) e de itens são
  **compartilhados**.
- O usuário só vê dados das empresas a que tem acesso; telas de relatório oferecem
  "Consolidado" quando o usuário tem acesso às duas.

## 6. Segurança e operação

- HTTPS obrigatório (certificado interno ou Let's Encrypt, se exposto à internet).
- **Acesso externo para o app de campo**: os técnicos precisam alcançar o servidor pelo
  4G. Opções: publicar o Nginx na internet com HTTPS e firewall, ou VPN no celular.
  Decisão a tomar antes da fase 6.
- Senhas com hash forte (padrão Django), bloqueio por tentativas, sessões com expiração.
- **Backup:** `pg_dump` diário + cópia dos anexos, com retenção (ex.: 7 diários,
  4 semanais, 12 mensais), copiado para fora da VM; teste de restauração mensal.
- Snapshot da VM antes de cada atualização.
- Logs de acesso e de alterações.

## 7. Estrutura do código

```
config/            configurações do Django (settings, urls, wsgi)
apps/
  core/            empresas, empresa ativa, layout, painel inicial
  accounts/        usuários, perfis, login
  (próximas)       cadastros, financeiro, crm, propostas, projetos,
                   estoque, suporte, campo
templates/         templates base e por app
static/            CSS/JS/imagens (identidade Worksys)
docs/              arquitetura, roadmap, implantação
deploy/            nginx e scripts de backup
```

## 8. Pendências de informação

- **Planilhas Excel atuais** de propostas, projetos e financeiro (base das fases 1 a 3).
- Dados das duas empresas (razão social, CNPJ, município do ISS, anexo do Simples).
- Exemplo de extrato (OFX ou texto colado) de cada banco, sem dados sensíveis se preferir.
- Logo e cores oficiais da Worksys (o layout atual usa cores provisórias em variáveis CSS).
- Decisão sobre acesso externo (internet x VPN) para o app de campo.
