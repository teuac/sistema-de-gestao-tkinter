import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
from models import Cliente
import re  # para validações


class ClientesView(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack(fill="both", expand=True, padx=12, pady=8)
        self.criar_widgets()
        self.listar_clientes()

    # ===========================================================
    # Criação dos widgets
    # ===========================================================
    def criar_widgets(self):
        # Campos
        ttk.Label(self, text="Nome:").grid(row=0, column=0, padx=6, pady=6, sticky="e")
        self.entry_nome = ttk.Entry(self, width=42)
        self.entry_nome.grid(row=0, column=1, padx=6, pady=6, sticky="w")

        ttk.Label(self, text="Email:").grid(row=1, column=0, padx=6, pady=6, sticky="e")
        self.entry_email = ttk.Entry(self, width=42)
        self.entry_email.grid(row=1, column=1, padx=6, pady=6, sticky="w")

        ttk.Label(self, text="Telefone:").grid(row=2, column=0, padx=6, pady=6, sticky="e")
        self.entry_tel = ttk.Entry(self, width=42)
        self.entry_tel.grid(row=2, column=1, padx=6, pady=6, sticky="w")

        # Botões
        frame_botoes = ttk.Frame(self)
        frame_botoes.grid(row=3, column=0, columnspan=2, pady=10)

        ttk.Button(frame_botoes, text="Salvar", command=self.salvar_cliente, width=12).grid(row=0, column=0, padx=6)
        ttk.Button(frame_botoes, text="Editar", command=self.abrir_modal_edicao, width=12).grid(row=0, column=1, padx=6)
        ttk.Button(frame_botoes, text="Excluir", command=self.excluir_cliente, width=12).grid(row=0, column=2, padx=6)

        # Barra de pesquisa
        frame_pesquisa = ttk.Frame(self)
        frame_pesquisa.grid(row=4, column=0, columnspan=2, sticky="ew", pady=6)

        ttk.Label(frame_pesquisa, text="Pesquisar por Email:").pack(side="left", padx=6)
        self.entry_pesquisa = ttk.Entry(frame_pesquisa, width=34)
        self.entry_pesquisa.pack(side="left", padx=6)
        self.entry_pesquisa.bind("<Return>", lambda e: self.pesquisar_cliente())

        ttk.Button(frame_pesquisa, text="Pesquisar", command=self.pesquisar_cliente).pack(side="left", padx=6)
        ttk.Button(frame_pesquisa, text="Limpar", command=self.listar_clientes).pack(side="left", padx=6)

        # Lista
        colunas = ("id", "nome", "email", "telefone")
        self.tree = ttk.Treeview(self, columns=colunas, show="headings")
        for col in colunas:
            self.tree.heading(col, text=col.capitalize())
        self.tree.column("id", width=60, anchor="center")
        self.tree.column("nome", width=220)
        self.tree.column("email", width=260)
        self.tree.column("telefone", width=130, anchor="center")
        self.tree.grid(row=5, column=0, columnspan=2, sticky="nsew", padx=6, pady=6)

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=5, column=2, sticky="ns", pady=6)

        self.grid_rowconfigure(5, weight=1)
        self.grid_columnconfigure(1, weight=1)

    # ===========================================================
    # Funções auxiliares de validação
    # ===========================================================
    def validar_email(self, email):
        """Verifica se o email é válido."""
        padrao = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(padrao, email) is not None

    def validar_telefone(self, telefone):
        """Verifica se o telefone é válido (aceita DDD, traços e espaços)."""
        padrao = r'^\(?\d{2,3}\)?[\s\-]?\d{4,5}[\s\-]?\d{4}$'
        return re.match(padrao, telefone) is not None

    # ===========================================================
    # CRUD e Pesquisa
    # ===========================================================
    def listar_clientes(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for c in Cliente.listar():
            self.tree.insert("", "end", values=c)

    def pesquisar_cliente(self):
        email_busca = self.entry_pesquisa.get().strip()
        if not email_busca:
            messagebox.showinfo("Pesquisa", "Digite um e-mail para pesquisar.")
            return

        resultados = Cliente.pesquisar_por_email(email_busca)
        for item in self.tree.get_children():
            self.tree.delete(item)

        if resultados:
            for c in resultados:
                self.tree.insert("", "end", values=c)
        else:
            messagebox.showinfo("Pesquisa", "Nenhum cliente encontrado com esse e-mail.")

    def salvar_cliente(self):
        nome = self.entry_nome.get().strip()
        email = self.entry_email.get().strip()
        telefone = self.entry_tel.get().strip()

        # Validação
        if not nome:
            messagebox.showwarning("Aviso", "O campo Nome é obrigatório!")
            return
        if email and not self.validar_email(email):
            messagebox.showerror("Email inválido", "Por favor, insira um e-mail válido (ex: usuario@dominio.com).")
            return
        if telefone and not self.validar_telefone(telefone):
            messagebox.showerror("Telefone inválido", "Digite um telefone válido. Exemplo: (11) 99999-9999")
            return

        cliente = Cliente(nome, email, telefone)
        cliente.salvar()
        self.listar_clientes()
        messagebox.showinfo("Sucesso", "Cliente salvo com sucesso!")

        self.entry_nome.delete(0, tk.END)
        self.entry_email.delete(0, tk.END)
        self.entry_tel.delete(0, tk.END)

    def excluir_cliente(self):
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um cliente para excluir.")
            return

        item = self.tree.item(selecionado)
        cliente_id = item["values"][0]

        if messagebox.askyesno("Confirmação", "Deseja realmente excluir este cliente?"):
            Cliente.deletar(cliente_id)
            self.listar_clientes()
            messagebox.showinfo("Sucesso", "Cliente excluído com sucesso!")

    # ===========================================================
    # Modal de edição
    # ===========================================================
    def abrir_modal_edicao(self):
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um cliente para editar.")
            return

        item = self.tree.item(selecionado)
        cliente_id, nome, email, telefone = item["values"]

        modal = Toplevel(self)
        modal.title("Editar Cliente")
        modal.geometry("350x220")
        modal.resizable(False, False)
        modal.grab_set()

        tk.Label(modal, text="Nome:").pack(pady=5)
        entry_nome = tk.Entry(modal, width=40)
        entry_nome.insert(0, nome)
        entry_nome.pack(pady=5)

        tk.Label(modal, text="Email:").pack(pady=5)
        entry_email = tk.Entry(modal, width=40)
        entry_email.insert(0, email)
        entry_email.pack(pady=5)

        tk.Label(modal, text="Telefone:").pack(pady=5)
        entry_tel = tk.Entry(modal, width=40)
        entry_tel.insert(0, telefone)
        entry_tel.pack(pady=5)

        def salvar_edicao():
            novo_nome = entry_nome.get().strip()
            novo_email = entry_email.get().strip()
            novo_tel = entry_tel.get().strip()

            if not novo_nome:
                messagebox.showwarning("Aviso", "O campo Nome é obrigatório!")
                return
            if novo_email and not self.validar_email(novo_email):
                messagebox.showerror("Email inválido", "Por favor, insira um e-mail válido (ex: usuario@dominio.com).")
                return
            if novo_tel and not self.validar_telefone(novo_tel):
                messagebox.showerror("Telefone inválido", "Digite um telefone válido. Exemplo: (11) 99999-9999")
                return

            cliente_editado = Cliente(novo_nome, novo_email, novo_tel, id=cliente_id)
            cliente_editado.salvar()
            self.listar_clientes()
            messagebox.showinfo("Sucesso", "Cliente atualizado com sucesso!")
            modal.destroy()

        tk.Button(modal, text="Salvar Alterações", command=salvar_edicao, width=20).pack(pady=10)
        tk.Button(modal, text="Cancelar", command=modal.destroy, width=20).pack(pady=5)
