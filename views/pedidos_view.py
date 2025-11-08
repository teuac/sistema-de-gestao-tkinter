import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
from models import Cliente, Pedido, ItemPedido, Produto
from datetime import datetime


class PedidosView(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack(fill="both", expand=True, padx=12, pady=8)
        self.criar_widgets()
        self.listar_pedidos()

    # ===========================================================
    # Interface principal
    # ===========================================================
    def criar_widgets(self):
        # Pesquisa
        frame_pesquisa = ttk.Frame(self)
        frame_pesquisa.grid(row=0, column=0, columnspan=2, sticky="ew", pady=6)
        ttk.Label(frame_pesquisa, text="Pesquisar por Cliente:").pack(side="left", padx=6)
        self.entry_pesquisa = ttk.Entry(frame_pesquisa, width=34)
        self.entry_pesquisa.pack(side="left", padx=6)
        ttk.Button(frame_pesquisa, text="Pesquisar", command=self.pesquisar_pedido).pack(side="left", padx=6)
        ttk.Button(frame_pesquisa, text="Limpar", command=self.listar_pedidos).pack(side="left", padx=6)

        # Botões principais
        frame_botoes = ttk.Frame(self)
        frame_botoes.grid(row=1, column=0, columnspan=2, pady=10)
        ttk.Button(frame_botoes, text="Novo Pedido", command=self.abrir_modal_pedido, width=16).grid(row=0, column=0, padx=6)
        ttk.Button(frame_botoes, text="Excluir Pedido", command=self.excluir_pedido, width=16).grid(row=0, column=1, padx=6)

        # Treeview de pedidos
        colunas = ("id", "cliente", "data", "total")
        self.tree = ttk.Treeview(self, columns=colunas, show="headings")
        for col in colunas:
            self.tree.heading(col, text=col.capitalize())
        self.tree.column("id", width=60, anchor="center")
        self.tree.column("cliente", width=300)
        self.tree.column("data", width=120, anchor="center")
        self.tree.column("total", width=120, anchor="e")
        self.tree.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=6, pady=6)

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=2, column=2, sticky="ns", pady=6)

        # Itens do pedido selecionado
        ttk.Label(self, text="Itens do Pedido Selecionado").grid(row=3, column=0, columnspan=2, pady=10)

        colunas_itens = ("id", "produto", "quantidade", "preco_unit", "subtotal")
        # agora armazenamos também produto_id (oculto) para referenciar produtos cadastrados
        colunas_itens = ("produto_id", "produto", "quantidade", "preco_unit", "subtotal")
        self.tree_itens = ttk.Treeview(self, columns=colunas_itens, show="headings", height=7)
        for col in colunas_itens:
            self.tree_itens.heading(col, text=col.capitalize())
        # Esconde coluna produto_id (mantém referência)
        self.tree_itens.column("produto_id", width=0, stretch=False)
        self.tree_itens.column("produto", width=280)
        self.tree_itens.column("quantidade", width=100, anchor="center")
        self.tree_itens.column("preco_unit", width=120, anchor="e")
        self.tree_itens.column("subtotal", width=120, anchor="e")
        self.tree_itens.grid(row=4, column=0, columnspan=2, padx=6, pady=6, sticky="nsew")

        self.tree.bind("<<TreeviewSelect>>", lambda e: self.carregar_itens_pedido())

        self.grid_rowconfigure(4, weight=1)
        self.grid_columnconfigure(1, weight=1)

    # ===========================================================
    # Funções auxiliares
    # ===========================================================
    def carregar_clientes(self):
        clientes = Cliente.listar()
        return [f"{c[0]} - {c[1]}" for c in clientes]

    def carregar_produtos(self):
        produtos = Produto.listar()
        # formato: "id - nome - preço"
        return [f"{p[0]} - {p[1]} - {p[2]:.2f}" for p in produtos]

    def validar_data(self, data):
        try:
            datetime.strptime(data, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    # ===========================================================
    # CRUD de Pedidos
    # ===========================================================
    def listar_pedidos(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        pedidos = Pedido.listar()
        clientes = {c[0]: c[1] for c in Cliente.listar()}
        for p in pedidos:
            nome_cliente = clientes.get(p[1], "Desconhecido")
            self.tree.insert("", "end", values=(p[0], nome_cliente, p[2], f"{p[3]:.2f}"))

    def pesquisar_pedido(self):
        termo = self.entry_pesquisa.get().strip().lower()
        for i in self.tree.get_children():
            self.tree.delete(i)
        pedidos = Pedido.listar()
        clientes = {c[0]: c[1] for c in Cliente.listar()}
        for p in pedidos:
            nome_cliente = clientes.get(p[1], "")
            if termo in nome_cliente.lower():
                self.tree.insert("", "end", values=(p[0], nome_cliente, p[2], f"{p[3]:.2f}"))

    def excluir_pedido(self):
        selec = self.tree.selection()
        if not selec:
            messagebox.showwarning("Aviso", "Selecione um pedido para excluir.")
            return
        pedido_id = self.tree.item(selec)["values"][0]
        if messagebox.askyesno("Confirmação", "Deseja excluir este pedido?"):
            Pedido.deletar(pedido_id)
            self.listar_pedidos()
            self.tree_itens.delete(*self.tree_itens.get_children())
            messagebox.showinfo("Sucesso", "Pedido excluído.")

    # ===========================================================
    # MODAL DE CRIAÇÃO DE PEDIDO
    # ===========================================================
    def abrir_modal_pedido(self):
        modal = Toplevel(self)
        modal.title("Novo Pedido")
        modal.geometry("550x500")
        modal.resizable(False, False)
        modal.grab_set()

        # Cliente
        tk.Label(modal, text="Cliente:").pack(pady=5)
        combo_cliente = ttk.Combobox(modal, values=self.carregar_clientes(), width=40, state="readonly")
        combo_cliente.pack(pady=5)

        # Data
        tk.Label(modal, text="Data (YYYY-MM-DD):").pack(pady=5)
        entry_data = tk.Entry(modal, width=40)
        entry_data.insert(0, datetime.now().strftime("%Y-%m-%d"))
        entry_data.pack(pady=5)

        # Itens do pedido
        frame_itens = tk.LabelFrame(modal, text="Itens do Pedido")
        frame_itens.pack(fill="both", expand=True, padx=10, pady=10)

        colunas = ("produto_id", "produto", "quantidade", "preco_unit", "subtotal")
        tree_itens_modal = ttk.Treeview(frame_itens, columns=colunas, show="headings", height=6)
        for col in colunas:
            tree_itens_modal.heading(col, text=col.capitalize())
        # Esconde coluna produto_id (mantém referência)
        tree_itens_modal.column("produto_id", width=0, stretch=False)
        for c, w in zip(["produto", "quantidade", "preco_unit", "subtotal"], [200, 80, 100, 100]):
            tree_itens_modal.column(c, width=w)
        tree_itens_modal.pack(fill="both", expand=True, padx=5, pady=5)

        # Total
        total_var = tk.DoubleVar(value=0.0)
        tk.Label(modal, textvariable=total_var, font=("Arial", 12, "bold")).pack(pady=5)

        # Funções internas
        def adicionar_item():
            item_modal = Toplevel(modal)
            item_modal.title("Adicionar Item")
            item_modal.geometry("360x300")
            item_modal.resizable(False, False)
            item_modal.grab_set()

            tk.Label(item_modal, text="Pesquisar produto:").pack(pady=4)
            entry_search = ttk.Entry(item_modal, width=40)
            entry_search.pack(pady=4)

            # Listbox com resultados pesquisáveis
            listbox_frame = ttk.Frame(item_modal)
            listbox_frame.pack(fill="both", expand=False, padx=6, pady=4)
            listbox = tk.Listbox(listbox_frame, height=6, width=48)
            listbox.pack(side="left", fill="both", expand=True)
            lb_scroll = ttk.Scrollbar(listbox_frame, orient="vertical", command=listbox.yview)
            lb_scroll.pack(side="right", fill="y")
            listbox.configure(yscrollcommand=lb_scroll.set)

            produtos_cache = Produto.listar() or []  # list of tuples (id, nome, preco_unit)

            def refresh_listbox(filter_text=""):
                listbox.delete(0, tk.END)
                ft = filter_text.strip().lower()
                for p in produtos_cache:
                    pid, nome, preco = p
                    display = f"{pid} - {nome}  (R$ {preco:.2f})"
                    if not ft or ft in nome.lower() or ft in str(pid):
                        listbox.insert(tk.END, display)

            refresh_listbox()

            tk.Label(item_modal, text="Quantidade:").pack(pady=4)
            entry_qtd = ttk.Entry(item_modal, width=20)
            entry_qtd.pack(pady=4)

            tk.Label(item_modal, text="Preço Unitário (R$):").pack(pady=4)
            preco_var = tk.StringVar(value="0.00")
            lbl_preco = ttk.Label(item_modal, textvariable=preco_var, width=20, anchor="w")
            lbl_preco.pack(pady=2)

            # atualizar listbox ao digitar
            def on_search_key(e=None):
                refresh_listbox(entry_search.get())

            entry_search.bind("<KeyRelease>", on_search_key)

            # quando selecionar na listbox, preencher preço
            def on_listbox_select(e=None):
                sel = listbox.curselection()
                if not sel:
                    return
                text = listbox.get(sel[0])
                try:
                    pid = int(text.split(" - ")[0])
                except Exception:
                    pid = None
                if pid is None:
                    return
                # buscar produto no cache
                for p in produtos_cache:
                    if p[0] == pid:
                        preco_var.set(f"{p[2]:.2f}")
                        break

            listbox.bind("<<ListboxSelect>>", on_listbox_select)

            def salvar_item():
                sel = None
                cur = listbox.curselection()
                if cur:
                    sel = listbox.get(cur[0])
                qtd = entry_qtd.get().strip()
                preco = preco_var.get().strip()

                if not sel or not qtd:
                    messagebox.showwarning("Campos obrigatórios", "Selecione um produto e informe a quantidade!")
                    return
                try:
                    qtd = int(qtd)
                except ValueError:
                    messagebox.showerror("Erro", "Quantidade deve ser um número inteiro.")
                    return

                try:
                    prod_id = int(sel.split(" - ")[0])
                except Exception:
                    messagebox.showerror("Erro", "Produto inválido selecionado.")
                    return

                # obter preço do cache
                preco_f = 0.0
                for p in produtos_cache:
                    if p[0] == prod_id:
                        preco_f = float(p[2])
                        prod_nome = p[1]
                        break

                subtotal = qtd * preco_f
                # armazenamos produto_id como primeira coluna (oculta)
                tree_itens_modal.insert("", "end", values=(prod_id, prod_nome, qtd, f"{preco_f:.2f}", f"{subtotal:.2f}"))
                total_var.set(total_var.get() + subtotal)
                item_modal.destroy()

            tk.Button(item_modal, text="Salvar", command=salvar_item, width=15).pack(pady=10)
            tk.Button(item_modal, text="Cancelar", command=item_modal.destroy, width=15).pack(pady=5)

        def salvar_pedido():
            cliente_sel = combo_cliente.get()
            if not cliente_sel:
                messagebox.showwarning("Aviso", "Selecione um cliente.")
                return
            id_cliente = int(cliente_sel.split(" - ")[0])
            data = entry_data.get().strip()
            if not self.validar_data(data):
                messagebox.showerror("Data inválida", "Use o formato YYYY-MM-DD.")
                return
            if not tree_itens_modal.get_children():
                messagebox.showwarning("Aviso", "Adicione pelo menos um item.")
                return

            # Salva pedido
            pedido = Pedido(id_cliente, data, total_var.get())
            pedido.salvar()

            # Recupera o ID recém-criado
            pedidos = Pedido.listar()
            novo_id = pedidos[-1][0]

            # Salva itens (ItemPedido aceita: pedido_id, produto_id, quantidade)
            for item in tree_itens_modal.get_children():
                vals = tree_itens_modal.item(item)["values"]
                produto_id = int(vals[0])
                qtd = int(vals[2])
                item_p = ItemPedido(novo_id, produto_id, qtd)
                item_p.salvar()

            self.listar_pedidos()
            messagebox.showinfo("Sucesso", "Pedido criado com sucesso!")
            modal.destroy()

        # Botões do modal
        frame_botoes = tk.Frame(modal)
        frame_botoes.pack(pady=10)
        tk.Button(frame_botoes, text="Adicionar Item", command=adicionar_item, width=15).grid(row=0, column=0, padx=5)
        tk.Button(frame_botoes, text="Salvar Pedido", command=salvar_pedido, width=15).grid(row=0, column=1, padx=5)
        tk.Button(frame_botoes, text="Cancelar", command=modal.destroy, width=15).grid(row=0, column=2, padx=5)

    # ===========================================================
    # ITENS DO PEDIDO (detalhes)
    # ===========================================================
    def carregar_itens_pedido(self):
        for i in self.tree_itens.get_children():
            self.tree_itens.delete(i)
        selec = self.tree.selection()
        if not selec:
            return
        pedido_id = self.tree.item(selec)["values"][0]
        itens = ItemPedido.listar_por_pedido(pedido_id)
        total = 0
        for item in itens:
            # item: (id, produto_id, nome, preco_unit, quantidade)
            produto_id = item[1]
            nome = item[2]
            preco = float(item[3])
            qtd = int(item[4])
            subtotal = preco * qtd
            total += subtotal
            # inserimos produto_id (oculto), nome, qtd, preco, subtotal
            self.tree_itens.insert("", "end", values=(produto_id, nome, qtd, f"{preco:.2f}", f"{subtotal:.2f}"))
