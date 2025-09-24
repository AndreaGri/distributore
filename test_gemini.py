import requests
import json
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor

# ==============================================================================
# 1. CONFIGURAZIONE
# ==============================================================================

# URL base del tuo server API.
BASE_URL = "http://127.0.0.1:5001"

# ==============================================================================
# 2. FUNZIONI DI TEST MODIFICATE
# ==============================================================================

def test_single_endpoint(endpoint):
    """Esegue un singolo test di un endpoint senza mostrare i dettagli della risposta."""
    try:
        if isinstance(endpoint, tuple):
            url, method, data = endpoint
            if method.upper() == 'GET':
                response = requests.get(url, timeout=5)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data, timeout=5)
        else:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
        
        response.raise_for_status() # Lancia un'eccezione per i codici di stato HTTP 4xx/5xx
        return "✅ Successo"

    except requests.exceptions.HTTPError as errh:
        return f"❌ Errore HTTP: {errh}"
    except requests.exceptions.ConnectionError as errc:
        return f"❌ Errore di Connessione: Assicurati che il server API sia in esecuzione. Errore: {errc}"
    except requests.exceptions.Timeout as errt:
        return "❌ Timeout: La richiesta è scaduta."
    except Exception as err:
        return f"❌ Si è verificato un errore generico: {err}"

async def stress_test_async(endpoint, num_requests, num_workers=10):
    """Esegue uno stress test asincrono su un endpoint e mostra solo il risultato finale."""
    print(f"\n--- ⏳ Avvio Stress Test: {endpoint} con {num_requests} richieste ---")
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(executor, test_single_endpoint, endpoint)
            for _ in range(num_requests)
        ]
        results = await asyncio.gather(*tasks)

    elapsed_time = time.time() - start_time
    success_count = results.count("✅ Successo")
    error_count = num_requests - success_count
    
    print("\n--- ✅ Stress Test Completato ---")
    print(f"Tempo totale: {elapsed_time:.2f}s")
    print(f"Richieste al secondo: {num_requests / elapsed_time:.2f}")
    print(f"Successi: {success_count}")
    print(f"Errori: {error_count}")
    if error_count > 0:
        print("\n--- Dettaglio Errori ---")
        for res in set(results):
            if not res.startswith("✅"):
                print(res)

# ==============================================================================
# 3. INTERFACCIA UTENTE E MENU
# ==============================================================================

def main():
    """Funzione principale per l'interfaccia utente."""
    while True:
        print("\n--- Scegli un'opzione di test ---")
        print("1. Testare tutti gli endpoint (successo atteso)")
        print("2. Testare gli endpoint con errori attesi (es. ID non trovato)")
        print("3. Eseguire uno stress test")
        print("4. Uscire")
        
        choice = input("Inserisci la tua scelta (1-4): ")
        
        if choice == '1':
            print("\n--- Eseguo i test di successo ---")
            test_endpoints = [
                "/api/distributori",
                "/api/livello/provincia/MI",
                "/api/livello/distributore/1",
                (f"{BASE_URL}/api/prezzo/provincia/MI", "POST", {"prezzo_benzina": 1.800})
            ]
            for endpoint in test_endpoints:
                result = test_single_endpoint(endpoint)
                print(f"Endpoint: {'/'.join(endpoint[0].split('/')[3:]) if isinstance(endpoint, tuple) else endpoint} -> {result}")
                
        elif choice == '2':
            print("\n--- Eseguo i test di errore ---")
            test_endpoints_errors = [
                "/api/distributori/rotta_sbagliata",
                "/api/livello/provincia/XYZ",
                "/api/livello/distributore/999"
            ]
            for endpoint in test_endpoints_errors:
                result = test_single_endpoint(endpoint)
                print(f"Endpoint: {endpoint} -> {result}")

        elif choice == '3':
            endpoint_stress = input("Inserisci l'endpoint da stressare (es. /api/distributori): ")
            try:
                num_reqs = int(input("Quante richieste vuoi inviare? "))
                asyncio.run(stress_test_async(endpoint_stress, num_reqs))
            except ValueError:
                print("Inserisci un numero valido.")

        elif choice == '4':
            print("Uscita...")
            break
            
        else:
            print("Scelta non valida. Riprova.")

# ==============================================================================
# 4. ESECUZIONE
# ==============================================================================

if __name__ == '__main__':
    main()