from neo4j import GraphDatabase
from transformers import pipeline

# Neo4j bağlantısı
uri = "bolt://localhost:7687"
user = "neo4j"
password = "testpassword"

driver = GraphDatabase.driver(uri, auth=(user, password))

def get_notes():
    with driver.session() as session:
        result = session.run("MATCH (n:Note) RETURN n.id AS id, n.content AS content")
        return [{"id": r["id"], "content": r["content"]} for r in result]

# Ücretsiz LLM pipeline, burada distilgpt2 kullandım (soru-cevap için optimize değil ama örnek amaçlı)
generator = pipeline('text-generation', model='distilgpt2')

def answer_question(question, notes):
    # Basit bir eşleşme mantığı: sorudaki kelimelere göre en ilgili notu bul
    question_words = set(question.lower().split())
    best_note = None
    best_overlap = 0

    for note in notes:
        note_words = set(note["content"].lower().split())
        overlap = len(question_words.intersection(note_words))
        if overlap > best_overlap:
            best_overlap = overlap
            best_note = note

    if best_note is None:
        return "Maalesef sorunuza uygun bir not bulunamadı.", None

    # Not içeriğinden model ile yanıt üret (basitçe içeriği modelden geçiriyoruz)
    prompt = f"Soru: {question}\nNot: {best_note['content']}\nCevap:"
    response = generator(prompt, max_length=50, num_return_sequences=1)[0]['generated_text']

    # Yanıttan "Cevap:" sonrası kısmı alalım
    answer = response.split("Cevap:")[-1].strip()

    return answer, best_note["id"]

# Kullanıcıdan soru alalım (örnek)
notes = get_notes()
user_question = input("Sorunuz: ")

answer, note_id = answer_question(user_question, notes)

print(f"Yanıt: {answer}")
if note_id:
    print(f"Yanıt, ID'si {note_id} olan nottan alınmıştır.")

driver.close()