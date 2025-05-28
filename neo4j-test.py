from neo4j import GraphDatabase
import os

# Connect to the database
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "testpassword"))

delete_all_query = "MATCH (n) DETACH DELETE n"

# Get the absolute path to the data directory and convert to forward slashes
data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'import')).replace('\\', '/')

constraints = [
    
    # Note
    """
    CREATE CONSTRAINT Note_id IF NOT EXISTS
    FOR (n:Note)
    REQUIRE n.id IS UNIQUE
    """,

    # Tag
    """
    CREATE CONSTRAINT Tag_id IF NOT EXISTS
    FOR (t:Tag)
    REQUIRE t.id IS UNIQUE
    """,

    # Concept
    """
    CREATE CONSTRAINT Concept_name IF NOT EXISTS
    FOR (c:Concept)
    REQUIRE c.name IS UNIQUE
    """,

    # Mind Map
    """
    CREATE CONSTRAINT MindMap_id IF NOT EXISTS
    FOR (m:MindMap)
    REQUIRE m.id IS UNIQUE
    """
]



load_csv_queries = [
    
    # Load Notes
    f"""
    LOAD CSV WITH HEADERS FROM 'file:///notes.csv' AS row
    MERGE (n:Note {{id: row.id}})
    SET n.title = row.title,
        n.content = row.content,
        n.embedding = row.embedding
    """,


    # Load Tags
    f"""
    LOAD CSV WITH HEADERS FROM 'file:///tags.csv' AS row
    MERGE (t:Tag {{id: row.id}})
    SET t.name = row.name
    """,

    # Load Concepts
    f"""
    LOAD CSV WITH HEADERS FROM 'file:///concepts.csv' AS row
    MERGE (c:Concept {{name: row.name}})
    SET c.embedding = row.embedding
    """,

    # Load MindMaps
    f"""
    LOAD CSV WITH HEADERS FROM 'file:///mindmaps.csv' AS row
    MERGE (m:MindMap {{id: row.id}})
    SET m.name = row.name
    """
]

cypher_statements = [

    # Note -> Tag
    """
    LOAD CSV WITH HEADERS FROM 'file:///note_tags.csv' AS hasTag
    MATCH (n:Note {id: hasTag.note_id})
    MATCH (t:Tag {id: hasTag.tag_id})
    MERGE (n)-[:HAS_TAG]->(t)
    """,

    # Note -> Concept
    """
    LOAD CSV WITH HEADERS FROM 'file:///note_concepts.csv' AS mentions
    MATCH (n:Note {id: mentions.note_id})
    MATCH (c:Concept {name: mentions.concept_name})
    MERGE (n)-[:MENTIONS]->(c)
    """,

    # Concept -> Concept
    """
    LOAD CSV WITH HEADERS FROM 'file:///related_concepts.csv' AS relatedTo
    MATCH (c1:Concept {name: relatedTo.concept1})
    MATCH (c2:Concept {name: relatedTo.concept2})
    MERGE (c1)-[:RELATED_TO {similarity: toFloat(relatedTo.similarity)}]->(c2)
    """,

    # Note -> MindMap
    """
    LOAD CSV WITH HEADERS FROM 'file:///mindmap_notes.csv' AS belongsTo
    MATCH (m:MindMap {id: belongsTo.map_id})
    MATCH (n:Note {id: belongsTo.note_id})
    MERGE (n)-[:BELONGS_TO]->(m)
    """
]



def create_constraints():
    with driver.session() as session:
        for query in constraints:
            session.run(query)
            print("Executed constraint:", query.strip().splitlines()[0])

def reset_database():
    with driver.session() as session:
        # Delete all existing nodes and relationships
        session.run(delete_all_query)
        print("All nodes and relationships deleted.")

        # Create constraints
        for query in constraints:
            session.run(query)
            print("Executed constraint:", query.strip().splitlines()[0])

def load_csv_data():
    with driver.session() as session:
        for query in load_csv_queries:
            try:
                session.run(query)
                print("Executed:", query.strip().splitlines()[0])
            except Exception as e:
                print(f"Error executing query: {query.strip().splitlines()[0]}")
                print(f"Error details: {str(e)}")

def load_relationships():
    with driver.session() as session:
        for query in cypher_statements:
            session.run(query)
            print("Executed query:\n", query.strip().splitlines()[0])


if __name__ == "__main__":
    reset_database()
    create_constraints()
    load_csv_data()
    load_relationships()
    driver.close()