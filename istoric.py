import json
import os
from flask import session, redirect, url_for, render_template
from typing import List, Dict, Any
from mysql.connector import Error
import logging
from db_config import get_db_connection

# Configurare logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Istoric:
    def __init__(self):
        # Pastram compatibilitatea pentru fallback in JSON
        self.caleFisier = "istoric.json"
        self._dateIstoric = []
        self._incarcaDate()
    
    def _incarcaDate(self) -> None:
        """Incarca istoricul din baza de date MySQL"""
        self._dateIstoric = []
        connection = None
        try:
            connection = get_db_connection()
            if connection is None:
                logger.warning("Fallback la fisierul JSON pentru istoric")
                self._dateIstoric = self._incarcaFisier()
                return
            
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT expresie, rezultat FROM istoric ORDER BY timestamp DESC")
            results = cursor.fetchall()
            
            if results:
                self._dateIstoric = results
            
        except Error as e:
            logger.error(f"Eroare la incarcarea istoricului din MySQL: {e}")
            self._dateIstoric = self._incarcaFisier()  # Fallback la JSON
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()
    
    def _incarcaFisier(self) -> List[Dict[str, str]]:
        """Fallback: Incarca istoricul din fisier dacă baza de date nu e disponibila"""
        if os.path.exists(self.caleFisier):
            try:
                with open(self.caleFisier, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []
    
    def salveazaFisier(self) -> None:
        """Fallback: Salveaza istoricul în fisier daca baza de date nu e disponibila"""
        try:
            with open(self.caleFisier, "w") as f:
                json.dump(self._dateIstoric, f, indent=4)
        except Exception as e:
            logger.error(f"Eroare la salvarea istoricului în fisier: {e}")
    
    def adauga(self, expresie: str, rezultat: str) -> None:
        """Adauga o intrare noua în istoric"""
        connection = None
        try:
            connection = get_db_connection()
            if connection is None:
                # Fallback la JSON
                self._dateIstoric.append({"expresie": expresie, "rezultat": rezultat})
                self.salveazaFisier()
                return
            
            cursor = connection.cursor()
            query = "INSERT INTO istoric (expresie, rezultat) VALUES (%s, %s)"
            cursor.execute(query, (expresie, rezultat))
            connection.commit()
            
            # Actualizam cache
            self._dateIstoric.insert(0, {"expresie": expresie, "rezultat": rezultat})
            
        except Error as e:
            logger.error(f"Eroare la adăugarea în istoric: {e}")
            # Fallback la JSON
            self._dateIstoric.append({"expresie": expresie, "rezultat": rezultat})
            self.salveazaFisier()
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()
    
    def listaTot(self) -> List[str]:
        """Return tot istoricul ca lista de strings"""
        # Refresh la datele din baza de date
        self._incarcaDate()
        return [f"{item['expresie']} = {item['rezultat']}" for item in self._dateIstoric]
    
    def getIstoricRaw(self) -> List[Dict[str, str]]:
        """Return istoric ca lista de dictionare"""
        # Refresh la datele din baza de date
        self._incarcaDate()
        return self._dateIstoric
    
    def stergeTot(self) -> None:
        """Sterge tot istoricul"""
        connection = None
        try:
            connection = get_db_connection()
            if connection is None:
                # Fallback la JSON
                self._dateIstoric = []
                self.salveazaFisier()
                return
            
            cursor = connection.cursor()
            cursor.execute("TRUNCATE TABLE istoric")
            connection.commit()
            
            # Actualizam cache
            self._dateIstoric = []
            
        except Error as e:
            logger.error(f"Eroare la stergerea istoricului: {e}")
            # Fallback la JSON
            self._dateIstoric = []
            self.salveazaFisier()
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()
    
    def getIntrare(self, index: int) -> Dict[str, str]:
        """Return o intrare specifica din istoric"""
        # Refresh la datele din baza de date
        self._incarcaDate()
        if 0 <= index < len(self._dateIstoric):
            return self._dateIstoric[index]
        raise IndexError("Index in afara intervalului")
    
    def numarIntrari(self) -> int:
        """Return numarul de intrari din istoric"""
        # Refresh la datele din baza de date
        self._incarcaDate()
        return len(self._dateIstoric)

# Functii de route pentru Flask

def afiseazaIstoric(calc, urlInapoi="/"):
    """Template pentru istoric"""
    istoricObj = Istoric()
    return render_template(
        "istoric.html",
        history=istoricObj.listaTot(),
        back_url=urlInapoi,
        darkMode=session.get("modIntunecat", False)
    )

def stergeIstoric():
    """Sterge tot istoricul"""
    istoricObj = Istoric()
    istoricObj.stergeTot()
    return redirect(url_for("index"))

def getRezultat(index):
    """Foloseste rezultatul unei operatii anterioare."""
    istoricObj = Istoric()
    try:
        intrare = istoricObj.getIntrare(index)
        if intrare:
            return intrare["rezultat"]
    except IndexError:
        pass
    return "0" 