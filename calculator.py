class Calculator:
    def __init__(self):
        self.valCurenta = "0"          # Reprezinta valoarea afisata
        self.valAnterioara = None      # Pastreaza valoarea anterioara (ca sir)
        self.operatie = None          # Operatia ("+", "-", "×", "÷")
        self.resetareAfisaj = False
        self.istoric = []             # Pentru compatibilitate, nu mai este folosit direct
        self.miniAfisaj = ""          # Textul mic de afisaj pentru operatii partiale
        
        from istoric import Istoric
        self.managerIstoric = Istoric()

    def actualizeazaAfisaj(self):
        return self.valCurenta

    def sterge(self):
        self.valCurenta = "0"
        self.valAnterioara = None
        self.operatie = None
        self.resetareAfisaj = False
        self.miniAfisaj = ""  # Sterge ecran

    def adaugaNumar(self, numar: str):
        if self.resetareAfisaj or self.valCurenta == "Error":
            self.valCurenta = numar
            self.resetareAfisaj = False
        else:
            self.valCurenta = numar if self.valCurenta == "0" else self.valCurenta + numar

    def adaugaZecimal(self):
        if "." not in self.valCurenta:
            self.valCurenta += "."

    def adaugaOperatie(self, op: str):
        if self.valAnterioara is None:
            self.valAnterioara = self.valCurenta
            self.miniAfisaj = self.valCurenta + " " + op
        elif self.operatie:
            rezultat = self.calculeaza()
            self.valAnterioara = rezultat
            self.miniAfisaj = rezultat + " " + op
        else:
            self.miniAfisaj = self.valCurenta + " " + op  # Fallback
        self.operatie = op
        self.resetareAfisaj = True
        self.valCurenta = ""

    def calculeaza(self):
        try:
            anterior = float(self.valAnterioara)
            curent = float(self.valCurenta)
        except (TypeError, ValueError):
            return "0"
        rezultat = None
        if self.operatie == "+":
            rezultat = anterior + curent
        elif self.operatie == "-":
            rezultat = anterior - curent
        elif self.operatie == "×":
            rezultat = anterior * curent
        elif self.operatie == "÷":
            if curent == 0:
                return "Error"
            rezultat = anterior / curent
        else:
            return "0"
        if rezultat is not None:
            rezultat = str(int(rezultat)) if rezultat.is_integer() else str(rezultat)
        return rezultat

    def egal(self):
        if self.operatie:
            rezultat = self.calculeaza()
            expresie = f"{self.valAnterioara} {self.operatie} {self.valCurenta}"
            self.adaugaIstoric(expresie, rezultat)
            self.valCurenta = rezultat
        self.valAnterioara = None
        self.operatie = None
        self.resetareAfisaj = True
        self.miniAfisaj = ""

    def schimbaSemn(self):
        try:
            valoare = float(self.valCurenta)
            valoare *= -1
            self.valCurenta = str(int(valoare)) if valoare.is_integer() else str(valoare)
        except ValueError:
            self.valCurenta = "Error"

    def procente(self):
        try:
            valoare = float(self.valCurenta) / 100
            self.valCurenta = str(int(valoare)) if valoare.is_integer() else str(valoare)
        except ValueError:
            self.valCurenta = "Error"

    def adaugaIstoric(self, expresie: str, rezultat: str):
        # Metoda pentru compatibilitate
        try:
            from istoric import Istoric
            managerIst = Istoric()
            managerIst.adauga(expresie, rezultat)
        except ImportError:
            # Fallback la metoda veche
            self.istoric.append({"expresie": expresie, "rezultat": rezultat})

    def getIstoric(self):
        # Metoda pentru compatibilitate
        try:
            from istoric import Istoric
            managerIst = Istoric()
            return managerIst.listaTot()
        except ImportError:
            # Fallback la metoda veche
            return [f"{item['expresie']} = {item['rezultat']}" for item in self.istoric]

    def folosesteDinIstoric(self, index: int):
        try:
            from istoric import Istoric
            managerIst = Istoric()
            try:
                intrare = managerIst.getIntrare(index)
                self.valCurenta = intrare["rezultat"]
                self.resetareAfisaj = True
            except IndexError:
                pass
        except ImportError:
            # Fallback la metoda veche
            if 0 <= index < len(self.istoric):
                self.valCurenta = self.istoric[index]["rezultat"]
                self.resetareAfisaj = True

    def golestIstoric(self):
        try:
            from istoric import Istoric
            managerIst = Istoric()
            managerIst.stergeTot()
        except ImportError:
            # Fallback la metoda veche
            self.istoric = []

    def getMiniAfisaj(self):
        return self.miniAfisaj


if __name__ == '__main__':
    calc = Calculator()

    calc.adaugaNumar("5")
    calc.adaugaOperatie("+")
    calc.adaugaNumar("3")
    calc.egal()
    print("Afișaj:", calc.actualizeazaAfisaj())
    print("Istoric:", calc.getIstoric())

    calc.adaugaOperatie("÷")
    calc.adaugaNumar("0")
    calc.egal()
    print("Afișaj:", calc.actualizeazaAfisaj())

    calc.sterge()
    calc.adaugaNumar("9")
    calc.adaugaZecimal()
    calc.adaugaNumar("5")
    calc.adaugaOperatie("×")
    calc.adaugaNumar("2")
    calc.egal()
    print("Afișaj:", calc.actualizeazaAfisaj())
    print("Istoric:", calc.getIstoric()) 