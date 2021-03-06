# -*- coding: utf-8 -*-
"""CaixeiroViajante.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1OKgcfpMA_0aafQmqVxhqhsV54fcHMk_E
"""

class TSP():
  def __init__(self, nomeArquivo):
    self.lerArquivo(nomeArquivo)
    self.gerarListaDeCidades()
    self.iniciarPopulacao()

  def lerArquivo(self, nomeArquivo):
    with open(nomeArquivo, 'r') as fp:
      conteudoArquivo = fp.read().split()
      self.tsplib(conteudoArquivo)

  def tsplib(self, conteudoArquivo):
    idx = conteudoArquivo.index('NAME:') + 1
    self.nome = conteudoArquivo[idx]

    idx = conteudoArquivo.index('TYPE:') + 1
    self.tipo = conteudoArquivo[idx]

    idx = conteudoArquivo.index('COMMENT:') + 1
    self.comentario = conteudoArquivo[idx]

    idx = conteudoArquivo.index('DIMENSION:') + 1
    self.dimensao = int(conteudoArquivo[idx])

    idx = conteudoArquivo.index('EDGE_WEIGHT_TYPE:') + 1
    self.tipoPesoBorda = conteudoArquivo[idx]

    idx = conteudoArquivo.index('EDGE_WEIGHT_FORMAT:') + 1
    self.formatoPesoBorda = conteudoArquivo[idx]


    if self.formatoPesoBorda != 'FULL_MATRIX':
      self.formatoPesoSecao = []
      return

    idx = conteudoArquivo.index('EDGE_WEIGHT_SECTION') + 1
    inf = int(conteudoArquivo[idx])
    dados = []
    for i in range(self.dimensao):
      if len(conteudoArquivo) > idx + self.dimensao:
        dados.append(list(map(int, conteudoArquivo[idx:idx + self.dimensao])))
      else:
        self.formatoPesoSecao = []
        return

      idx += self.dimensao

    self.formatoPesoSecao = dados

  def gerarListaDeCidades(self):
    self.listaCidade = []
    for rota in self.formatoPesoSecao:
      for i in range(len(rota)):
        if i+1 == len(rota):
          break

        coordX = int(rota[i])
        coordY = int(rota[i+1])
        self.listaCidade.append(Cidade(coordX, coordY))
        i = i + 1
    self.listaCidade = list(dict.fromkeys(self.listaCidade))

  def criarRota(self, rotaIndex):
    rota = []
    rotaSemFormatar = self.formatoPesoSecao[rotaIndex]
    #print('rf', rotaSemFormatar)
    for i in range(len(rotaSemFormatar)):
      if i+1 == len(rotaSemFormatar):
        #print('rota',rota)
        return rota

      coordX = int(rotaSemFormatar[i])
      coordY = int(rotaSemFormatar[i+1])
      rota.append(Cidade(coordX, coordY))
      i = i + 1

  def iniciarPopulacao(self):
    self.populacao = []

    for i in range(0, self.dimensao):
        self.populacao.append(self.criarRota(i))
    #print(self.populacao)

class Cidade:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def distancia(self, cidade):
        xDis = abs(self.x - cidade.x)
        yDis = abs(self.y - cidade.y)
        distancia = np.sqrt((xDis ** 2) + (yDis ** 2))
        return distancia
    
    def __key(self):
        return (self.x, self.y)

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, outro):
        if isinstance(outro, Cidade):
            return self.__key() == outro.__key()
        return NotImplemented

    def __repr__(self):
        return "(" + str(self.x) + "," + str(self.y) + ")"

import numpy as np, random, operator, pandas as pd, matplotlib.pyplot as plt
import copy

class Fitness:
    def __init__(self, rota):
        self.rota = rota
        self.distancia = 0
        self.fitness= 0.0
    
    def distanciaRota(self):
        if self.distancia ==0:
            distanciaCaminho = 0
            for i in range(0, len(self.rota)):
                daCidade = self.rota[i] 
                paraCidade = None
                if i + 1 < len(self.rota):
                    paraCidade = self.rota[i + 1]
                else:
                    paraCidade = self.rota[0]
                distanciaCaminho += daCidade.distancia(paraCidade)
            self.distancia = distanciaCaminho
        return self.distancia
    
    def rotaFitness(self):
        if self.fitness == 0:
            self.fitness = 1 / float(self.distanciaRota())
        return self.fitness

def criarListaCidades():
  listaCidades = []

  for i in range(0,25):
    listaCidades.append(Cidade(x=int(random.random() * 200), y=int(random.random() * 200)))
  return listaCidades

def criarRota(listaCidade):
  rota = random.sample(listaCidade, len(listaCidade))
  return rota

