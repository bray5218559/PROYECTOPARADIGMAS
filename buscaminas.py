import tkinter as tk
import random
from tkinter import messagebox

# Clase base genérica
class Juego:
    def __init__(self, titulo="Juego"):
        self.titulo = titulo

    def iniciar(self):
        print(f"Iniciando {self.titulo}...")

    def fin_del_juego(self, victoria):
        # Método genérico (será sobrescrito)
        if victoria:
            print("Ganaste el juego")
        else:
            print("Perdiste el juego")


# Clase intermedia con tablero
class JuegoConTablero(Juego):
    def __init__(self, filas, columnas, titulo="Juego con Tablero"):
        super().__init__(titulo)
        self._filas = filas
        self._columnas = columnas
        self._tablero = [[0 for _ in range(columnas)] for _ in range(filas)]

    def crear_tablero(self):
        # Método genérico para inicializar un tablero
        self._tablero = [[0 for _ in range(self._columnas)] for _ in range(self._filas)]

    def mostrar_tablero(self):
        for fila in self._tablero:
            print(fila)


# Clase específica del Buscaminas
class Buscaminas(JuegoConTablero):
    def __init__(self, master, filas=8, columnas=8, minas=10):
        super().__init__(filas, columnas, titulo="Buscaminas 🎮")
        self.master = master
        self._minas = minas
        self._botones = {}
        self._colores = {
            1: "blue", 2: "green", 3: "red", 4: "purple",
            5: "maroon", 6: "turquoise", 7: "black", 8: "gray"
        }

        self._colocar_minas()
        self._contar_minas()
        self._crear_interfaz()

    # ----------------- Métodos privados -----------------
    def _colocar_minas(self):
        minas_colocadas = 0
        while minas_colocadas < self._minas:
            f = random.randint(0, self._filas - 1)
            c = random.randint(0, self._columnas - 1)
            if self._tablero[f][c] != "M":
                self._tablero[f][c] = "M"
                minas_colocadas += 1

    def _contar_minas(self):
        for f in range(self._filas):
            for c in range(self._columnas):
                if self._tablero[f][c] == "M":
                    continue
                minas_cerca = 0
                for i in range(max(0, f-1), min(self._filas, f+2)):
                    for j in range(max(0, c-1), min(self._columnas, c+2)):
                        if self._tablero[i][j] == "M":
                            minas_cerca += 1
                self._tablero[f][c] = minas_cerca

    def _crear_interfaz(self):
        frame = tk.Frame(self.master, bg="#d9d9d9")
        frame.pack(padx=10, pady=10)

        for f in range(self._filas):
            for c in range(self._columnas):
                b = tk.Button(frame, width=4, height=2, font=("Arial", 12, "bold"),
                              bg="#e6e6e6", relief="raised",
                              command=lambda f=f, c=c: self._revelar(f, c))
                b.grid(row=f, column=c, padx=1, pady=1)
                self._botones[(f, c)] = b

    # ----------------- Lógica del juego -----------------
    def _revelar(self, f, c):
        boton = self._botones[(f, c)]
        if self._tablero[f][c] == "M":
            boton.config(text="💣", bg="red", disabledforeground="black")
            self.fin_del_juego(False)  # polimorfismo
        else:
            self._mostrar_celda(f, c)
            if self._verificar_victoria():
                self.fin_del_juego(True)

    def _mostrar_celda(self, f, c):
        boton = self._botones[(f, c)]
        if boton["state"] != "normal":
            return
        valor = self._tablero[f][c]
        boton.config(relief="sunken", state="disabled", bg="#cccccc")
        if valor > 0:
            boton.config(text=str(valor), disabledforeground=self._colores.get(valor, "black"))
        else:
            for i in range(max(0, f-1), min(self._filas, f+2)):
                for j in range(max(0, c-1), min(self._columnas, c+2)):
                    if (i, j) != (f, c):
                        self._mostrar_celda(i, j)

    def _verificar_victoria(self):
        for f in range(self._filas):
            for c in range(self._columnas):
                if self._tablero[f][c] != "M" and self._botones[(f, c)]["state"] == "normal":
                    return False
        return True

    # ----------------- Polimorfismo -----------------
    def fin_del_juego(self, victoria):
        for f in range(self._filas):
            for c in range(self._columnas):
                if self._tablero[f][c] == "M":
                    self._botones[(f, c)].config(text="💣", bg="#ff6666")
        if victoria:
            messagebox.showinfo("Buscaminas", "¡Felicidades, ganaste! 🎉")
        else:
            messagebox.showinfo("Buscaminas", "💥 ¡BOOM! Perdiste 😢")
        self.master.destroy()


# ----------------- Ejecutar juego -----------------
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Buscaminas 🎮")
    root.config(bg="#d9d9d9")
    juego = Buscaminas(root, filas=10, columnas=10, minas=15)
    root.mainloop()

