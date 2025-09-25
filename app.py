import json
from flask import Flask, jsonify, request
from flasgger import Swagger

# ==============================================================================
# 1. CLASSE DISTRIBUTORE E DATI INIZIALI
# ==============================================================================

class Distributore:
    """Rappresenta un singolo distributore con tutte le sue informazioni."""
    def __init__(self, id, nome, indirizzo, citta, provincia, lat, lon,
                 livello_benzina, capacita_benzina,
                 livello_diesel, capacita_diesel,
                 prezzo_benzina, prezzo_diesel):
        self.id = id
        self.nome = nome
        self.indirizzo = indirizzo
        self.citta = citta
        self.provincia = provincia
        self.lat = lat
        self.lon = lon
        self.livello_benzina = livello_benzina
        self.capacita_benzina = capacita_benzina
        self.livello_diesel = livello_diesel
        self.capacita_diesel = capacita_diesel
        self.prezzo_benzina = prezzo_benzina
        self.prezzo_diesel = prezzo_diesel

    def to_dict(self):
        """Converte l'oggetto Distributore in un dizionario per le risposte API."""
        return self.__dict__

# Lista in memoria che funge da database
distributori = [
    Distributore(1, "Iperstaroil Milano", "Via Roma 1", "Milano", "MI", 45.4642, 9.1900, 5000, 10000, 8000, 15000, 1.85, 1.75),
    Distributore(2, "Iperstaroil Roma", "Piazza del Popolo 10", "Roma", "RM", 41.9109, 12.4768, 7500, 12000, 9000, 12000, 1.89, 1.79),
    Distributore(3, "Iperstaroil Napoli", "Via Toledo 15", "Napoli", "NA", 40.8399, 14.2522, 4000, 9000, 6000, 10000, 1.82, 1.72),
    Distributore(4, "Iperstaroil Torino", "Corso Vittorio Emanuele II 50", "Torino", "TO", 45.0678, 7.6745, 9000, 15000, 11000, 16000, 1.86, 1.76),
    Distributore(5, "Iperstaroil Milano Sud", "Viale Lombardia 20", "Milano", "MI", 45.4431, 9.2218, 6000, 10000, 7000, 13000, 1.84, 1.74)
]

# ==============================================================================
# 2. CREAZIONE DELL'APPLICAZIONE FLASK
# ==============================================================================

app = Flask(__name__)

# ==============================================================================
# 3. ROTTE API (con documentazione Swagger)
# ==============================================================================

@app.route('/api/distributori', methods=['GET'])
def get_distributori():
    """
    Elenco distributori
    ---
    get:
      summary: Elenco distributori
      description: Ritorna l'elenco ordinato di tutti i distributori.
      responses:
        200:
          description: Lista dei distributori
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Distributore'
    """
    distributori_ordinati = sorted(distributori, key=lambda d: d.id)
    return jsonify([d.to_dict() for d in distributori_ordinati])


@app.route('/api/livello/provincia/<string:provincia>', methods=['GET'])
def get_livello_provincia(provincia):
    """
    Livelli per provincia
    ---
    parameters:
      - name: provincia
        in: path
        required: true
        schema:
          type: string
        description: Sigla della provincia (es. MI, RM, NA, TO)
    responses:
      200:
        description: Lista dei distributori della provincia
        content:
          application/json:
            schema:
              type: array
              items:
                $ref: '#/components/schemas/Distributore'
    """
    risultato = [d.to_dict() for d in distributori if d.provincia.lower() == provincia.lower()]
    return jsonify(risultato)


@app.route('/api/livello/distributore/<int:distributore_id>', methods=['GET'])
def get_livello_distributore(distributore_id):
    """
    Livelli per distributore
    ---
    parameters:
      - name: distributore_id
        in: path
        required: true
        schema:
          type: integer
        description: ID del distributore
    responses:
      200:
        description: Dati del distributore
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Distributore'
      404:
        description: Distributore non trovato
        content:
          application/json:
            schema:
              type: object
              properties:
                errore:
                  type: string
    """
    distributore = next((d for d in distributori if d.id == distributore_id), None)
    return jsonify(distributore.to_dict()) if distributore else (jsonify({"errore": "Distributore non trovato"}), 404)


@app.route('/api/prezzo/provincia/<string:provincia>', methods=['POST'])
def set_prezzo_provincia(provincia):
    """
    Aggiornamento prezzi per provincia
    ---
    parameters:
      - name: provincia
        in: path
        required: true
        schema:
          type: string
        description: Sigla della provincia
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              prezzo_benzina:
                type: number
                format: float
              prezzo_diesel:
                type: number
                format: float
    responses:
      200:
        description: Prezzi aggiornati
        content:
          application/json:
            schema:
              type: object
              properties:
                messaggio:
                  type: string
    """
    data = request.get_json()
    modificati = 0
    for d in distributori:
        if d.provincia.lower() == provincia.lower():
            if 'prezzo_benzina' in data and data['prezzo_benzina']:
                d.prezzo_benzina = float(data['prezzo_benzina'])
            if 'prezzo_diesel' in data and data['prezzo_diesel']:
                d.prezzo_diesel = float(data['prezzo_diesel'])
            modificati += 1
    return jsonify({"messaggio": f"Prezzi aggiornati per {modificati} distributori."})

# ==============================================================================
# 4. SCHEMI OPENAPI
# ==============================================================================

template = {
  "components": {
    "schemas": {
      "Distributore": {
        "type": "object",
        "properties": {
          "id": {"type": "integer"},
          "nome": {"type": "string"},
          "indirizzo": {"type": "string"},
          "citta": {"type": "string"},
          "provincia": {"type": "string"},
          "lat": {"type": "number", "format": "float"},
          "lon": {"type": "number", "format": "float"},
          "livello_benzina": {"type": "number"},
          "capacita_benzina": {"type": "number"},
          "livello_diesel": {"type": "number"},
          "capacita_diesel": {"type": "number"},
          "prezzo_benzina": {"type": "number", "format": "float"},
          "prezzo_diesel": {"type": "number", "format": "float"}
        }
      }
    }
  }
}

swagger = Swagger(app, template=template)

# ==============================================================================
# 5. ESECUZIONE
# ==============================================================================

if __name__ == '__main__':
    print("=====================================================")
    print("🚀 API Server in esecuzione sulla porta 5001!")
    print("📖 Documentazione disponibile su http://localhost:5001/apidocs/")
    print("=====================================================")
    app.run(host="0.0.0.0", debug=True, port=5001)
