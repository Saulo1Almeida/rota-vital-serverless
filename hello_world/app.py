import json
import time

contador = 0  # Não é armazenamento persistente.


def lambda_handler(event, context):
    global contador
    contador += 1

    try:
        pedido = json.loads(event.get('body') or '{}')
    except (json.JSONDecodeError, TypeError):
        return {'statusCode': 400, 'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'erro': 'JSON inválido'}, ensure_ascii=False)}

    if not isinstance(pedido, dict) or not pedido.get('requisicaoId'):
        return {'statusCode': 400, 'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'erro': 'requisicaoId obrigatório'}, ensure_ascii=False)}

    if pedido.get('demorar'):
        time.sleep(5)  # Teste do timeout de 3 segundos.

    guia = {
        'guia': 'G-' + str(pedido['requisicaoId']),
        'hospital': pedido.get('hospital'),
        'bolsas': pedido.get('bolsas', []),
        'invocacaoNesteAmbiente': contador,
    }
    return {'statusCode': 201, 'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(guia, ensure_ascii=False)}
