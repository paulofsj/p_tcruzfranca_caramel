# -*- coding: utf-8 -*-
import tweepy
import pymongo
import json
import sys
import time


class StdOutListener(tweepy.StreamListener):

    def __init__(self):
        self.logFile = ""
        self.collection = ""
        self.backOff = None

    def setLogFile(self, arq):
        self.logFile = arq

    def closeLogFile(self):
        if ((self.logFile is not None) and (self.logFile != "")):
            self.logFile.close()

    def setCollection(self, collection):
        self.collection = collection

    def setTimerBackOffToStream(self, backOff):
        self.backOff = backOff

    def on_data(self, data):
        if(self.collection == ""):
            print("Error: use setCollection para definir uma colecao no mongo")
            return

        data = json.loads(data)
        self.collection.insert(data)
        self.backOff.reiniciarContadorTentativas()

    def on_error(self, status):
        self.logFile.write("\n\nerror:" + str(status))
        self.backOff.timeReconexao(status)


class TimerBackOffToStream(object):

    def __init__(self):
        self.tentativas = 1  # fator de multiplicacao

    def timeReconexao(self, HTTPerror=0):
        '''
            Avoiding to block the user's IP or credentials.
        '''
        if (HTTPerror == 420):
            time.sleep(60 * self.tentativas)
        elif (self.tentativas == 1):
            time.sleep(5)
        else:
            time.sleep(5 * self.tentativas * 2)
        self.tentativas += 1

    def setTentativas(self, incrementar):
        self.tentativas += incrementar

    def reiniciarContadorTentativas(self):
        self.tentativas = 1


if __name__ == '__main__':

    # parametros de autenticacao
    Consumer_key = ""
    Consumer_secret = ""
    Access_token = ""
    Access_token_secret = ""

    backOff = TimerBackOffToStream()
    arqLog = open("log.txt", "a")

    while (True):
        try:
            # This handles Twitter authetification and the connection to Twitter Streaming API
            listen = StdOutListener()

            # Definindo banco e collection no mongo onde serao salvos os dados
            mongo = pymongo.MongoClient()
            db = mongo['']  # inserir nome do banco aqui
            collection = db['']  # inserir nome da coleção aqui

            listen.setCollection(collection)
            listen.setLogFile(arqLog)
            listen.setTimerBackOffToStream(backOff)

            auth = tweepy.OAuthHandler(Consumer_key, Consumer_secret)
            auth.set_access_token(Access_token, Access_token_secret)
            stream = tweepy.Stream(auth, listen)

            termos = ['']  # inserir termos aqui, podem ser inclusive hashtags

            # This line filter Twitter Streams to capture data by the hashtags
            stream.filter(track=termos)

        except:
            print("except")
            arqLog.write("\nError: Exception:" + str(sys.exc_info()[0]))
            backOff.timeReconexao()