def populacaoInicial(tamanhoPop, listaCidade):
  populacao = []

  for i in range(0, tamanhoPop):
      populacao.append(criarRota(listaCidade))
  return populacao

def rankRotas(populacao):
  fitnessResultados = {}
  for i in range(0,len(populacao)):
      fitnessResultados[i] = Fitness(populacao[i]).rotaFitness()
  return sorted(fitnessResultados.items(), key = operator.itemgetter(1), reverse = True)

def selecao(popRanked, eliteTamanho):
  resultadosSelecao = []
  df = pd.DataFrame(np.array(popRanked), columns=["Index","Fitness"])
  df['cum_sum'] = df.Fitness.cumsum()
  df['cum_perc'] = 100*df.cum_sum/df.Fitness.sum()
  
  for i in range(0, eliteTamanho):
      resultadosSelecao.append(popRanked[i][0])
  for i in range(0, len(popRanked) - eliteTamanho):
      pick = random.random()
      for i in range(0, len(popRanked)):
          if pick <= df.iat[i,3]:
              resultadosSelecao.append(popRanked[i][0])
              break
  return resultadosSelecao

def selecaoPais(populacao, resultadosSelecao):
  selecaoPais = []
  for i in range(0, len(resultadosSelecao)):
      index = resultadosSelecao[i]
      selecaoPais.append(populacao[index])
  return selecaoPais

def cruzamento(pai1, pai2):
  filho = []
  filhoP1 = []
  filhoP2 = []
  
  geneA = int(random.random() * len(pai1))
  geneB = int(random.random() * len(pai1))
  
  geneInicial = min(geneA, geneB)
  geneFinal = max(geneA, geneB)

  for i in range(geneInicial, geneFinal):
      filhoP1.append(pai1[i])
      
  filhoP2 = [item for item in pai2 if item not in filhoP1]

  filho = filhoP1 + filhoP2
  return filho

def populacaoCrossover(selecaoPais, eliteTamanho):
  filhos = []
  length = len(selecaoPais) - eliteTamanho
  pais = random.sample(selecaoPais, len(selecaoPais))

  for i in range(0,eliteTamanho):
      filhos.append(selecaoPais[i])
  
  for i in range(0, length):
      filho = cruzamento(pais[i], pais[len(selecaoPais)-i-1])
      filhos.append(filho)
  return filhos


def mutacao(individuo, chanceMutacao):
  for trocado in range(len(individuo)):
      if random.random() < chanceMutacao:
          trocaCom = int(random.random() * len(individuo))
          
          cidade1 = individuo[trocado]
          cidade2 = individuo[trocaCom]
          
          individuo[trocado] = cidade2
          individuo[trocaCom] = cidade1
  return individuo

def populacaoMutacao(populacao, chanceMutacao):
  popMutante = []
  
  for i in range(0, len(populacao)):
      mutacaoIndex = mutacao(populacao[i], chanceMutacao)
      popMutante.append(mutacaoIndex)
  return popMutante

def proximaGeracao(geracaoAtual, eliteTamanho, chanceMutacao):
  popRanked = rankRotas(geracaoAtual)
  resultadosSelecao = selecao(popRanked, eliteTamanho)
  paisSelecionados = selecaoPais(geracaoAtual, resultadosSelecao)
  filhos = populacaoCrossover(paisSelecionados, eliteTamanho)
  proximaGeracao = populacaoMutacao(filhos, chanceMutacao)
  return proximaGeracao


def algoritmoGenetico(populacao, tamanhoPop, eliteTamanho, chanceMutacao, geracoes):
  pop = populacao
  print("Distancia inicial : " + str(1 / rankRotas(pop)[0][1]))
  
  for i in range(0, geracoes):
      pop = proximaGeracao(pop, eliteTamanho, chanceMutacao)
  
  print("Distancia final : " + str(1 / rankRotas(pop)[0][1]))
  melhorRotaIndex = rankRotas(pop)[0][0]
  melhorRota = pop[melhorRotaIndex]
  # return melhorRota

#criando uma população a partir de arquivos .atsp

br17 = TSP('br17.atsp')
algoritmoGenetico(populacao=copy.deepcopy(br17.populacao), tamanhoPop=20, eliteTamanho=7, chanceMutacao=0.01, geracoes=500)

ftv33 = TSP('ftv33.atsp')
algoritmoGenetico(populacao=copy.deepcopy(ftv33.populacao), tamanhoPop=20, eliteTamanho=7, chanceMutacao=0.01, geracoes=500)

#criando uma população genérica

listaCidade = criarListaCidades()
popIni = populacaoInicial(20, listaCidade)

algoritmoGenetico(populacao=popIni, tamanhoPop=20, eliteTamanho=7, chanceMutacao=0.01, geracoes=500)