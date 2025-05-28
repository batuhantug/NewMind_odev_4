# NewMind_-dev_4

neo4j-test.py dosyasını veritabanını kurmak için kullandım.

docker komutları:
docker run -d \
  --name neo4j \
  -p 7474:7474 \
  -p 7687:7687 \
  -v "D:/python_projects/Neo4j_project/patika/import:/var/lib/neo4j/import" \
  -e NEO4J_AUTH=neo4j/testpassword \
  my-neo4j

