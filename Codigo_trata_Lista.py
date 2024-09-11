import pandas as pd
import emoji
import re
import time
import sys

# Configuração para exibir todas as linhas
pd.set_option('display.max_rows', None)

telefonesSemConformidade =[["telefone","nome","razão"]]
ddds = []


def formatarTelefone (telefone, nome):
    #print(telefone,nome)
    try:
        if isinstance(telefone, float):
            telefone = int(telefone)
        if type(telefone) == str:
            if 'href' in telefone:
                telefone = re.sub('<[^>]+?>', '', telefone)
        #if  " - IH" in nome or  " - CORTESIA"in nome or " - BL"in nome:
         #   telefonesSemConformidade.append([telefone,nome,"contem as tag da deli"])
          #  return None

        telefone = str(telefone)
        telefone = telefone.replace('(','').replace(')','').replace('-','').replace(' ','').replace('+','').replace('.','')
        if telefone[0] == '0':
            telefone = telefone [1:]
        #print(telefone)
        if telefone == '' or telefone == None:
            return None
            telefonesSemConformidade.append([telefone,nome,"telefone vazio"])

        if len(telefone) < 10:
            telefonesSemConformidade.append([telefone,nome,"menos que 10 digitos"])
            #print("telefone sem conformidade sera excluido: %s, \npertence ao contato %s"%telefone%nome)
            return None
        elif len(telefone) >13:
                telefone = telefone.split('\n')[0]
                if  len(telefone) >13:
                    telefonesSemConformidade.append([telefone,nome,"mais de 13 digitos"])
                    return None
 

        if len(telefone) < 12:
            ddd = telefone[:2]
        else:
            ddd = telefone[2:4]
        ultimosDigitos = telefone[-8:]

        if len(ddds)>0:
            if (int(ddd) not in ddds):
                #print(int(ddd) not in ddds, ddd,ddds)
                telefonesSemConformidade.append([telefone,nome,"DDD que não ta nos DDD's informados"])
                return None

                
        
        if (int(ddd)<29):
            ultimosDigitos = "9" + ultimosDigitos
        telefone = "55"+ddd+ultimosDigitos
        #print(ddd)
        #print(telefone)

        return telefone
        #print(telefone,nome)

    except Exception as e:
        print("erro ao tentar tratar numero: ",telefone, "do contato: ", nome,"\n",e,"\n\n")
        telefonesSemConformidade.append([telefone,nome,str(e)])
        return None
    

def removerRepetidos(arq):
    #arq = arq.sort_values(by='telefone', na_position='last')
    telefones_duplicados = arq[arq.duplicated(['telefone'], keep=False)]
    print('\n\nIniciando tratamento para remover duplicados')
    if not telefones_duplicados.empty:
        print("temos um total de ", len(telefones_duplicados))
        arq = arq.drop_duplicates(subset='telefone', keep='first')
        print('Tratamento concluído.\nlista de contatos duplicados\n')
        pd.set_option('display.max_rows', None)
        
        print(telefones_duplicados)
    else:
        print('Nenhum telefone duplicado encontrado.')
    

    return arq, telefones_duplicados

