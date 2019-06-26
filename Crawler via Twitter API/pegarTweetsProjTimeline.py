# -*- coding: utf-8 -*-
import re
#import urllib2
import oauth2 as oauth
#import pymongo
import json
import time
import codecs
import sys
import datetime
import pymongo

'''
__author__ = "Tiago Cruz de França"
__copyright__ = "Copyright 2018, UFRRJ"
__credits__ = ["Tiago França"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Tiago França, Edu Mangabeira"
__email__ = "tcruz.franca@gmail.com, edu.mangaba@gmail.com"
__status__ = "Test"

'''

'''
TO DO: refactor the code because each function and the class were built by demand. Now, they are all available, but some adjustment must be made. The fixes are related to integrating to use without adjustment. This version was used to get data from timelines in the project of "modeling social media timeline and their update rules".
'''
class SnapshotIdSingleton(object):

    snapshot = None
    aux = 0
    def __init__(self):
        if (self.aux == 0):
            self.__done__()
            self.__del__()

    def __del__(self):
        print("objeto destruido")

    def __done__(self):
        print ("Por favor, use o metodo instance para criar uma instancia desta classe, ela e singleton")

    def getLastSnapShotIdFromMongo(self, collection):
        register = collection.find({},{"_id":0,"snapshot_id":1}).sort("snapshot_id",pymongo.DESCENDING).limit(1)
        register = register.next()
        return register["snapshot_id"]


    @classmethod
    def instance(cls):
        if (cls.snapshot == None):
            cls.aux = 1
            cls.snapshot = SnapshotIdSingleton()
            cls.aux = 0

        return cls.snapshot


def logError(log, msg):
    log.write(msg+"\n")


def salvarArquivo(data, destino, log):
    #for registro in data:
    #print "escreveu no arquivo"
    data = json.loads(data)
    #print data
    order = 1
    for registro in data:
        try:
            #print "vaiEscreverNoArquivo"
            #print registro
            destino.write("{\"order\":"+str(order)+",\"tweet\":"+json.dumps(registro)+"}\n")
            #print "Escreveu"
            #destino.flush()
            #print "flush"
            order += 1
        except:
            msg = "Ao Salvar o Arquivo"
            logError(log, msg)
            print "Unexpected error:" + str(sys.exc_info()[0])

#Salvar somente o texto e id de um tweet
def customTweet(data, destino, ids):
    data = json.loads(data)
    cont = 0
    for row in data:
        destino.write(str(cont)+": "+json.dumps(row["text"])+'\n')
        ids.write(str(cont)+": "+json.dumps(str(row["id"]))+"\n")
        cont+=1
        #timeStamp.write(json.dumps(row["created_at"],'\n'))

def obterLastSnapshotId(collection):
    resultado = SnapshotIdSingleton.instance()
    try:
        resultado = resultado.getLastSnapShotIdFromMongo(collection)
    except:
        resultado = 0

    resultado += 1
    return resultado

'''
Adaptacao do metodo salvarArquivo para o projeto de modelagem da timeline.
A mudanca e que a cada solicitacao para salvar no arquivo eu incluo uma linha em branco, a hora UTC
'''
#def salvarTweets(data, collection, destino, log, screen_name):
def salvarTweets(data, collection, collection2, log, screen_name):

    timestamp_snapshot = datetime.datetime.utcnow().strftime("%a %b %d %H:%M:%S +0000 %Y")
    #destino.write("\n"+timestamp_snapshot+"\t"+screen_name+"\n")

    data = json.loads(data)
    order = 1
    snapShotId = obterLastSnapshotId(collection)

    for registro in data:
        try:
            print "111111111111111111111"
            #destino.write("{\"order\":"+str(order)+",\"tweet\":"+json.dumps(registro)+"}\n")
            completJSON = {'snapShotId':snapShotId, 'time_stamp':timestamp_snapshot, 'bot_screen_name':screen_name, 'impression_order':order,'tweet':json.dumps(registro)}

            print "22222222222222222222"

            adjustedJSON = {'id_tweet':registro["id"],'bot_screen_name': screen_name,'publisher_screen_name':registro["user"]["screen_name"],'snapshot_id': snapShotId,'snapshot_timestamp':timestamp_snapshot,'impression_order':order,'retweet_count':registro["retweet_count"],'favorite_count':registro["favorite_count"],'created_at_tweet':registro["created_at"],'text':registro["text"]}

            #if (screen_name != ""):
            #    adjustedJSON["bot_screen_name"] = screen_name

            collection.insert_one(adjustedJSON)
            collection2.insert_one(completJSON)
            print "3333333333333333333333"

            order += 1

        except:
            msg = "Ao Salvar o Arquivo"
            logError(log, msg)
            print "Unexpected error:" + str(sys.exc_info()[0])


