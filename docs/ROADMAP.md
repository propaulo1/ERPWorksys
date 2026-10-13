# ERP Worksys — Roadmap por fases

Cada fase entrega algo utilizável em produção. A ordem prioriza o que mais
consome trabalho manual hoje (financeiro e conciliação) e respeita as dependências
entre módulos (proposta → projeto → diário de obra). Arquitetura em
[ARQUITETURA.md](ARQUITETURA.md).

| Fase | Entrega | Depende de | Insumos necessários |
|---|---|---|---|
| **0. Base** | Projeto Django, login, usuários e perfis, cadastro das 2 empresas, seleção de empresa ativa, layout Worksys, Docker Compose para a VM | — | — |
| **1. Cadastros e Financeiro** | Pessoas (clientes/fornecedores), plano de contas, centros de custo, contas bancárias, contas a pagar/receber, registro de NF emitida, importação de extrato **OFX e colar texto** (Itaú e Bradesco), conciliação, fluxo de caixa realizado/previsto **individual e consolidado**, provisão de impostos (Simples e Presumido) | 0 | Planilha Excel do financeiro, exemplos de extrato, plano de contas do contador |
| **2. CRM e Pré-vendas** | Contas, contatos, oportunidades em funil, follow-ups com lembretes, propostas com revisões, composição de custo/BDI, PDF da proposta | 1 (pessoas) | Planilha Excel de propostas, modelo de proposta em PDF/Word |
| **3. Projetos / Engenharia** | Projeto gerado a partir da proposta, EAP, cronograma (Gantt), linha de base, medições, documentos, custo orçado x realizado | 2 | Planilha Excel de projetos/cronogramas |
| **4. Estoque, ferramentas e EPI** | Almoxarifados, materiais, movimentações, cautela de ferramentas, EPI individual com CA e ficha (NR-6), EPC por obra, reservas por projeto | 1, 3 | Lista de itens e saldos atuais |
| **5. Suporte e OS de manutenção** | Chamados com SLA, OS de manutenção, apontamento de horas e materiais, relatório ao cliente | 4 | Contratos de manutenção e SLAs |
| **6. App de campo (PWA) e diário de obra** | PWA instalável, atividades do dia vindas do cronograma, apontamento fácil de quantidade/%, fotos, GPS, modo offline, diário de obra, produtividade por técnico | 3, 4, 5 | Decisão de acesso externo (internet/VPN) |
| **7. Automação e indicadores** | Captura automática de extrato (CNAB/API/Open Finance), DRE gerencial, painéis de indicadores, portal do cliente | 1–6 | Contratos com bancos/agregador |

## Implantação

- Homologação: VM de testes no mesmo ESXi, para validar cada fase com os usuários.
- Produção: VM Ubuntu Server 24.04 LTS (4 vCPU, 8 GB RAM, 100 GB disco para começar),
  Docker Compose, backup diário fora da VM.
- Nenhuma implantação é feita sem autorização explícita da Worksys.

## Status

- [x] Fase 0 — em revisão (PR "Arquitetura e base do ERP")
- [ ] Fase 1
- [ ] Fase 2
- [ ] Fase 3
- [ ] Fase 4
- [ ] Fase 5
- [ ] Fase 6
- [ ] Fase 7
