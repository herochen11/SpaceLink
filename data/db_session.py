from py2neo import Graph


def db_auth():
    user = 'neo4j'
    pword = '0000'
    graph = Graph("http://127.0.0.1:7474/db/data/", username=user, password=pword)
    return graph
