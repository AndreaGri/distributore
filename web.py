import json
import requests
from flask import Flask, request, redirect, url_for, flash, get_flashed_messages

# URL del server API
API_URL = "http://127.0.0.1:5001/api/distributori"
API_PRICE_URL = "http://127.0.0.1:5001/api/prezzo/provincia"

# ==============================================================================
# 1. CREAZIONE DELL'APPLICAZIONE FLASK
# ==============================================================================

app = Flask(__name__)
app.secret_key = 'una_chiave_segreta_per_i_messaggi'

# ==============================================================================
# 2. ROTTE WEB (per l'interfaccia utente)
# ==============================================================================

@app.route('/', methods=['GET'])
def home():
    """Pagina principale che mostra mappa, elenco e form."""
    
    # 🌍 Chiama l'API per ottenere tutti i dati dei distributori
    try:
        response = requests.get(API_URL)
        response.raise_for_status()  # Lancia un'eccezione se la risposta non è 200 OK
        dati_distributori = response.json()
    except requests.exceptions.RequestException as e:
        flash(f"Errore nel connettersi al server API: {e}", "danger")
        dati_distributori = []

    # Prepara i dati per l'HTML
    province = sorted(list(set(d['provincia'] for d in dati_distributori)))
    
    # Genera dinamicamente le opzioni del menu a tendina per le province
    opzioni_province = "".join([f'<option value="{p}">{p}</option>' for p in province])
    
    # Genera dinamicamente la lista dei distributori
    lista_html = "".join([f'''
        <li class="list-group-item">
            <b>{d['id']}. {d['nome']} ({d['provincia']})</b><br>
            <small>
                Benzina: {d['prezzo_benzina']:.3f}€ - Liv: {d['livello_benzina']}L<br>
                Diesel: {d['prezzo_diesel']:.3f}€ - Liv: {d['livello_diesel']}L
            </small>
        </li>
    ''' for d in dati_distributori])

    # Ottieni i messaggi flash (se presenti)
    flashed_messages = get_flashed_messages(with_categories=True)
    alert_html = ""
    if flashed_messages:
        for category, message in flashed_messages:
            alert_html += f'<div class="alert alert-{category}">{message}</div>'

    # Incorpora l'HTML in una stringa
    html_content = f'''
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <title>Monitor Iperstaroil</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
        <style> #map {{ height: 600px; }} </style>
    </head>
    <body>
        <div class="container mt-4">
            <h1 class="mb-4 text-center">Dashboard Monitoraggio Iperstaroil ⛽</h1>
            {alert_html}
            <div class="row">
                <div class="col-md-8">
                    <div class="card shadow-sm">
                        <div class="card-header"><h3>Mappa Distributori</h3></div>
                        <div class="card-body"><div id="map"></div></div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card shadow-sm mb-4">
                        <div class="card-header"><h3>Cambia Prezzi per Provincia</h3></div>
                        <div class="card-body">
                            <form action="/cambia-prezzo" method="POST">
                                <div class="mb-3">
                                    <label class="form-label">Provincia</label>
                                    <select name="provincia" class="form-select">{opzioni_province}</select>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Nuovo Prezzo Benzina</label>
                                    <input type="number" step="0.001" name="prezzo_benzina" class="form-control" placeholder="es. 1.850">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Nuovo Prezzo Diesel</label>
                                    <input type="number" step="0.001" name="prezzo_diesel" class="form-control" placeholder="es. 1.750">
                                </div>
                                <button type="submit" class="btn btn-primary w-100">Applica Modifiche</button>
                            </form>
                        </div>
                    </div>
                    <div class="card shadow-sm">
                        <div class="card-header"><h3>Elenco Distributori</h3></div>
                        <div class="card-body" style="max-height: 400px; overflow-y: auto;">
                            <ul class="list-group list-group-flush">{lista_html}</ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
        <script>
            var map = L.map('map').setView([41.9, 12.5], 5.5);
            L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            }}).addTo(map);
            var distributori = {json.dumps(dati_distributori)};
            distributori.forEach(d => {{
                L.marker([d.lat, d.lon]).addTo(map)
                    .bindPopup(`<b>${{d.nome}}</b><br>Benzina: ${{d.prezzo_benzina.toFixed(3)}}€<br>Diesel: ${{d.prezzo_diesel.toFixed(3)}}€`);
            }});
        </script>
    </body>
    </html>
    '''
    return html_content

@app.route('/cambia-prezzo', methods=['POST'])
def cambia_prezzo_web():
    """Riceve i dati dal form web e chiama l'API interna per la modifica."""
    provincia = request.form.get('provincia')
    prezzo_benzina = request.form.get('prezzo_benzina')
    prezzo_diesel = request.form.get('prezzo_diesel')
    
    payload = {}
    if prezzo_benzina: payload['prezzo_benzina'] = prezzo_benzina
    if prezzo_diesel: payload['prezzo_diesel'] = prezzo_diesel

    if not payload:
        flash("Nessun nuovo prezzo inserito. Nessuna modifica effettuata.", "warning")
    else:
        try:
            # 🔄 Chiamata all'API per modificare i prezzi
            response = requests.post(f"{API_PRICE_URL}/{provincia}", json=payload)
            response.raise_for_status()
            flash(f"Prezzi per la provincia di {provincia} aggiornati con successo!", "success")
        except requests.exceptions.RequestException as e:
            flash(f"Errore nell'aggiornamento dei prezzi: {e}", "danger")

    return redirect(url_for('home'))

# ==============================================================================
# 3. ESECUZIONE DELL'APPLICAZIONE
# ==============================================================================

if __name__ == '__main__':
    print("=====================================================")
    print("🌐 Web Server in esecuzione sulla porta 5000!")
    print("🔗 Apri il browser e vai a: http://127.0.0.1:5000")
    print("=====================================================")
    app.run(debug=True, port=5000)