def adicionarTags(arq, removeEtiqueta, adicionaAquecimento, tipo, tamanhoDoGrupo):
    #reset index para não dar outOfBound quando for tagear a lista depois que remover os telefones repetidos/duplicados
    arq.reset_index(drop=True, inplace=True)
    #tipo = tipo.replace(' ','_')
    if removeEtiqueta:
        arq = arq.drop(['etiquetas'], axis=1)

    if adicionaAquecimento:
        # Lista de tuplas com a tag e o número de linhas para essa tag
        tags_aqc = [
            ('aqc_01', 30),
            ('aqc_02', 30),
            ('aqc_03', 50),
            ('aqc_04', 50),
            ('aqc_05', 70),
            ('aqc_06', 70),
            ('aqc_07', 100),
            ('aqc_08', 100),
            ('aqc_09', 150),
            ('aqc_10', 150),
            ('aqc_11', 200),
            ('aqc_12', 200)
        ]
        # Adicionando as tags 'aqc_01', 'aqc_02', etc.
        inicio = 0
        for tag, linhas in tags_aqc:
            arq.loc[inicio:inicio+linhas-1, 'etiquetas'] =  tag
            inicio += linhas
    # Adicionando as tags 'G1_leads', 'G2_leads', etc.
    inicio = 0
    grupo = 1
    while inicio < len(arq):
        
        fim = min(inicio+tamanhoDoGrupo-1, len(arq)-1)
        
        if not adicionaAquecimento: 
            arq.loc[inicio:fim, 'etiquetas'] =f'G{grupo}_{tipo}'

        else:    
            if pd.isna(arq.loc[inicio, 'etiquetas']):
                arq.loc[inicio:fim, 'etiquetas'] =f'G{grupo}_{tipo}'
            else:
                arq.loc[inicio:fim, 'etiquetas'] = arq.loc[inicio:fim, 'etiquetas'] + f', G{grupo}_{tipo}'
        inicio += tamanhoDoGrupo
        grupo += 1
    return arq

def removerTelefonesExistentes(arq, arqLead):
    # Encontra os telefones em arqLead que estão presentes em arq
    mask = arqLead['telefone'].isin(arq['telefone'])
    # Mantém apenas os telefones em arqLead que não estão em arq
    arqLead = arqLead[~mask]
    return arqLead



def remove_emoji(text):
    text = text.replace('Nan', '').replace('nan','')
    if not isinstance(text, str):  # Check if the input is not a string
        return text  # Return the input as is if it's not a string

    if text is None:
        return None
    emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                           u"\U0001F700-\U0001F77F"  # alchemical symbols
                           u"\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
                           u"\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
                           u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
                           u"\U0001FA00-\U0001FA6F"  # Chess Symbols
                           u"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
                           u"\U00002702-\U000027B0"  # Dingbats
                           u"\U000024C2-\U0001F251" 
                           "]+", flags=re.UNICODE)

    return emoji_pattern.sub(r'', text).title()


    

#tratar clientes
local = input("digite onde se encontra o arquivo ex: 'C:\\Users\\Felipe Arnauld\\Downloads': ->")
local.replace("\\","/")
arquivo = input("agora o nome do arquivo que deseja tratar ex: lista Cliente.xlsx ->")
try:
    arq = pd.read_excel(local+"/"+arquivo)
    
except FileNotFoundError as error:
    print("erro ao abrir o arquivo\npor favor certifique-se de que a pasta existe e o arquivo esta na extensão .xlsx\n",error)
    sys.exit()
    
print("arquivo encontrado com sucesso")
print("vou colocar na tela as colunas para definir qual vai ser a coluna nome e a coluna telefone")

#arq.style
#print(arq)
print(arq.columns.values)


nome = input("qual coluna é a coluna nome? certifique-se de copiar o nome exatamente como esta escrito")
arq['nome'] = arq[nome].astype(str)
combineNome = input("tem sobme ou segundo nome ? Y ou N")
if combineNome.lower() == 'y':
    combineNome = 'True'
else:
    combineNome = 'False'

if eval(combineNome):
    nome2 = input("digite qual a coluna sobrenome (nome sera os dois nomes juntos)")
    arq['nome'] = arq['nome'] + " " + arq[nome2].astype(str)

    
separaDDD = input("deseja separar por algum DDD? Y ou N")
if separaDDD.lower() == 'y':
    separaDDD = 'True'
else:
    separaDDD = 'False'
while eval(separaDDD):
    ddd = input("digite o DDD que deseja filtrar")
    ddds.append(int(ddd))
    separaDDD = input("mais algum DDD? Y ou N")
    if separaDDD.lower() == 'y':
        separaDDD = 'True'
    else:
        separaDDD = 'False'

telefone = input("qual coluna é  telefone?")
arq['telefone'] = arq[telefone]
arq['telefone'] = arq.apply(lambda row: formatarTelefone(row['telefone'], row['nome']), axis=1)
#arq.to_excel(local+"/"+"depois do primeiro telefone "+arquivo, index=False)

