from multiprocessing import Pool
import timelineScrap

__author__ = "Tiago Cruz de França"
__copyright__ = "Copyright 2018, UFRRJ"
__credits__ = ["Tiago França"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Tiago França, Edu Mangabeira"
__email__ = "tcruz.franca@gmail.com"
__status__ = "Test"

if __name__ == '__main__':

    listaArquivos = input("Arquivo com lista de configuracoes:")
    listaArquivos = open(listaArquivos)
    #resp = input("Deseja seguir mais usuários do Twitter?  s - sim  n - não")
    #cont = timelineScrap.getFollowIsFalse(resp)

    
    arquivos = []
    for arquivo in listaArquivos:
        arquivo = arquivo.replace("\n","")
        #arquivo = open(arquivo)
        arquivos.append(arquivo)
    
    with Pool() as p:
        p.map(timelineScrap.rodarColetador,arquivos)    
    print ("rodando")
        
