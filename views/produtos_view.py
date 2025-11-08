import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox, Toplevel

# Permite executar este arquivo isoladamente adicionando a raiz do projeto ao sys.path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from models import Produto


class ProdutosView(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack(fill="both", expand=True, padx=12, pady=8)
        self.criar_widgets()
        self.listar_produtos()

    def criar_widgets(self):
        ttk.Label(self, text="Nome:").grid(row=0, column=0, padx=6, pady=6, sticky="e")
        self.entry_nome = ttk.Entry(self, width=40)
        self.entry_nome.grid(row=0, column=1, padx=6, pady=6, sticky="w")

        ttk.Label(self, text="Preço Unitário (R$):").grid(row=1, column=0, padx=6, pady=6, sticky="e")
        self.entry_preco = ttk.Entry(self, width=40)
        self.entry_preco.grid(row=1, column=1, padx=6, pady=6, sticky="w")

        frame_botoes = ttk.Frame(self)
        frame_botoes.grid(row=2, column=0, columnspan=2, pady=10)
        ttk.Button(frame_botoes, text="Salvar", command=self.salvar_produto, width=12).grid(row=0, column=0, padx=6)
        ttk.Button(frame_botoes, text="Editar", command=self.abrir_modal_edicao, width=12).grid(row=0, column=1, padx=6)
        ttk.Button(frame_botoes, text="Excluir", command=self.excluir_produto, width=12).grid(row=0, column=2, padx=6)

        colunas = ("id", "nome", "preco")
        self.tree = ttk.Treeview(self, columns=colunas, show="headings")
        for col in colunas:
            self.tree.heading(col, text=col.capitalize())
        self.tree.column("id", width=60, anchor="center")
        self.tree.column("nome", width=260)
        self.tree.column("preco", width=120, anchor="e")
        self.tree.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=6, pady=6)

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=3, column=2, sticky="ns", pady=6)

        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(1, weight=1)

    def listar_produtos(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for p in Produto.listar():
            self.tree.insert("", "end", values=(p[0], p[1], f"{p[2]:.2f}"))

    def salvar_produto(self):
        nome = self.entry_nome.get().strip()
        preco = self.entry_preco.get().strip()
        if not nome:
            messagebox.showwarning("Aviso", "O campo Nome é obrigatório!")
            return
        try:
            preco = float(preco)
        except ValueError:
            messagebox.showerror("Erro", "Preço deve ser numérico.")
            return
        prod = Produto(nome, preco)
        prod.salvar()
        self.listar_produtos()
        messagebox.showinfo("Sucesso", "Produto salvo com sucesso!")
        self.entry_nome.delete(0, tk.END)
        self.entry_preco.delete(0, tk.END)

    def excluir_produto(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um produto para excluir.")
            return
        pid = self.tree.item(sel)["values"][0]
        if messagebox.askyesno("Confirmação", "Deseja realmente excluir este produto?"):
            Produto.deletar(pid)
            self.listar_produtos()
            messagebox.showinfo("Sucesso", "Produto excluído.")

    def abrir_modal_edicao(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um produto para editar.")
            return
        pid, nome, preco = self.tree.item(sel)["values"]
        modal = Toplevel(self)
        modal.title("Editar Produto")
        modal.geometry("350x180")
        modal.grab_set()

        ttk.Label(modal, text="Nome:").pack(pady=6)
        e_nome = ttk.Entry(modal, width=40)
        e_nome.insert(0, nome)
        e_nome.pack(pady=6)

        ttk.Label(modal, text="Preço Unitário (R$):").pack(pady=6)
        e_preco = ttk.Entry(modal, width=40)
        e_preco.insert(0, preco)
        e_preco.pack(pady=6)

        def salvar_edicao():
            nn = e_nome.get().strip()
            pp = e_preco.get().strip()
            if not nn:
                messagebox.showwarning("Aviso", "Nome é obrigatório")
                return
            try:
                pp = float(pp)
            except ValueError:
                messagebox.showerror("Erro", "Preço deve ser numérico")
                return
            prod = Produto(nn, pp, id=pid)
            prod.salvar()
            self.listar_produtos()
            messagebox.showinfo("Sucesso", "Produto atualizado com sucesso")
            modal.destroy()

        ttk.Button(modal, text="Salvar Alterações", command=salvar_edicao, width=20).pack(pady=8)
        ttk.Button(modal, text="Cancelar", command=modal.destroy, width=20).pack()

__all__ = ["ProdutosView"]
