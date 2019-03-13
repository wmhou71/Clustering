'''
NodeTable                          GroupTable

Node number   X    Y    Group      Group number  centralX   centralY
-------------------------------    -----------------------------------
    0        2.0   3.0    1             1          3.33        5.00
    1       12.0  13.0    2             2         12.50        1.67
    2        2.0   1.0    1             3         16.13       19.87
    .         .     .     .             .           .           . 
    .         .     .     .             .           .           . 

'''
import math
import numpy
from operator import itemgetter, attrgetter


def read(datafile):
    inputfile = open(datafile, "r")
    data = []
    for line in inputfile.readlines():
        tmp = []
        for key in line[0:-1].split(" "):
            tmp.append(key)
        data.append(tmp)
    return data

def buildNodeTables(data):
    nodeTable = [[" " for m in range(4)] for n in range(len(data))]
    for i in range(len(data)):
        nodeTable[i][0]=i
        nodeTable[i][1]=float(data[i][0])
        nodeTable[i][2]=float(data[i][1])
        nodeTable[i][3]=0
    #print(nodeTable)
    return nodeTable

def getDistance(nodeA_x, nodeA_y, nodeB_x, nodeB_y): #-----計算兩點間距離
    distance = 0.0
    distance = math.sqrt(pow(nodeB_x-nodeA_x, 2)+pow(nodeB_y-nodeA_y, 2))
    return distance

def deleteOutlier(nodeTable): #-----刪除離群點
    X,Y=[],[]
    for i in range(len(nodeTable)):
        X.append(nodeTable[i][1])
        Y.append(nodeTable[i][2])
    
    avgX, avgY = numpy.mean(X), numpy.mean(Y)
    stdX, stdY = numpy.std(X), numpy.std(Y)
    
    #print(avgX, avgY, stdX, stdY)
    dCount = 0
    for i in range(len(nodeTable)):
        #print(i, (nodeTable[i][1]-avgX)/stdX, (nodeTable[i][2]-avgY)/stdY)
        if (nodeTable[i][1]-avgX)/stdX > 3 and (nodeTable[i][2]-avgY)/stdY >3:
            nodeTable[i][3] = -1
            dCount+=1

    newNodeTable = [[" " for m in range(4)] for n in range(len(nodeTable)-dCount)]
    add = 0

    for i in range(len(data)):
        if nodeTable[i][3] ==-1:
            pass
        else:
            #print("add =", add, "i=", i)
            newNodeTable[add][0] = add
            newNodeTable[add][1] = float(data[i][0])
            newNodeTable[add][2] = float(data[i][1])
            newNodeTable[add][3] = 0
            add+=1

    #print(newNodeTable)
    return newNodeTable, dCount


def buildInitialNodes(k, nodeTable): #-----兩階段建立InitialNodes(找出起始兩點)
    initialNodes = []
    largeDistance = 0.0
    startTwoNodes = [0, 0]

    for i in range(len(nodeTable)): #-----找出起始兩點
        for j in range(len(nodeTable)):
            if i != j and i<j:
                if getDistance(nodeTable[i][1], nodeTable[i][2], nodeTable[j][1], nodeTable[j][2])> largeDistance:
                    startTwoNodes[0], startTwoNodes[1] = i, j
                    largeDistance = getDistance(nodeTable[i][1], nodeTable[i][2], nodeTable[j][1], nodeTable[j][2])

    for i in range(len(nodeTable)): #-----找出起始兩點，將座標加入initialNodes陣列
        for element in startTwoNodes:
            if nodeTable[i][0] == element:
                initialNodes.append([element, nodeTable[i][1], nodeTable[i][2]])
    
    
    distanceArray=[]
    distanceTable=[]
    trueCount=0

    initialArray=[] #--紀錄在起始的Node
    for i in range(len(initialNodes)):
        initialArray.append(initialNodes[i][0])

    while(len(initialNodes)<k): #-----找出其餘k-2點
        #print("ARRAY=",initialArray)
        for i in range(len(nodeTable)): 
            if nodeTable[i][0] in initialArray:
                pass
            else:
                for j in range(len(initialNodes)):
                    distanceArray.append(getDistance(nodeTable[i][1], nodeTable[i][2], initialNodes[j][1], initialNodes[j][2]))
                for key in distanceArray:
                    #print(nodeTable[i][0], distanceArray)
                    if key > largeDistance / k: #-----判斷特定點到起始兩點需有一定距離
                        trueCount+=1
                        if trueCount== len(distanceArray):
                            distanceTable.append([nodeTable[i][0], sum(distanceArray[:])])
                            distanceArray=[]
                            trueCount = 0
                    else:
                        distanceArray=[]
                        trueCount = 0
        distanceTable = sorted(distanceTable, key=itemgetter(1), reverse=True)
        #print(distanceTable)
        for i in range(len(nodeTable)):
            if nodeTable[i][0]==distanceTable[0][0]:
                initialNodes.append([distanceTable[0][0], nodeTable[i][1], nodeTable[i][2]])
                initialArray.append(distanceTable[0][0])

        distanceTable=[]

    return initialNodes

