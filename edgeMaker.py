##todo create edges

#_network_circle
def _network_circle(tx,network,circle):
    tx.run("MATCH (n:Network),(c:Circle) "
    "WHERE n.name = $netName AND c.name=$circName "
    "CREATE (n)-[r:Contains]->(c) ",netName=network.name,circName=network.name + '-' + circle.name)
#_network_user
def _network_user(tx,network,user):
    tx.run("MATCH (n:Network),(u:User) " #always include the trailing space
    "WHERE n.name = $netName AND u.name=$usrName "
    "CREATE (n)-[r:Contains]->(u) ",netName=network.name,usrName=network.name + '-' + user.name)
#circle_user
def _circle_user(tx,network,circle,userName):
    tx.run("MATCH (c:Circle),(u:User) "
    "WHERE c.name = $circName AND u.name=$usrName "
    "CREATE (c)-[r:Contains]->(u) ",circName=network.name + '-' + circle.name,usrName=network.name + '-' + userName)

#user_follows_user
def _user_follows_user(tx,network,u1,u2):
    tx.run("MATCH (u1:User),(u2:User) "
    "WHERE u1.name = $u1Name AND u2.name=$u2Name "
    "CREATE (u1)-[r:Friends]->(u2) ",u1Name=network.name + '-' + u1,u2Name=network.name + '-' + u2)

def driver(session,network,circles,users,edges):
    for c in circles:
        session.write_transaction(_network_circle,network,c)
    
    for u in users:
        session.write_transaction(_network_user,network,u)

    for c in circles:
        for u in c.users:
            session.write_transaction(_circle_user,network,c,u)

    for follower in edges:
        for followee in edges[follower]:
            session.write_transaction(_user_follows_user,network,follower,followee) 


    


    