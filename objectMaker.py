from classes.Circle import Circle
from classes.Network import Network
from classes.User import User
from edgeMaker import driver
from os import walk
from neo4j import GraphDatabase
import re

#c = Circle('a',[1,2])
#print(c.name)
#print(c.users)

#n = Network('a',[1,2],[3,4])
#print(n.name)
#print(n.circles)
#print(n.users)

#u = User('a',[1,2])
#print(u.name)
#print(u.features)

def _create_network(tx,net):
    tx.run("CREATE (n:Network) "
        "SET n.name = $name ",name=net.name)

def _create_circle(tx,netName,cir):
    tx.run("CREATE (c:Circle) "
        "SET c.name = $name ",name=netName + '-' + cir.name)

def _create_user(tx,netName,usr):
    ufeats = ['--none--']
    if(usr.features):
        ufeats = usr.features

    tx.run("CREATE (u:User) "
        "SET u.name = $name "
        "SET u.feats = $feats ",name=netName + '-' + usr.name,feats=ufeats)

def getNetworks(path):
    networks = []
    filePat = '^(\d*)\.([a-zA-Z]*)'
    r = re.compile(filePat)
    for (dirpath,dirnames,filenames) in walk(path):
        for f in filenames:
            res = r.match(f)
            network = res.group(1)

            if(network not in networks):
                networks.append(network)
    
    return networks

def getCircles(path,netName):
    circles = []
    with open(path + netName + '.circles') as C:
        cContent = C.readlines()
        for line in cContent:
            token = line.split()

            circleName = token[1]
            circleUsers = []
            for u in token[2:]:
                circleUsers.append(u)
            
            mCircle = Circle(circleName,circleUsers)
            circles.append(mCircle)

    return circles    

def getFeatures(path,netName):
    features = []
    with open(path + netName + '.featnames',encoding='utf-8') as F:
        fContent = F.readlines()
        for line in fContent:
            features.append(line.split()[1])

    return features

def getUsers(path,netName,features):
    users = []
    with open(path + netName + '.feat',encoding='utf-8') as F1:
        f1Content = F1.readlines()
        for line in f1Content:
            token = line.split()
            uName = token[0]
            fPos = []

            for i in range(1,len(token)):
                if(token[i] == '1'):
                    fPos.append(i-1)
            
            ufeats = []
            for p in fPos:
                ufeats.append(features[p])
            
            mUser = User(uName,ufeats)
            users.append(mUser)

    return users

def getEdges(path,netName):
    edges = {}
    with open(path + netName + '.edges',encoding='utf-8') as E:
        eContent = E.readlines()
        for line in eContent:
                token = line.split()
                if token[0] in edges.keys():
                    edges[token[0]].append(token[1])
                else:
                    edges[token[0]] = []
                    edges[token[0]].append(token[1])
    
    return edges

def mDriver(netNum):
    mUri = "bolt://localhost:7687"
    conn = GraphDatabase.driver(uri=mUri, auth=('neo4j', 'sjsu123'),encrypted=False)

    print('con success!')

    networks = getNetworks('./data')

    count = 0
    for nName in networks:
        count += 1
        circles = getCircles('./data/',nName)
        features = getFeatures('./data/',nName)
        users = getUsers('./data/',nName,features)  
        edges = getEdges('./data/',nName)
                    

    #todo: inser user's feature array into db
        mNetwork = Network(nName,circles,users)

    #insert all into graphdb
        with conn.session() as session:
            session.write_transaction(_create_network,mNetwork)

            for cir in circles:
                session.write_transaction(_create_circle,nName,cir)

            for usr in users:
                session.write_transaction(_create_user,nName,usr)

            driver(session,mNetwork,circles,users,edges)

        if(count == netNum):
            exit(0)
    conn.close()

mDriver(3)