#def salvarPublisherTweets(data, collection, destino, log):
def salvarPublisherTweets(data, collection, collection2, log):

    data = json.loads(data)

    for registro in data:
        try:

            #destino.write("{\"tweet\":"+json.dumps(registro)+"}\n")
            adjustedJSON = {'id_tweet':registro["id"],'publisher_screen_name':registro["user"]["screen_name"],'retweet_count':registro["retweet_count"],'favorite_count':registro["favorite_count"],'created_at_tweet':registro["created_at"]}

            collection.insert_one(adjustedJSON)
            collection2.insert_one(registro)

        except:
            msg = "Ao Salvar o Arquivo"
            logError(log, msg)
            print "Unexpected error:" + str(sys.exc_info()[0])



'''
Adaptacao do metodo customTweet para o projeto de modelagem da timeline.
A mudanca e que a cada solicitacao para salvar no arquivo eu incluo uma linha em branco, a hora UTC
'''
def customTweetAdapter(data, destino, ids,screen_name=""):

    destino.write("\n"+datetime.datetime.utcnow().strftime("%a %b %d %H:%M:%S +0000 %Y")+"\t"+screen_name+"\n")
    ids.write("\n"+datetime.datetime.utcnow().strftime("%a %b %d %H:%M:%S +0000 %Y")+"\t"+screen_name+"\n")
    customTweet(data, destino, ids)


'''
No trabalho de formacao de timeline, alem de coletar a user_home quero coletar dados de uma timeline especificada pelo usuário: coletar a timeline de duas contas que sigo?
O metodo abaixo faz isso. Preciso agora penas monitorar para pegar as mensagens mais recentes sem repetições. Melhor do que isso, so se for possivel usar usar a API de stream e pegar apenas novas publicacoes.
'''
def pegarTweetsDeUmUsuario(user, tweetTexto,destino, ids,maxTweets=1):

    if maxTweets > 200:
        maxTweets = 200
        print "A quantidade maxima de tweets é 200"
    maxId = 0

    cont = 0
    while True:
        URL = "https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name="+user+"&count="+str(maxTweets)
        if (maxId > 0):
            URL +="&max_id=" + str(maxId)
        response,data = client.request(URL,"GET")

        print "a",maxId
        maxId = (json.loads(data)[-1]['id'] - 1)
        print "b",maxId

        if (cont >= 10):
            break;
        cont += 1

        customTweet(data, tweetTexto, ids)

        salvarArquivo(data, destino,log)

