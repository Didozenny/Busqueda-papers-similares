import string 
import binascii
import random
import numpy
import time
from csv import reader
import re
import sys
#valores globales para hashing
a = []
b = []
p = 2**32-1

def GenerateRandomNumbs(k):#generamos k random numb para la funcion hash
	nums = []
	for x in range(k):
		randNum = random.randint(0,2**32-1)
		while randNum in nums:
			randNum = random.randint(0,2**32-1)
		nums.append(randNum)
	return nums

def hash(i,shingle):#aplicamos funcion hash
	return (a[i]*shingle+b[i])%p

def Minhashing(line,k,h):#k lenght of shingle, h number of hash functions. Minhash a un documento
	#generamos shingles del documento
	shingles = set() #set(no se repiten elementos)
	if(k == 1):#generamos lista de shingles de largo 1
		for x in line:
			shingles.add(binascii.crc32(x.encode()) & 0xffffffff)
	else:#generamos lista de shingles de largo k>1
		for x in range(len(line)):
			if(x+k <= len(line)):
				newshingle = ''
				for y in range(k):
					newshingle = newshingle+line[x+y]
				shingles.add(binascii.crc32(newshingle.encode()) & 0xffffffff)
	#generamos las signatures del documento
	signature = []
	for j in range(h):
		minval = 2**32-1
		for shingle in shingles:
			minval = min(minval,hash(j,shingle))
		signature.append(minval)
	return signature



if __name__ == "__main__":
	file = open('data_input.csv','r')
	output = open("Resultado.txt","w")
	#variables para minhashing
	maxSampleSize = 10000
	signatures = []
	k = 1
	h = 100
	treshhold = 0.7
	a = GenerateRandomNumbs(h)
	b = GenerateRandomNumbs(h)
	#variables para LSH
	band_num = 20
	rowb = int(h/band_num)
	buckets = []
	for x in range(band_num):
		buckets.append({})
	#almacenamiento de resultados
	similars = []
	#ID
	Id_document = -2
	print("Generamos matriz de signatures y hacemos hash a los buckets")
	print("Time: 0")
	start = time.time()
	for line in file:#leemos documentos
		Id_document += 1
		if(Id_document == -1):#saltamos linea sin documento
			continue
		if(Id_document == maxSampleSize):
			break
		line=re.sub(r'^.*?,', ',', line)##eliminamos el numero de id
		if("withdrawn" in line):#eliminamos ruido
			Id_document -= 1;
			continue
		line = line.translate(line.maketrans('','',string.punctuation))#eliminamos puntuacion
		line = line.lower()#eliminamos mayusculas
		line = line.split(sep=" ")#separamos en palabras que formaran shingles
		signatures.append(Minhashing(line,k,h))#generamos y comparamos signatures
		#LSH
		for i in range(band_num):##hacemos hash y generamos los buckets
			hashval = 1
			for j in range(rowb):#hash
				hashval = ((hashval*33)+signatures[Id_document][i*rowb+j])%1000003
			if((hashval in buckets[i])==False):#checkeamos que la key haya sido registrada
				buckets[i][hashval] = []
			buckets[i][hashval].append(Id_document)#agregamos el documento al bucket
	#buscamos pares candidatos
	print("Buscando pares candidatos")
	print("Time:",time.time()-start)
	candidatos = set()
	for x in range(band_num):#exploramos por banda
		val_buckets = buckets[x].values()#buckets de la banda x
		for lists in val_buckets:#listas correspondientes a cada bucket
			if(len(lists)>1):#si hay mas de un documento en la bucket avanzamos
				for i in range(len(lists)-1):#tomamos todos los pares de documentos y agregamos a candidatos
					for j in range(i+1,len(lists)):
						candidatos.add(frozenset((lists[i],lists[j])))
	print("Comienza comparacion")
	print("Time:",time.time()-start)
	for pair in candidatos:#por cada par de candidatos
		Lpair = []
		for i in pair:
			Lpair.append(i)
		signature1 = signatures[Lpair[0]]
		signature2 = signatures[Lpair[1]]
		count = 0
		for x in range(h):#interseccion
			count = count+(signature1[x] == signature2[x])
		if(count/h >= treshhold):#coeficiente Jaccard
			similars.append({Lpair[0],Lpair[1]})
	sys.stdout = output
	print("Treshhold:", treshhold, "")
	print("Resultados:")
	print("Time:",time.time()-start)
	print("Cantidad de candidatos:",len(candidatos))
	print("Cantidad de elementos similares:",len(similars))
	print("Elementos similares:")
	print(similars)
	