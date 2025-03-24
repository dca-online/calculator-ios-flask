
#Config pentru conexiunea la baza de date MySQL

import mysql.connector
from mysql.connector import Error
import logging
import sys

# Config logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Config conexiune MySQL
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'parola1234',
    'database': 'calculatorios'
}

def get_db_connection():
    """
    Creeaza si returneaza o conexiune la baza de date
    Returnează None daca conexiunea da fail
    """
    try:
        # Test DB fara credentiale
        test_config = DB_CONFIG.copy()
        if 'database' in test_config:
            del test_config['database']
        
        logger.info(f"Testare conexiune de baza: {test_config}")
        test_connection = mysql.connector.connect(**test_config)
        
        if test_connection.is_connected():
            logger.info("Conexiune reusita, încercare cu baza de date specificata")
            test_connection.close()
            
            # Test cu db
            connection = mysql.connector.connect(**DB_CONFIG)
            if connection.is_connected():
                logger.info("Conectat cu succes la baza de date MySQL")
                
                # Test operatii
                cursor = connection.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                cursor.close()
                
                return connection
        
    except Error as e:
        logger.error(f"Eroare la conectarea la MySQL: {e}")
        # Info log detaliat
        logger.error(f"Parametrii conexiune: host={DB_CONFIG['host']}, port={DB_CONFIG['port']}, user={DB_CONFIG['user']}, database={DB_CONFIG.get('database', 'None')}")
    
    return None

def initialize_database():
    """
    Initializeaza baza de date si creeaza tabelele necesare daca nu exista
    """
    connection = None
    try:
        # Test conexiune fara db pt verificare, daca exista db creat
        initial_config = DB_CONFIG.copy()
        if 'database' in initial_config:
            del initial_config['database']
        
        logger.info(f"Incercare de conectare fara selectarea bazei de date: {initial_config}")
        try:
            initial_connection = mysql.connector.connect(**initial_config)
        except Error as e:
            logger.error(f"Eroare la conectarea initială: {e}")
            logger.error("Verifica daca serverul MySQL merge si user + pass sunt corecte")
            return False
        
        if initial_connection.is_connected():
            cursor = initial_connection.cursor()
            
            # Creaza db daca nu exista
            db_name = DB_CONFIG['database']
            logger.info(f"Creare baza de date daca nu exista: {db_name}")
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            logger.info(f"Baza de date {db_name} creata sau exista deja")
            
            # Inchide conex initiala
            cursor.close()
            initial_connection.close()
            
            # Conex cu db selectata
            logger.info("Reincercare conectare cu baza de date selectata")
            connection = get_db_connection()
            if connection is None:
                logger.error("Nu s-a putut conecta la baza de date dupa creare")
                return False
            
            cursor = connection.cursor()
            cursor.execute(f"USE {db_name}")
            
            # Creaza tabel
            logger.info("Creare tabel pt istoric dacă nu exista")
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS istoric (
                id INT AUTO_INCREMENT PRIMARY KEY,
                expresie VARCHAR(255) NOT NULL,
                rezultat VARCHAR(255) NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            connection.commit()
            logger.info("Baza de date initializata cu succes")
            return True
        else:
            logger.error("Nu s-a putut realiza conexiunea")
            return False
        
    except Error as e:
        logger.error(f"Eroare la initializarea bazei de date: {e}")
        return False
    except Exception as e:
        logger.error(f"Excepție neasteptata: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close() 