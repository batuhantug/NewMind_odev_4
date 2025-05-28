# Use official Neo4j 5 image
FROM neo4j:5

# Set default Neo4j user and password
ENV NEO4J_AUTH=neo4j/testpassword

# Optional: Enable CSV file import from /import (already default in neo4j)
ENV NEO4J_dbms_security_allow__csv__import__from__file__urls=true

# Expose HTTP and Bolt ports
EXPOSE 7474 7687