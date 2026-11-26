# Rota Vital — Serverless

Atividade individual de Infraestrutura de Software — ADS, CESAR School.

## Objetivo

Simular a geração de guias de transporte de bolsas de sangue com AWS Lambda e API Gateway, utilizando AWS SAM localmente. O experimento demonstra invocações por evento e HTTP, inicialização e reutilização de ambientes, timeout e custos de execução serverless.

## Como executar

Pré-requisitos: Python 3.12, Docker em execução e AWS SAM CLI. Os comandos abaixo foram testados no CMD do Windows 10, na raiz do projeto.

```cmd
sam build
sam local invoke -e events/pedido.json
sam local invoke -e events/pedido.json
```

A função está em `hello_world/app.py`, o evento em `events/pedido.json` e a configuração em `template.yaml`. A função `GuiaTransporteFunction` utiliza Python 3.12 e 128 MB de memória.

Para iniciar a API:

```cmd
sam local start-api
```

Em outro CMD, execute três vezes:

```cmd
curl -X POST http://127.0.0.1:3000/guias -H "Content-Type: application/json" -d "{\"requisicaoId\":\"R-002\",\"hospital\":\"H-Caruaru\"}"
```

A rota é `POST /guias`. A função retorna a guia, hospital, bolsas e o contador `invocacaoNesteAmbiente`. Para testar o reaproveitamento, encerre o servidor com Ctrl+C e inicie novamente:

```cmd
sam local start-api --warm-containers LAZY
```

Repita as três requisições anteriores.

## Resultados dos experimentos

### Invocações por evento

| Invocação | Init Duration | Duration | Billed Duration | Contador |
|---|---:|---:|---:|---:|
| Primeira | 0,06 ms | 69,01 ms | 70 ms | 1 |
| Segunda | 0,04 ms | 209,24 ms | 210 ms | 1 |

Ambas retornaram status 201, guia G-R-001, hospital H-Recife e bolsa O-NEG-0142. Os identificadores dos containers eram diferentes.

### Invocações HTTP

| Chamada | Sem warm: duração | Sem warm: contador | Com warm: duração | Com warm: contador |
|---|---:|---:|---:|---:|
| 1 | 59,30 ms | 1 | 60,14 ms | 1 |
| 2 | 56,92 ms | 1 | 2,64 ms | 2 |
| 3 | 57,27 ms | 1 | 1,41 ms | 3 |

Todas retornaram HTTP 201 e guia G-R-002. Com warm containers, a terceira chamada apresentou redução de aproximadamente 97,54% na duração em comparação com a terceira chamada sem warm containers.

### Timeout

A configuração final do projeto utiliza `Timeout: 10`. Para reproduzir a falha, encerre o servidor, altere temporariamente o timeout em `template.yaml` para 3, execute `sam build` e reinicie a API. Em outro CMD, execute:

```cmd
curl -i -X POST http://127.0.0.1:3000/guias -H "Content-Type: application/json" -d "{\"requisicaoId\":\"R-003\",\"demorar\":true}"
```

A função espera cinco segundos quando recebe `demorar: true`. Após observar a falha, encerre o servidor, restaure `Timeout: 10`, execute `sam build`, reinicie a API e repita a requisição.

| Timeout | Duration | Billed Duration | HTTP |
|---|---:|---:|---|
| 3 s | 3000,00 ms | 3000 ms | 502 Bad Gateway |
| 10 s | 5060,30 ms | 5061 ms | 201 Created |

No primeiro teste, o log informou `Function 'GuiaTransporteFunction' timed out after 3 seconds`. No segundo, a guia G-R-003 foi gerada normalmente. O hospital retornou null e as bolsas retornaram uma lista vazia porque esses campos não foram enviados.

## Respostas teóricas

### 1. Por que a primeira invocação pode ser mais lenta? O que é Init Duration?