'''
Este metodo e uma adaptacao da funcao pegarTweetsDeUmUsuario. A diferenca e que o que se deseja e pegar uma quantidade (max de 200) mensagens de uma timeline dado um intervalo. Esses dados sao sempre os mais
recentes na timeline ainda que sejam repetidos a cada coleta. Por exemplo, se eu pego 5 tweets mais recentes e rodo novamente em 1 minuto e apenas uma nova mensagem chegou, pegarei os 5 mais recentes (o novo
e os outros 4 que ja tinha coletado na rodada anterior.
'''
#def pegarTweetsDeUmUsuarioQtdeIntervalo(user, tweetTexto,destino, ids, collection, intervalColeta=60, maxTweets=200):
def pegarTweetsDeUmUsuarioQtdeIntervalo(user, collection, collection2, intervalColeta=60, maxTweets=200):

    '''
        @param user identifica perfil do twitter que esta sendo 'monitorado'
        @param tweetTexto e uma referencia para um arquivo. Nele sera apenas o texto do twitter.
        @param destino arquivo para salvar os tweets coletados (todo o json).
        @param ids e o arquivo para salvar os ids dos tweets.
        @param collection e a colecao para salvar os dados no mongo
        @param intervalColeta - intervalo de coleta das mensagens em segundos.
        @param maxTweets define a quantidade maxima de mensagens solicitadas a cada requisicao. Pela API o maximo sao de 200 mensagens.

    '''

    if maxTweets > 200:
        maxTweets = 200
        print "A quantidade maxima de tweets é 200"
    sinceId = 0

    cont = 0
    while True:
        URL = "https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name="+user+"&count="+str(maxTweets)
        if (sinceId > 0):
            URL +="&since_id=" + str(sinceId)

        try:

            response,data = client.request(URL,"GET")

            sinceId = (json.loads(data)[0]['id']) #sempre coletar os posteriores a um certo id

            '''
            #apenas consulta 10x a API obtendo 10x a quantidade de tweets passada (se disponivel essa qtde).
            if (cont >= 10):
                break;
            cont += 1
            '''
            #customTweetAdapter(data, tweetTexto, ids)
            #salvarPublisherTweets(data, collection, destino,log)
            salvarPublisherTweets(data, collection, collection2, log)

        except:
            print "quantidade maxima de tweets disponivel atingida. Ou seja, se vc pediu 10 e so tem 9, da erro."
        finally:
            print "finally"
            #time.sleep(intervalColeta) #dorme a cada iteracao
            time.sleep(10)


#Criado Por Eliel
def pegarTextosDeUmPerfil(user, destino, ids, maxTweets=200):


    if maxTweets > 800:
        maxTweets = 200
        print "A quantidade maxima de tweets é 200"
    maxId = 0
    maxTweets = 2

    cont = 0
    while True:
        URL = "https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name="+user+"&count="+str(maxTweets)
        if (maxId > 0):
            URL +="&max_id=" + str(maxId)
        response,data = client.request(URL,"GET")

        maxId = json.loads(data)[-1]['id']

        if (cont >= 600 ):
            break;
        cont += 1

    customTweet(data, destino, ids)

'''
Esta funcao pega da home_timeline (linha do tempo do usuario com publicações dele e de quem ele segue) Pega a quantidade especificada em maxTweets (maximo de 200) dos tweets mais recentes na timeline.
Como no trabalho nos queremos pegar repeticoes (tweets que ele ja viu, nao vou controlar se ele pega tweets que ja foram recuperados antes - que seria feito com since_id, no caso).
Na nossa pergunta seria sobre a time line "como pegar apenas as mensagens mais recentes (20 últimas publicadas)?"... resolvido a explicacao acima.
'''
def pegarTimelineAuthUser(tweetTexto,destino,ids,maxTweets=100):

    '''
        Returns a collection of the most recent Tweets and Retweets posted by the authenticating user and the users they follow. The home timeline is central to how most users interact with the Twitter service.
        Up to 800 Tweets are obtainable on the home timeline. It is more volatile for users that follow many users or follow users who Tweet frequently.

        Parameters:
           tweetTexto - file where only the tweets text will be saved.
           destino - file where the tweet json will be saved.
           ids - file where tweets ids will be saved. This is an important file because tweets ids can be saved more than 30 days and it is possible recovery old tweets by ids.
           maxTweets is used to set the number of tweets to retrieve. The default value is 20 and the maximum is 200. maxTweets and max_id are different.

        Information:
            Response formats: JSON
            Require authentication
            Rate limits: 15 to each 15 minutes

        It is possible to use others parameters. See the reference.
        Reference: https://developer.twitter.com/en/docs/tweets/timelines/api-reference/get-statuses-home_timeline
    61,

    '''

    if maxTweets > 200:
        maxTweets = 200
        print "A quantidade maxima de tweets é 200"
    maxId = 0

    cont = 0
    while True:
        URL = "https://api.twitter.com/1.1/statuses/home_timeline.json?count="+str(maxTweets)#+"&include_entities=false"#to exclude entites from json response
        if (maxId > 0):
            URL +="&max_id=" + str(maxId)
        response,data = client.request(URL,"GET")

        maxId = (json.loads(data)[-1]['id'] - 1)

        '''incluir testes do tamanho da janela'''

        if cont > 0:
            break

        cont += 1

        customTweet(data, tweetTexto, ids)

        salvarArquivo(data, destino,log)

