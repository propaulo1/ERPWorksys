"""Módulos do ERP exibidos no menu e no painel, na ordem do roadmap.

url_name None indica módulo ainda não entregue (aparece como "em breve").
"""

MODULOS = [
    {"chave": "financeiro", "nome": "Financeiro", "icone": "cifrao", "fase": 1,
     "descricao": "Contas a pagar e receber, conciliação Itaú/Bradesco e fluxo de caixa.", "url_name": None},
    {"chave": "crm", "nome": "CRM", "icone": "pessoas", "fase": 2,
     "descricao": "Contatos comerciais, oportunidades e follow-ups.", "url_name": None},
    {"chave": "propostas", "nome": "Propostas", "icone": "documento", "fase": 2,
     "descricao": "Pré-vendas: propostas, revisões e composição de custo.", "url_name": None},
    {"chave": "projetos", "nome": "Projetos", "icone": "cronograma", "fase": 3,
     "descricao": "Engenharia: cronograma, medições e acompanhamento de obra.", "url_name": None},
    {"chave": "estoque", "nome": "Estoque", "icone": "caixa", "fase": 4,
     "descricao": "Materiais, ferramentas e EPI individual e coletivo.", "url_name": None},
    {"chave": "suporte", "nome": "Suporte", "icone": "fone", "fase": 5,
     "descricao": "Chamados de clientes e ordens de serviço de manutenção.", "url_name": None},
    {"chave": "campo", "nome": "Campo", "icone": "capacete", "fase": 6,
     "descricao": "App do técnico: diário de obra, apontamentos e produtividade.", "url_name": None},
]