def initialize(initialNodes, nodeTable): #-----修改NodeTable和建立GroupTable
    for i in range(len(initialNodes)):
        for j in range(len(nodeTable)):
            if nodeTable[j][0] == initialNodes[i][0]:
                nodeTable[j][3] = i+1

    groupTable = [[" " for m in range(3)] for n in range(len(initialNodes))]
    for i in range(len(groupTable)): 
        groupTable[i][0]=i+1
        for j in range(len(nodeTable)):
            if nodeTable[j][3] == groupTable[i][0]:
                groupTable[i][1], groupTable[i][2] = nodeTable[j][1], nodeTable[j][2]
    
    #print(nodeTable)
    #print(groupTable)
    #print("#######")
    return nodeTable, groupTable
####################################################################
def Run(initialNodes, nodeTable, groupTable):
    initialArray=[]
    for i in range(len(initialNodes)):
        initialArray.append(initialNodes[i][0])

    distanceArray=[]
    for i in range(len(nodeTable)):
        if nodeTable[i][0] in initialArray:
            pass
        else:
            for j in range(len(groupTable)):
                distanceArray.append(getDistance(nodeTable[i][1], nodeTable[i][2], groupTable[j][1], groupTable[j][2]))
            nodeTable[i][3] = distanceArray.index(min(distanceArray))+1
            groupTable = renewGroupTable(nodeTable[i][3], nodeTable, groupTable)
            distanceArray = []

    #print(nodeTable)
    #print(groupTable)
    return nodeTable, groupTable

def renewGroupTable(adjustGroup, nodeTable, groupTable): #-----更新GroupTable
    sumX, sumY, count = 0.0, 0.0, 0
    for i in range(len(nodeTable)):
        if nodeTable[i][3] == adjustGroup:
            sumX+=nodeTable[i][1]
            sumY+=nodeTable[i][2]
            count += 1
    groupTable[adjustGroup-1][1] = sumX/count
    groupTable[adjustGroup-1][2] = sumY/count
    return groupTable

def calculateMeasure(nodeTable, groupTable): #-----衡量分群後的效果指標
    tempMeasure = 0.0
    groupMeasure = 0.0
    for i in range(len(nodeTable)):
        for j in range(len(groupTable)):
            if nodeTable[i][3] != groupTable[j][0]: #-----計算各點與不同群的中心點距離之平均
                tempMeasure += getDistance(nodeTable[i][1], nodeTable[i][2], groupTable[j][1], groupTable[j][2])
        groupMeasure += tempMeasure/(len(groupTable)-1)
        tempMeasure = 0.0
    groupMeasure = groupMeasure / len(nodeTable)
    #print(groupMeasure)
    return groupMeasure

########################################################################

def cluster(X, Y, groupTable): #-----分群器
    distanceArray=[]
    for i in range(len(groupTable)):
        distanceArray.append(getDistance(X, Y, groupTable[i][1], groupTable[i][2]))
    groupBelong = distanceArray.index(min(distanceArray))+1

    print("( X=", X, "Y=", Y, " ClusterID=", groupBelong, ")")

    return groupBelong

###---------------main---------------###

data = read('Clustering_test1.txt')
nodeTable = buildNodeTables(data)
nodeTable, dCount = deleteOutlier(nodeTable)

k = input('Please key in how many group you want to divide：')

initialNodes = buildInitialNodes(int(k), nodeTable)
nodeTable, groupTable = initialize(initialNodes, nodeTable)

nodeTable, groupTable = Run(initialNodes, nodeTable, groupTable)
groupMeasure = calculateMeasure(nodeTable, groupTable)

print("k = ", k, "Cluster Measure =", groupMeasure)

X = input('Please key in the node of X ：')
Y = input('Please key in the node of Y ：')

GB = cluster(float(X), float(Y), groupTable)
