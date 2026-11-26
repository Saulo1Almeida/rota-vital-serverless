# Roteiro sugerido (até 3 minutos)

**0:00–0:25** — Apresentar o repositório, `template.yaml`, `hello_world/app.py` e explicar que o SAM simula o Lambda localmente.

**0:25–1:00** — Mostrar `sam build` e duas invocações `sam local invoke -e events/pedido.json`, indicando tempos reais.

**1:00–1:40** — Mostrar `sam local start-api` e executar `curl` em outro terminal. Exibir o JSON com guia, hospital, bolsas e contador.

**1:40–2:15** — Mostrar diferença com `--warm-containers LAZY` e explicar por que o contador global não garante persistência.

**2:15–2:45** — Mostrar o erro de timeout com 3 segundos e o sucesso após alterar para 10 segundos e recompilar.

**2:45–3:00** — Mostrar `evidencias/`, README, seção Uso de IA e encerrar.

Grave sua própria tela com resultados reais; este arquivo é apenas o roteiro.
