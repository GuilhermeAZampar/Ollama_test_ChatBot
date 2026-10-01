import json
from email.header import UTF8
from shlex import join

import ollama


#aqui e como o sistema deve se comportar
messages=[{
    "role":"system",
    "content":"Voce é um professor de programação, responda de forma didatica ,curta e simples sempre"
}]


with open("memoria.json","r",encoding="UTF-8") as arquivo:
    memoria=json.load(arquivo)


while True:
    pergunta = input("Voce: ")
    if pergunta.lower() =="sair":
        break

    analisador=ollama.chat(
        model="llama3.2:3b",
        messages=[{
            "role":"system",
            "content":"""Você é um classificador de memória.

                Escolha uma das três ações:

                guardar:
                Quando a mensagem informar um novo fato pessoal, preferência,
                gosto, objetivo ou característica do usuário que ainda não esteja
                nas memórias.
                
                ignorar:
                Quando a mensagem for apenas uma pergunta, pedido, cálculo
                ou informação que não descreva o usuário.
                
                atualizar:
                Quando a mensagem alterar ou substituir uma informação
                que já existe nas memórias do usuário.
                
                
                Quando a ação for "atualizar", retorne em "memoria_antiga"
                exatamente a memória existente que deve ser substituída.
                
                Quando a ação for "guardar" ou "ignorar",
                retorne "memoria_antiga" como uma string vazia.
                                
                Exemplos:
                "Meu cachorro se chama Sipi" -> guardar
                "Minha comida favorita é pizza" -> guardar
                "Quanto é 10 + 5?" -> ignorar
                "O que é Python?" -> ignorar
                "Minha banda favorita agora é Rammstein" -> atualizar
                
                Exemplo de atualização:

                Memórias atuais:
                Minha banda favorita é Metallica
                
                Mensagem:
                Minha banda favorita é Megadeth
                
                Resultado:
                acao = atualizar
                memoria_antiga = Minha banda favorita é Metallica
                
                
                Exemplo de nova memória:
                
                Memórias atuais:
                Meu cachorro se chama Sipi
                
                Mensagem:
                Minha comida favorita é pizza
                
                Resultado:
                acao = guardar
                memoria_antiga = ""
                
                IMPORTANTE:
                Se a ação for atualizar, "memoria_antiga" deve ser uma cópia EXATA
                de uma das memórias fornecidas em "Memórias atuais".
                Não invente outro formato e não reformule o texto.
                
                Exemplo de pergunta:
                
                Mensagem:
                Qual é minha banda favorita?
                
                Resultado:
                acao = ignorar
                memoria_antiga = ""
                
                Não responda à mensagem do usuário. Apenas classifique."""

        },
            {
                "role":"system",
                "content":"Memória ja salvas do usúario \n" + "\n".join(memoria)

            },
            {
                "role": "user",
                "content": pergunta
            }
        ],
        options={
            "temperature":0
        },
        format={
            "type":"object",
            "properties":{
                "acao":{
                    "type":"string",
                    "enum":["guardar","ignorar","atualizar"]
                },
                "memoria_antiga":{
                    "type":"string"
                }
            },
            "required": ["acao","memoria_antiga"]
        }

    )

    resultado=analisador["message"]["content"]
    dados=json.loads(resultado)
    print("Resultado Bruto:",resultado)
    print("Dados",dados)
    if dados["acao"]=="guardar":
        memoria.append(pergunta)
        with open("memoria.json","w",encoding="UTF-8") as arquivo:
            json.dump(memoria,arquivo,ensure_ascii=False,indent=4)
    elif dados["acao"]=="atualizar":
        for i , item in enumerate(memoria):
            if item.lower()==dados["memoria_antiga"].lower():
                memoria[i] = pergunta
                with open("memoria.json", "w", encoding="UTF-8") as arquivo:
                    json.dump(memoria, arquivo, ensure_ascii=False, indent=4)


    #print("DEBUG memoria",memoria)
    #print("DEBUG dados",dados)

    memoria_msg = {
        "role": "system",
        "content": "Informaçoes importante \n" + "\n".join(memoria)
    }

    #aqui o sistema recebe do user a pergunta
    messages.append({
        "role": "user",
        "content": pergunta
    })

    historico=messages[1:]
    contexto=[messages[0]]+[memoria_msg]+historico[-6:]
    #Envia contexto a llm e gera a resposta
    resposta = ollama.chat(
        model="llama3.2:3b",
        messages=contexto,
        options={
            "temperature":0.2,
            "num_predict":300
        },
        stream=True
    )
    resposta_completa=""
    print("IA: ", end="")
    for partes in resposta:
        print(partes["message"]["content"], end="")
        resposta_completa+=partes["message"]["content"]
    print()

    #aqui devolve a resposta completa
    messages.append({
        "role": "assistant",
        "content": resposta_completa
    })



     #print("IA resposta: ",resposta["message"]["content"])

