from flask import Flask, render_template, request, redirect, url_for, session
from calculator import Calculator
from istoric import Istoric, afiseazaIstoric, stergeIstoric
from datetime import datetime
from zoneinfo import ZoneInfo
from db_config import initialize_database
import logging

# Configurare logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'e9f3a1c4d6b7e8f9a2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7'

# Inițializeaza baza de date inainte de a deservi cereri
# Metoda pentru Flask >= 2.3
with app.app_context():
    logger.info("Initializare baza de date...")
    success = initialize_database()
    if success:
        logger.info("Baza de date calculatorios a fost initializată cu succes")
    else:
        logger.warning("Nu s-a putut initializa baza de date, se va folosi fallback-ul la fisier JSON")

def getCalculator():
    date = session.get('calculator')
    calc = Calculator()
    if date:
        calc.valCurenta = date.get("valCurenta", "0")
        calc.valAnterioara = date.get("valAnterioara")
        calc.operatie = date.get("operatie")
        calc.resetareAfisaj = date.get("resetareAfisaj", False)
        calc.miniAfisaj = date.get("miniAfisaj", "")
    return calc

def salveazaCalculator(calc):
    session['calculator'] = {
        "valCurenta": calc.valCurenta,
        "valAnterioara": calc.valAnterioara,
        "operatie": calc.operatie,
        "resetareAfisaj": calc.resetareAfisaj,
        "miniAfisaj": calc.miniAfisaj
    }

@app.route("/", methods=["GET", "POST"])
def index():
    calc = getCalculator()
    if request.method == "POST":
        valoare = request.form.get("input")
        valoareInserata = request.form.get("insert_value")
        
        if valoareInserata:
            calc.valCurenta = valoareInserata
            calc.resetareAfisaj = True
        elif valoare:
            if valoare in "0123456789":
                calc.adaugaNumar(valoare)
            elif valoare == ".":
                calc.adaugaZecimal()
            elif valoare in "+-×÷":
                calc.adaugaOperatie(valoare)
            elif valoare == "=":
                calc.egal()
            elif valoare == "AC":
                calc.sterge()
            elif valoare == "+/-":
                calc.schimbaSemn()
            elif valoare == "%":
                calc.procente()
        salveazaCalculator(calc)
        return redirect(url_for("index"))
    
    oraCurenta = datetime.now(ZoneInfo("Europe/Bucharest")).strftime("%H:%M")
    modIntunecat = session.get("modIntunecat", False)
    istoricObj = Istoric()  # Folosim clasa Istoric
    
    return render_template("index.html", 
                       display=calc.actualizeazaAfisaj(),
                       miniDisplay=calc.getMiniAfisaj(),
                       history=istoricObj.listaTot(),
                       time=oraCurenta,
                       darkMode=modIntunecat)

@app.route("/schimba_tema", endpoint="schimbaTema")
def schimbaTema():
    modIntunecat = session.get("modIntunecat", False)
    session["modIntunecat"] = not modIntunecat
    return redirect(url_for("index"))

@app.route("/istoric", endpoint="istoric")
def istoric():
    """Route pentru afisarea paginii de istoric"""
    calc = getCalculator()
    modIntunecat = session.get("modIntunecat", False)
    istoricObj = Istoric()
    return render_template(
        "istoric.html",
        history=istoricObj.listaTot(),
        back_url=url_for('index'),
        darkMode=modIntunecat
    )

@app.route("/goleste_istoric", endpoint="goleste_istoric")
def stergeIstoricul():
    """Route pentru stergerea istoricului"""
    return stergeIstoric()

@app.route("/goleste_istoric_ajax", endpoint="goleste_istoric_ajax", methods=["POST"])
def golestIstoricAjax():
    """Route pentru stergerea istoricului cu AJAX"""
    istoricObj = Istoric()
    istoricObj.stergeTot()
    return "", 204

@app.route("/foloseste/<int:index>", endpoint="folosesteDinIstoric")
def folosesteDinIstoric(index):
    """Route pentru folosirea unei valori din istoric"""
    istoricObj = Istoric()
    try:
        intrare = istoricObj.getIntrare(index)
        if intrare:
            calc = getCalculator()
            calc.valCurenta = intrare["rezultat"]
            calc.resetareAfisaj = True
            salveazaCalculator(calc)
    except IndexError:
        pass
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True) 