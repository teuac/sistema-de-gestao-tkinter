import tkinter as tk
from tkinter import ttk
from db import inicializar_banco
from views.clientes_view import ClientesView
from views.pedidos_view import PedidosView
from views.dashboard_view import DashboardView


def main():
    inicializar_banco()  # Garante que o banco esteja pronto

    root = tk.Tk()
    root.title("Gestão de Clientes e Pedidos")
    root.geometry("1000x650")

    # --- Tema e estilo global ---
    style = ttk.Style()
    # Tenta um tema moderno quando disponível
    for t in ("vista", "clam", "default"):
        try:
            style.theme_use(t)
            break
        except Exception:
            continue

    DEFAULT_FONT = ("Segoe UI", 10)
    style.configure("TLabel", font=DEFAULT_FONT)
    style.configure("TButton", font=DEFAULT_FONT, padding=6)
    style.configure("TEntry", font=DEFAULT_FONT)
    style.configure("Treeview", font=DEFAULT_FONT, rowheight=24)
    style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

    # Cabeçalho com título (fundo azul, texto branco, centralizado)
    HEADER_BG = "#1e6fb3"  # azul profissional
    style.configure("Header.TFrame", background=HEADER_BG)
    style.configure("Header.TLabel", background=HEADER_BG, foreground="white", font=("Segoe UI", 14, "bold"))

    header = ttk.Frame(root, style="Header.TFrame", padding=(12, 8))
    header.pack(fill="x")
    # Label centralizada no header
    ttk.Label(header, text="Sistema de Gestão - Clientes & Pedidos", style="Header.TLabel").pack(expand=True)

    # Notebook (abas)
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    # Abas
    frame_dashboard = ttk.Frame(notebook)
    frame_clientes = ttk.Frame(notebook)
    frame_pedidos = ttk.Frame(notebook)

    notebook.add(frame_dashboard, text="Dashboard")
    notebook.add(frame_clientes, text="Clientes")
    notebook.add(frame_pedidos, text="Pedidos")

    # Inserir as views dentro das abas
    DashboardView(frame_dashboard)
    ClientesView(frame_clientes)
    PedidosView(frame_pedidos)

    root.mainloop()


if __name__ == "__main__":
    main()
