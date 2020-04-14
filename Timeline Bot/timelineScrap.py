#    'snapshot_id': snapShotId,'snapshot_timestamp':timestamp_snapshot,'impression_order':order,

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from Tweet import Tweet
import json
import time
import re
import pymongo
import datetime

__author__ = "Tiago Cruz de França"
__copyright__ = "Copyright 2018, UFRRJ"
__credits__ = ["Tiago França"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Tiago França, Edu Mangabeira"
__email__ = "tcruz.franca@gmail.com"
__status__ = "Test"

'''
TO DO list:
Se o usuario passar um tempo sem fazer login, o Twitter monta a pagina de um jeito diferente 
destacando tweets que tenham alguma importancia (de acordo com algoritmo da midia) para o usuario. 
Ou seja, o HTML da pagina fica diferente. Uma abordagem seria detectar periodos longos sem coletar 
(quando o bot ficar fora por falta de energia, por exemplo), matar o processo e rodar novamente. 
Partimos do pre-suposto de que o usuario vê continuamente sua timeline.
'''
def extraindoApenasTexto(tweet_texto):
    
    texto = re.sub('<[^>]*>'," ",tweet_texto)
    texto = re.sub('\s+',' ',texto)
    texto = texto.strip()
    return texto

def getDriverOnTwitter(timeout):
    # create a new browser session
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--window-size=1420,1080')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(executable_path="./chromedriver",chrome_options=chrome_options)
    driver.implicitly_wait(timeout)#30 seconds to launch the browser
    driver.maximize_window()#When launched, maximizer it
    # Navigate to the application home page
    driver.get("https://twitter.com")    
    #waiting the browser load the twitter webpage
    return driver
    
def fazerLogin(usuario,senha,driver):

    user = driver.find_element_by_name('session[username_or_email]')
    user.clear()
    user.send_keys(usuario)

    password = driver.find_element_by_name('session[password]')
    password.clear()
    password.send_keys(senha)

    password.submit()#Simulating user pressing Enter after type the password
    #I could simulate press the button to submit, but that was not necessary. The Enter is enough.

def getBotScreenName(driver):
    # currently on result page using find_elements_by_class_name method
    lists = driver.find_elements_by_class_name('u-linkComplex-target')

    bot_screen_name = ""
    for listitem in lists:
        if (listitem.get_attribute("class") == "u-linkComplex-target"):
            bot_screen_name = listitem.get_attribute("innerHTML")
            
            break
    return bot_screen_name

def FollowsUser(driver):


    follow_list = {}
    follow_arc = open("FollowCount.txt",'w')
    for linha in follow_arc:
            texto = re.sub('#+[\s\S]*',"",linha)
            texto = texto.strip()
            if len(texto) > 0:
                
                key,value = texto.split("=")
                key = key.strip()
                value = int(value.strip())

                parametros[key]=value

            if(value < 48):
                users_list = open('sources.txt','r')
                for user in users_list:
                    user = user.replace("\n","")
                    driver.get("https://twitter.com/%s" % user)
                    time.sleep(5)
                    try:
                        follow_button = driver.find_element(By.CSS_SELECTOR,"button.EdgeButton.EdgeButton--secondary.EdgeButton--medium.button-text.follow-text")
                        follow_button.click()
                        #abrir arquivo e escrever o novo valor de follows
                        value += 1
                    except:
                        if (follows == 48):
                            print("Already follows all")
                            break
                            time.sleep(10)
                    follow_arc.close()
    follow_list.close()

def criandoTweet(li,order,attributes_to_wrapped_tweet=[]):#eu pego tudo a partir de um element li

    _id = li.get_attribute("data-item-id")
    text = li.find_element(By.CSS_SELECTOR,"p.TweetTextSize.js-tweet-text.tweet-text").get_attribute("innerHTML")        
    text = extraindoApenasTexto(text)

    amount_of_comments = li.find_element_by_class_name("ProfileTweet-actionCountForPresentation").get_attribute("innerHTML")
    amount_of_likes = li.find_element_by_class_name("ProfileTweet-actionCountForPresentation").get_attribute("innerHTML")
    amount_of_retweets = li.find_element_by_class_name("ProfileTweet-actionCountForPresentation").get_attribute("innerHTML")
    timestamp = li.find_element(By.CSS_SELECTOR,"a.tweet-timestamp.js-permalink.js-nav.js-tooltip").get_attribute("title")

    publisher_id = li.find_element(By.CSS_SELECTOR,"a.account-group.js-account-group.js-action-profile.js-user-profile-link.js-nav").get_attribute("data-user-id")
    publisher_name = li.find_element(By.CSS_SELECTOR, "span.username.u-dir.u-textTruncate").find_element_by_tag_name("b").get_attribute("innerHTML")

    bot_screen_name = attributes_to_wrapped_tweet[0]
    snapshot_id = attributes_to_wrapped_tweet[1]
    snapshot_timestamp = attributes_to_wrapped_tweet[2]
    impression_order = order

    tweet = Tweet(_id,text,amount_of_comments,amount_of_likes,amount_of_retweets,timestamp,bot_screen_name,publisher_id,publisher_name,snapshot_id,snapshot_timestamp,impression_order)

    return tweet 


def pegandoTweets(tweets_lis,collection,numTweets=20,attributes_to_wrapped_tweet=[]):

    tweets = []
    order = 0
    for li in tweets_lis:
        try:
            tweet = criandoTweet(li,order,attributes_to_wrapped_tweet)

            serializedTweet= json.dumps(tweet.__dict__)            
            serializedTweet = json.loads(serializedTweet)

            collection.insert_one(serializedTweet)

            order += 1
            
            if (order == numTweets):
                break
              
        except:
            print ("excecao em pegandoTweets")
            

def pegandoTimeline(driver):
    timeline = driver.find_elements(By.CSS_SELECTOR,".stream")#find_elements_by_class_name pode usar tb
    element = timeline[0]
    tweets_lis = element.find_elements(By.CSS_SELECTOR, "li.js-stream-item.stream-item.stream-item")#ou 
    return tweets_lis

def getMongoCollection(db,col):
    mongo = pymongo.MongoClient()
    db = mongo[db]
    col = db[col]
    return col
    
def obterLastSnapshotId(collection):
    try:
        register = collection.find({},{"_id":0,"snapshot_id":1}).sort("snapshot_id",pymongo.DESCENDING).limit(1)
        register = register.next()
        resultado = register["snapshot_id"]
    except:
        print ("except snapshot_id")
        resultado = 0

    return resultado
    

def getParametrosBot(arquivo):

    parametros = {}
    for linha in arquivo:
        texto = re.sub('#+[\s\S]*',"",linha)
        texto = texto.strip()
        if len(texto) > 0:
            
            chave,valor = texto.split("=")
            chave = chave.strip()
            valor = valor.strip()
            
            parametros[chave]=valor

    return parametros        
        
def rodarColetador(arquivo):

    arquivo = open(arquivo)
    parametros = getParametrosBot(arquivo)

    collection = getMongoCollection(parametros['db'],parametros['collection'])

    #verificando se existem outros ids no banco de coletas anteriores
    snapshot_id = obterLastSnapshotId(collection)
        
    driver = getDriverOnTwitter(parametros['timeoutNavegador'])
    time.sleep(int(parametros['timeToLogIn']))
    user = parametros['user']
    password = parametros['password']
    fazerLogin(user,password,driver)
    #waiting the user login before catch the desired fields
    time.sleep(int(parametros['timeToLoadTheTimeLine']))
    bot_screen_name = getBotScreenName(driver)

    #bot_follow_count = parametros['botFollowCount']
    #verifies whether the bot follows all users or not
    #FollowsUser(driver)

    while True:

        tweets_lis = pegandoTimeline(driver)
        
        snapshot_id += 1
        snapshot_timestamp = datetime.datetime.utcnow().strftime("%a %b %d %H:%M:%S +0000 %Y")
        
        attributes_to_wrapped_tweet = [bot_screen_name,snapshot_id,snapshot_timestamp]
        
        pegandoTweets(tweets_lis,collection,int(parametros['amountOfTweets']),attributes_to_wrapped_tweet)
        
        #colocando o bot para dormir
        time.sleep(int(parametros['botSleepTime']))
        #
        try:
            print("atualiza?")
            driver.find_element(By.CSS_SELECTOR,"button.new-tweets-bar.js-new-tweets-bar").click()
            print ("atualizou")
        except:
            continue

#def rodarColetadores(arquivo):
    
#    for arq in arquivos:
#        rodarColetador(open(arq

if __name__ == '__main__':

    arquivo = input("Arquivo de configuração com o path (ex: path/settings.txt):")
    rodarColetador(arquivo)