#def pegarTimelineAuthUserProjetoTimeline(tweetTexto,destino,ids,collection, screen_name,intervalColeta=60,maxTweets=200):
def pegarTimelineAuthUserProjetoTimeline(collection, collection2, screen_name,intervalColeta=60,maxTweets=200):

    if maxTweets > 200:
        maxTweets = 200
        print "A quantidade maxima de tweets é 200"
    #maxId = 0

    #cont = 0
    while True:
        URL = "https://api.twitter.com/1.1/statuses/home_timeline.json?count="+str(maxTweets)#+"&include_entities=false"#to exclude entites from json response
        #if (maxId > 0):
        #    URL +="&max_id=" + str(sinceId)

        try: #nao precisa, mas deixei porque estava dando erro quando estava usando maxId
            response,data = client.request(URL,"GET")
            #maxId = (json.loads(data)[-1]['id']-1)#uma lista de tweets (padrao e 200 no param maxTweets) sao obtidos. Aqui pego o id do ultimo tweet da lista. Entao coleto os mais antigos, antes dele na proxima iteracao.

            '''incluir testes do tamanho da janela

            if cont > 0:
                break

            cont += 1
            '''
            #customTweetAdapter(data, tweetTexto, ids, screen_name)
            #salvarTweets(data, collection, destino, log, screen_name)
            salvarTweets(data, collection, collection2, log, screen_name)
            #contExc = 0
        except:
           print "exception"
           #contExc += 1

        finally:
            print "finally"
            time.sleep(intervalColeta)


def pegarTweets(ids, destino, log):

    listaIds = ""
    URL = "https://api.twitter.com/1.1/statuses/lookup.json?id="
    for j in ids:
        listaIds += str(j)+","

    listaIds = listaIds[:-1]#remover ultima virgula
    URL += listaIds
    #print "vaiEnviarReqisição"
    response,data = client.request(URL,"GET")

    #print "enviouRequisiçãoVaiSalvar"
    salvarArquivo(data, destino,log)
    #print "Salvou"


def coletarTweetsAntigos(arqIDs, destino, log):
    ids = []

    #arqIDs = ["577982721596723200"]

    for i in arqIDs:
        #i = i.replace("\n","")
        #i = i.replace("\r","")
        i = re.sub("[^0-9]","",i)


        ids.append(i)

            #URL = "https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name=tcruzfranca&count=1"
        if len(ids) == 100:
            try:
                print "pegaTweets"
                pegarTweets(ids,destino,log)
                print "depoisPegarTweets"
                time.sleep(5)
            except:
                msg = "Erro ao coletar."
                #logErro(log,msg)
                print "Unexpected error:"+ str(sys.exc_info()[0])
                print "dormiu"
                time.sleep(60*15)
                pegarTweets(ids,destino,log)
            finally:
                ids = []

    else:
        pegarTweets(ids,destino, log)

def getScreenNameAuthUser():

    URL = "https://api.twitter.com/1.1/account/settings.json"
    response, data = client.request(URL,"GET")

    screen_name = json.loads(data)
    screen_name = screen_name["screen_name"]
    return screen_name


def getCredentials():

    arq = open("credentials.txt")

    credentials = {}

    for i in arq:
        i = i.replace("\n","")
        i = i.replace(" ","")
        aux = i.split("=")
        key = aux[0]
        value = aux[1]

        credentials.update({key:value})

    return credentials



