import tkinter as tk
from tkinter import ttk
from db import inicializar_banco
from views.clientes_view import ClientesView
from views.pedidos_view import PedidosView
from views.dashboard_view import DashboardView
# nova view de produtos
try:
    from views.produtos_view import ProdutosView
    has_produtos_view = True
except Exception:
    has_produtos_view = False


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
    # Estilo específico para botões da navbar: padding maior
    style.configure("Nav.TButton", font=DEFAULT_FONT, padding=(10, 8))
    style.configure("TEntry", font=DEFAULT_FONT)
    style.configure("Treeview", font=DEFAULT_FONT, rowheight=24)
    style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

    # Estilo para a navbar (fundo branco)
    style.configure("Nav.TFrame", background="#ffffff")

    # Estado visível da navbar (usado pelo toggle)
    nav_visible = True

    # Cabeçalho com título (fundo azul, texto branco, centralizado)
    HEADER_BG = "#1e6fb3"  # azul profissional
    BTN_ACTIVE_BG = "#155785"  # tom ligeiramente mais escuro para efeito ativo
    style.configure("Header.TFrame", background=HEADER_BG)
    style.configure("Header.TLabel", background=HEADER_BG, foreground="white", font=("Segoe UI", 14, "bold"))

    header = ttk.Frame(root, style="Header.TFrame", padding=(6, 6))
    header.pack(fill="x")
    # Layout do header: grid com 3 colunas para botão (esq), título (centro) e espaço (dir)
    header.grid_columnconfigure(0, weight=0)
    header.grid_columnconfigure(1, weight=1)
    header.grid_columnconfigure(2, weight=0)

    # Animação de slide da navbar
    animating = False

    # Garante que a largura configurada seja respeitada quando animarmos
    # (o `nav` será configurado posteriormente)

    def animate_hide(step=24, delay=6):
        nonlocal animating, nav_visible
        if animating:
            return
        animating = True
        start = nav.winfo_width()

        def _step(w):
            nonlocal animating, nav_visible
            if w <= 0:
                try:
                    nav.pack_forget()
                except Exception:
                    pass
                animating = False
                nav_visible = False
                btn_toggle.config(text="☰")
                return
            nav.config(width=w)
            root.update_idletasks()
            root.after(delay, lambda: _step(max(0, w - step)))

        _step(start)

    def animate_show(step=24, delay=6):
        nonlocal animating, nav_visible
        if animating:
            return
        animating = True
        # Re-pack if necessário
        try:
            nav.pack(side="left", fill="y", before=content)
        except Exception:
            nav.pack(side="left", fill="y")
        target = nav_width

        def _step(w):
            nonlocal animating, nav_visible
            if w >= target:
                nav.config(width=target)
                animating = False
                nav_visible = True
                btn_toggle.config(text="✕")
                return
            nav.config(width=w)
            root.update_idletasks()
            root.after(delay, lambda: _step(min(target, w + step)))

        _step(0)

    # Botão hamburger para mostrar/ocultar navbar (usa símbolo comum ☰)
    def toggle_nav():
        nonlocal nav_visible
        if nav_visible:
            animate_hide()
        else:
            animate_show()

    # toggle button - usa tk.Button para permitir customização do background
    btn_toggle = tk.Button(
        header,
        text=("✕" if nav_visible else "☰"),
        bg=HEADER_BG,
        fg="white",
        activebackground=BTN_ACTIVE_BG,
        bd=0,
        highlightthickness=0,
        relief="flat",
        font=("Segoe UI", 12, "bold"),
        command=toggle_nav,
    )
    btn_toggle.grid(row=0, column=0, padx=(0, 6), pady=2, sticky="w")

    # Efeito visual de pressionamento: troca temporária de background
    btn_toggle.bind("<ButtonPress-1>", lambda e: btn_toggle.config(bg=BTN_ACTIVE_BG))
    btn_toggle.bind("<ButtonRelease-1>", lambda e: btn_toggle.config(bg=HEADER_BG))

    # Label centralizada no header (coluna 1)
    ttk.Label(header, text="Sistema de Gestão - Clientes & Pedidos", style="Header.TLabel").grid(row=0, column=1)

    # Layout principal: nav bar à esquerda + área de conteúdo
    main_frame = ttk.Frame(root)
    main_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    # Barra de navegação lateral
    nav_width = 220
    nav = ttk.Frame(main_frame, width=nav_width, style="Nav.TFrame")
    nav.pack(side="left", fill="y")
    # Garante que a largura configurada seja respeitada quando animarmos
    nav.pack_propagate(False)

    # Conteúdo principal (onde as views serão renderizadas)
    content = ttk.Frame(main_frame)
    content.pack(side="left", fill="both", expand=True)

    # Cria frames para cada view e empilha (serão levantados quando selecionados)
    frame_dashboard = ttk.Frame(content)
    frame_clientes = ttk.Frame(content)
    frame_pedidos = ttk.Frame(content)
    frame_produtos = ttk.Frame(content) if has_produtos_view else None

    frames_to_pack = [frame_dashboard, frame_clientes, frame_pedidos]
    if frame_produtos:
        frames_to_pack.append(frame_produtos)
    # Não empacotar os frames agora — iremos empacotar apenas o frame ativo
    # lista de frames usada para navegação
    frames = tuple(frames_to_pack)

    # Instancia as views dentro dos frames correspondentes
    DashboardView(frame_dashboard)
    ClientesView(frame_clientes)
    PedidosView(frame_pedidos)
    if frame_produtos:
        ProdutosView(frame_produtos)

    # Função auxiliar para trocar a view ativa: esconde as outras e mostra apenas a selecionada

    def show_frame(frame):
        for f in frames:
            if f is frame:
                # (re)empacota para garantir que esteja visível
                f.pack(fill="both", expand=True)
            else:
                # esconde
                try:
                    f.pack_forget()
                except Exception:
                    pass
        # destaque do botão ativo
        try:
            highlight_active(frame)
        except Exception:
            pass

    # Botões da nav
    # Botões com ícones (uso de emoji simples para compatibilidade)
    # Usa o estilo Nav.TButton e ancora o texto à esquerda
    btn_dash = ttk.Button(nav, text="📊 Dashboard", style="Nav.TButton", command=lambda: show_frame(frame_dashboard))
    btn_clients = ttk.Button(nav, text="👥 Clientes", style="Nav.TButton", command=lambda: show_frame(frame_clientes))
    btn_orders = ttk.Button(nav, text="🧾 Pedidos", style="Nav.TButton", command=lambda: show_frame(frame_pedidos))
    if frame_produtos:
        btn_produtos = ttk.Button(nav, text="📦 Produtos", style="Nav.TButton", command=lambda: show_frame(frame_produtos))

    # Posiciona botões (com espaçamento)
    btn_dash.pack(fill="x", pady=(12, 6), padx=12)
    btn_clients.pack(fill="x", pady=6, padx=12)
    btn_orders.pack(fill="x", pady=6, padx=12)
    if frame_produtos:
        btn_produtos.pack(fill="x", pady=6, padx=12)

    # Mantém referência aos botões para permitir destaque do ativo
    nav_buttons = {frame_dashboard: btn_dash, frame_clientes: btn_clients, frame_pedidos: btn_orders}
    if frame_produtos:
        nav_buttons[frame_produtos] = btn_produtos

    def highlight_active(frame):
        for fr, btn in nav_buttons.items():
            if fr is frame:
                btn.state(["pressed"])
            else:
                btn.state(["!pressed"])

    # Mostra dashboard por padrão
    show_frame(frame_dashboard)
    highlight_active(frame_dashboard)

    root.mainloop()


if __name__ == "__main__":
    main()
