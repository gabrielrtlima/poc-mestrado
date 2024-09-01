import requests
import json

LLM_URL = "http://localhost:11434/api/generate"


def generate_function_info(function_code, function_name, params, return_type):
    prompt = f"""
    Analise a seguinte função Python e forneça uma descrição concisa e um exemplo de uso:

    Função: {function_name}
    Parâmetros: {json.dumps(params, indent=2)}
    Tipo de retorno: {return_type}

    Código:
    {function_code}

    Por favor, forneça:
    1. Uma descrição do propósito da função, o que ela faz e como ela funciona em no máximo 3 frases.
    2. Um exemplo conciso de como a função seria chamada/executada, incluindo valores de exemplo para os parâmetros e, se aplicável, como usar o valor retornado.

    Formate sua resposta e siga, sem exceção este modelo: 
    Descrição: [Sua descrição aqui]
    Exemplo de uso: [Seu exemplo aqui]


    Não é necessário adicionar mais informações além do que foi pedido apenas a descrição e o exemplo de uso, também não é necessário após a descrição: e o exemplo de uso: repetir novamente dizendo que é uma descrição ou exemplo de uso
    """

    payload = {"model": "llama3.1", "prompt": prompt, "stream": False}

    try:
        response = requests.post(LLM_URL, json=payload)
        response.raise_for_status()
        result = response.json()
        response_text = result["response"].strip()

        # Separar a descrição e o exemplo de uso
        description = (
            response_text.split("Exemplo de uso:")[0].replace("Descrição:", "").strip()
        )
        example = (
            response_text.split("Exemplo de uso:")[1].strip()
            if "Exemplo de uso:" in response_text
            else ""
        )

        return description, example
    except requests.RequestException as e:
        print(f"Erro ao chamar o LLM: {e}")
        return None, None