if __name__ == "__main__":

    '''
        dependencias: oauth2 e codecs
        Use uma das seguintes funcoes e comente a outra.
        pegarTimelineAuthUser: pegar conteudo da timeline do usuario proprietario das credenciais.
        pegarTweetsDeUmUsuario: pegar conteudo de timeline de um usuario especifico (o que ele publicou)
    '''
    #crie suas credenciais em https://apps.twitter.com/. voce precisa estar logado no twitter com uma conta (tem que ter fornecido um numero de celular que sera validado por eles).

    credenciais = getCredentials()

    Consumer_key = credenciais['Consumer_key']
    Consumer_secret = credenciais['Consumer_secret']
    Access_token = credenciais['Access_token']
    Access_token_secret = credenciais['Access_token_secret']

    consumer = oauth.Consumer(key=Consumer_key, secret=Consumer_secret)
    access_token = oauth.Token(key=Access_token, secret=Access_token_secret)
    client = oauth.Client(consumer, access_token)


    arquivo = raw_input("Forneca o nome do banco onde serao salvos os dados da coleta:")
    #print ("Esse mesmo nome tambem sera usado para salvar todos os dados em um arquivo.")

    #substitua os nomes dos arquivos
    #salvarTweet = arquivo+".txt"
    #salvarApenasIdsTweets = arquivo+"_ids.txt"
    #salvarApenasTextoTweets = arquivo+"_texto.txt"
    salvarLogErros = arquivo+"_log.txt"

    #destino = codecs.open(salvarTweet, "a", "utf-8")
    #tweets_ids = codecs.open(salvarApenasIdsTweets, "a", "utf-8")
    #tweets_texto= codecs.open(salvarApenasTextoTweets, "a", "utf-8")
    log = open(salvarLogErros,"a")

    mongo = pymongo.MongoClient()
    db = mongo[arquivo]

    #print ("Os arquivos:"+salvarTweet+','+salvarApenasIdsTweets+','+salvarApenasTextoTweets+','+salvarLogErros+" foram criados")

    try:
        intervaloColeta = input("Qual o intervalo de coleta (em segundos)? (default 1500s)") #3600
        qtdeTweetsPorRequisicao = input("Qual a quantidade de tweets deseja por requisicao (min = 1 e max = 200)?") #30
    except:
        intervaloColeta = 3600
        qtdeTweetsPorRequisicao = 30

    resp = raw_input("Deseja coletar da timeline do usuario dono das credenciais fornecidas? (S-sim, n-nao)")

    if (resp != 'n'):
        screen_name = getScreenNameAuthUser()
        collection = db[screen_name]
        collection2 = db[screen_name+"_completeJSON"]
        #collection.find_one()
        #screen_name is the name of the logged user
        #pegarTimelineAuthUserProjetoTimeline(tweets_texto, destino, tweets_ids, collection, screen_name, intervaloColeta, qtdeTweetsPorRequisicao)
        pegarTimelineAuthUserProjetoTimeline(collection, collection2, screen_name, intervaloColeta, qtdeTweetsPorRequisicao)
    else:
        userName = raw_input("Qual nome do usuario que voce deseja coletar dados da timeline (sem '@') ?")
        userName = userName.replace("@","")
        collection = db[userName]
        collection2 = db[userName+"_completeJSON"]
        #pegarTweetsDeUmUsuarioQtdeIntervalo(userName, tweets_texto,destino,tweets_ids, collection, intervaloColeta,qtdeTweetsPorRequisicao)
        pegarTweetsDeUmUsuarioQtdeIntervalo(userName, collection, collection2, intervaloColeta,qtdeTweetsPorRequisicao)

    print("A coleta esta sendo realizada. Sente, tome um cafe e trabalhe em outra coisa. Ou coloque outra coleta pra rodar, caso deseje. =D")
    #coletarTweetsAntigos(arq, destino,log)#coleta por ids que estao no arquivo idsTweets


    destino.close()
    tweets_texto.close()
    log.close()
