# Evidências a capturar no seu computador

Não coloque capturas fictícias. Salve prints reais nesta pasta:

1. `01-versoes.png`: `sam --version`, `python --version`, `docker --version`.
2. `02-invocacao-1.png` e `03-invocacao-2.png`: duas execuções de `sam local invoke -e events/pedido.json` com tempos registrados.
3. `04-http.png`: três chamadas HTTP via curl, mostrando a resposta.
4. `05-warm.png`: repetir com `sam local start-api --warm-containers LAZY` e comparar o contador.
5. `06-timeout-3s.png`: erro ao enviar `demorar: true` com Timeout 3.
6. `07-timeout-10s.png`: após editar Timeout para 10 e `sam build`, resposta de sucesso.

Anote os tempos e as diferenças reais no README. Não use números inventados.
