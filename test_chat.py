import requests
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "http://127.0.0.1:5001"

# =============================================================================
# FUNZIONI DI SUPPORTO
# =============================================================================

def pretty_print(resp):
    try:
        print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
    except Exception:
        print("Risposta non JSON:", resp.text)


# =============================================================================
# TEST UNITARI (stile pytest, ma funzionano anche con esecuzione normale)
# =============================================================================

def test_get_distributori():
    print("\n=== Test: GET /api/distributori ===")
    r = requests.get(f"{BASE_URL}/api/distributori")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) > 0
    print("OK - ricevuti", len(data), "distributori")
    pretty_print(r)


def test_get_livello_provincia():
    print("\n=== Test: GET /api/livello/provincia/MI ===")
    r = requests.get(f"{BASE_URL}/api/livello/provincia/MI")
    assert r.status_code == 200
    data = r.json()
    assert all(d["provincia"].lower() == "mi" for d in data)
    print("OK - provincia MI ha", len(data), "distributori")
    pretty_print(r)


def test_get_livello_distributore():
    print("\n=== Test: GET /api/livello/distributore/1 ===")
    r = requests.get(f"{BASE_URL}/api/livello/distributore/1")
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == 1
    print("OK - distributore trovato:", data["nome"])
    pretty_print(r)


def test_get_livello_distributore_non_esiste():
    print("\n=== Test: GET /api/livello/distributore/999 ===")
    r = requests.get(f"{BASE_URL}/api/livello/distributore/999")
    assert r.status_code == 404
    data = r.json()
    assert "errore" in data
    print("OK - messaggio di errore ricevuto:", data["errore"])


def test_set_prezzo_provincia():
    print("\n=== Test: POST /api/prezzo/provincia/RM ===")
    nuovo_prezzo = {"prezzo_benzina": 1.99, "prezzo_diesel": 1.89}
    r = requests.post(f"{BASE_URL}/api/prezzo/provincia/RM", json=nuovo_prezzo)
    assert r.status_code == 200
    msg = r.json()
    assert "aggiornati" in msg["messaggio"]

    # Verifica che il prezzo sia stato aggiornato
    r2 = requests.get(f"{BASE_URL}/api/livello/provincia/RM")
    assert r2.status_code == 200
    data = r2.json()
    assert all(d["prezzo_benzina"] == 1.99 for d in data)
    assert all(d["prezzo_diesel"] == 1.89 for d in data)
    print("OK - prezzi aggiornati per provincia RM")
    pretty_print(r2)


# =============================================================================
# STRESS TEST
# =============================================================================

def call_endpoint(endpoint):
    try:
        r = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
        return r.status_code
    except Exception as e:
        return str(e)


def stress_test(endpoint="/api/distributori", num_requests=200, workers=20):
    print(f"\n=== Stress test su {endpoint} ===")
    print(f"Invio {num_requests} richieste con {workers} thread...")
    start = time.time()
    results = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(call_endpoint, endpoint) for _ in range(num_requests)]
        for f in as_completed(futures):
            results.append(f.result())
    durata = time.time() - start
    ok = results.count(200)
    fail = len(results) - ok
    print(f"✅ Successi: {ok} | ❌ Falliti: {fail}")
    print(f"Tempo totale: {durata:.2f} sec | RPS ~ {num_requests/durata:.2f}")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    # Esegui i test unitari
    test_get_distributori()
    test_get_livello_provincia()
    test_get_livello_distributore()
    test_get_livello_distributore_non_esiste()
    test_set_prezzo_provincia()

    # Esegui stress test
    stress_test("/api/distributori", num_requests=200, workers=20)
    stress_test("/api/livello/provincia/MI", num_requests=200, workers=20)