Quando não existe um ambiente disponível, a Lambda precisa inicializar o runtime e carregar o código e suas dependências antes de executar o handler. Esse processo é chamado de cold start. Init Duration representa o tempo da fase de inicialização reportado pelo ambiente, não necessariamente todo o tempo de preparação do Docker ou da requisição. No teste por evento, a primeira chamada precisou preparar a imagem local, enquanto a segunda utilizou a imagem em cache. Apesar disso, a Duration da segunda foi maior (209,24 ms contra 69,01 ms). As duas chamadas usaram containers diferentes, portanto a segunda não foi uma warm invocation. Já no teste HTTP com reaproveitamento, as chamadas seguintes tiveram duração de 2,64 ms e 1,41 ms, sem uma nova Init Duration reportada.

### 2. O que aconteceu com o contador global?

Sem warm containers, o contador retornou 1 nas três chamadas porque cada execução ocorreu em um novo ambiente. Com `--warm-containers LAZY`, retornou 1, 2 e 3, pois o mesmo ambiente foi reutilizado e a variável global permaneceu em memória. Na AWS, esse reaproveitamento não é garantido: novos ambientes podem ser criados a qualquer momento. Por isso, dados importantes devem ser armazenados externamente, por exemplo no DynamoDB, e não em variáveis globais.

### 3. O que acontece quando a função ultrapassa o timeout? Qual é o limite da Lambda?

A execução é interrompida quando ultrapassa o limite configurado. No experimento local, o timeout de 3 segundos gerou HTTP 502, pois a função não conseguiu concluir a espera de cinco segundos. Com o limite de 10 segundos, retornou HTTP 201. O limite máximo de execução de uma função AWS Lambda é 900 segundos (15 minutos). Processamentos maiores podem ser divididos em etapas menores, orquestrados com AWS Step Functions ou executados em serviços como ECS/Fargate, conforme a necessidade.

### 4. Quanto custa um milhão de invocações com 128 MB e duração de 100 ms?

Considerando os valores de US$ 0,20 por milhão de requisições e US$ 0,0000166667 por GB-segundo:

- Memória: 128 / 1024 = 0,125 GB.
- Duração: 100 ms = 0,1 segundo.
- Consumo: 1.000.000 × 0,125 × 0,1 = 12.500 GB-segundos.
- Custo de execução: 12.500 × 0,0000166667 = US$ 0,20833375.
- Custo das requisições: US$ 0,20.
- Total: aproximadamente **US$ 0,41**.

O cálculo desconsidera a camada gratuita, impostos e custos de serviços adicionais, como API Gateway. Se houver franquia gratuita suficiente disponível, o custo da Lambda nesse cenário pode ser zero.

### 5. Onde a arquitetura serverless se encaixa na Rota Vital e onde não se encaixa?

A Lambda é adequada para gerar guias de transporte, validar requisições, processar eventos e disparar notificações, pois essas tarefas são curtas e podem ocorrer sob demanda. Isso reduz a necessidade de manter servidores ativos continuamente. Não é a melhor opção para tarefas que precisam permanecer em execução por longos períodos, manter conexões contínuas ou guardar estado exclusivamente em memória. O rastreamento contínuo e o armazenamento confiável das informações de transporte precisam de serviços apropriados, como serviços de mensageria, bancos de dados ou containers, dependendo dos requisitos. A função demonstrada é um protótipo local, não um sistema hospitalar pronto para produção.

## Evidências

- [Build](evidencias/01-build.png)
- [Primeira invocação](evidencias/02-primeira-invocacao.png)
- [Segunda invocação](evidencias/03-segunda-invocacao.png)
- [HTTP sem warm containers](evidencias/04-http-sem-warm.png)
- [HTTP com warm containers](evidencias/05-http-com-warm.png)
- [Erro de timeout](evidencias/06-timeout-erro.png)
- [Timeout corrigido](evidencias/07-timeout-corrigido.png)

## Uso de IA

Utilizei o ChatGPT para gerar o código inicial do projeto, auxiliar na configuração do AWS SAM e do Docker, orientar os comandos e experimentos, interpretar os logs e elaborar a documentação e as respostas teóricas. Executei os comandos localmente, conferi os retornos HTTP, os contadores e os tempos registrados pelo SAM, alterei o timeout e capturei as evidências. Os resultados experimentais apresentados neste README foram obtidos nessas execuções locais.