#print (arq[['nome', 'telefone','Telefone 1', 'Telefone 2']])
combineTelefone = input("teria alguma coluna extra de telefone? Y ou N")
if combineTelefone.lower() == 'y':
    combineTelefone = 'True'
else:
    combineTelefone = 'False'

while eval(combineTelefone):
    tel2 = input("digite qual a coluna de telefone extra (caso haja os dois sera considerado o 1°)")
    arq[tel2] = arq.apply(lambda row: formatarTelefone(row[tel2], row['nome']), axis=1)
    #arq.to_excel(local+"/"+"depois do segundo telefone "+arquivo, index=False)
    arq['telefone'] = arq['telefone'].combine_first(arq[tel2])
    #arq.to_excel(local+"/"+"depois de juntar "+arquivo, index=False)
    #arq['telefone'] = arq.apply(lambda row: formatarTelefone(row['telefone'], row['nome']), axis=1)
    #arq.to_excel(local+"/"+"depois do segundo telefone "+arquivo, index=False)

    combineTelefone = input("teria alguma coluna extra de telefone? Y ou N")
    if combineTelefone.lower() == 'y':
        combineTelefone = 'True'
    else:
        combineTelefone = 'False'


#print (arq[['nome', 'telefone','Telefone 1', 'Telefone 2']])


separar = input("deseja separar por alguma coluna? Y ou N")
if separar.lower() == 'y':
    separar = 'True'
else:
    separar = 'False'

while eval(separar):
    print("qual coluna deseja separar?\n", arq.columns)
    coluna = input("coluna: ")
    pd.set_option('display.max_rows', None)
    print("esses são os valores da coluna:\n",arq[coluna].value_counts())
    pd.set_option('display.max_rows', 10)
    valor = input("agora digite o valor que deseja pegar")
    arq = arq[arq[coluna] == valor]
    print("o arquivo se encontra assim no momento\n",arq)
    arquivo =  valor +" - "+ arquivo
    #print(arquivo)
    separar = input("tem mais alguma coluna que deseja separar? Y ou N")
    if separar.lower() == 'y':
        separar = 'True'
    else:
        separar = 'False'

    



arq = arq[['nome', 'telefone']]
arq.dropna(subset=['telefone'], inplace=True)
pd.set_option('display.max_rows', 10)

display(arq)


arq.dropna(subset=['telefone'], inplace=True)
arq, telefones_duplicados = removerRepetidos(arq)

arq['nome'] = arq['nome'].apply(remove_emoji)

# adicionarTags(arquivo, removeEtiqueta, adicionaAquecimento, tipo, tamanhoDoGrupo):
tag = input("digite o que vc deseja na tag: ")

print(f"\n\n(tamanho da lista sem repretição: {len(arq)})")
print(f"sugiro grupos de {round((len(arq)/5)+0.5)}  para ter 1 disparo de seg-sex")
print(f"ou então grupos de {round((len(arq)/6)+0.5)} para ter disparo sábado também")

tamanho = input(f"digite o tamanho dos grupos")
aqc = input("deseja aquecer o numero? Y ou N")
if aqc.lower() == 'y':
    aqc = 'True'
else:
    aqc = 'False'

arq = adicionarTags(arq, False, eval(aqc), tag.lower(), int(tamanho))


# Salvar o DataFrame modificado em um novo arquivo Excel
pd.set_option('display.max_rows', 30)
arq.to_excel(local+"/"+"[tratada] "+arquivo.replace('/','_'), index=False)

print("fim do tratamento, da lista\nfoi salvado arquivo com nome [tratada]",arquivo," \nna pasta de origem")
time.sleep(2)
if len(telefonesSemConformidade) > 1:
    print("telefones sem conformidade encontrados:\n")
    for telefone in telefonesSemConformidade:
        print(telefone)
else:
    print("não foram encontrados telefones sem conformidade")
time.sleep(3)
display(arq)