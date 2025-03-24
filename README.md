# Calculator iOS

O aplicatie web Flask care reproduce aspectul si functionalitatea unui calculator iOS, cu istoric stocat in baza de date MySQL

## Cerinte

- Python 3.7 sau mai recent
- MySQL 5.7 sau mai recent
- Librariile Python specificate în `librarii.txt`

## Instalare

1. Clonați repository-ul:
```bash
git clone https://github.com/dca-online/calculator-ios-flask.git
```

2. Instalati dependentele:
```bash
pip install -r requirements.txt
```

3. Configurati baza de date:
   - Creati o baza de date MySQL `calculatorios`
   - Dacă doriti să modificati credentialele de conectare, editati fisierul `db_config.py`

```python
# Configurare conexiune MySQL
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'port': port, #TREBUIE SA FIE INT FARA APOSTROAFE
    'password': '',
    'database': 'calculatorios'
}
```

## Pornirea aplicatiei

```bash
flask run
```

Aplicația va fi disponibilă la adresa [http://localhost:5000](http://localhost:5000)

## Utilizare

- Interfata simuleaza un calculator iOS
- Calculele sunt salvate automat in istoric
- Accesati istoricul apasand butonul "Istoric" din partea de sus
- Puteti sterge istoricul din pagina de istoric

## Functionalitati

- Operatii aritmetice de baza (adunare, scădere, inmultire, impartire)
- Procente, schimbare semn
- Istoric al calculelor
- Interfata in stil iOS cu suport pentru dark mode
- Stocare persistenta a istoricului in baza de date MySQL

## Integrare cu MySQL

Aplicatia foloseste MySQL Workbench pentru a stoca istoricul calculelor. Structura tabelului este:

```sql
CREATE TABLE istoric (
    id INT AUTO_INCREMENT PRIMARY KEY,
    expresie VARCHAR(255) NOT NULL,
    rezultat VARCHAR(255) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

In caz ca baza de date MySQL nu este disponibila, aplicatia va folosi un fallback la un fisier JSON pentru a stoca istoricul

## Important

- Trebuie sa aveti MySQL instalat si configurat corect
- Daca MySQL nu este disponibil, se va folosi stocarea in fisier JSON

