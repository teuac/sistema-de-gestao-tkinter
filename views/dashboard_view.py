import tkinter as tk
from tkinter import ttk, messagebox
from db import consultar
from datetime import datetime


class DashboardView(ttk.Frame):
	"""Dashboard refinado com três métricas e botão Atualizar.

	Exibe:
	- total de clientes
	- total de pedidos no mês corrente
	- ticket médio do mês corrente
	"""

	def __init__(self, master=None):
		super().__init__(master)
		self.pack(fill="both", expand=True, padx=12, pady=8)
		self._create_widgets()
		self.update_dashboard()

	def _create_widgets(self):
		# Título da área
		ttk.Label(self, text="Dashboard", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 8))

		# Container principal
		container = ttk.Frame(self)
		container.pack(fill="both", expand=True)

		# Linha de cards
		cards_row = ttk.Frame(container)
		cards_row.pack(fill="x", pady=6)

		# Card: total clientes
		self.card_clients = self._make_card(cards_row, "Total de Clientes")
		# Card: pedidos no mês
		self.card_orders = self._make_card(cards_row, "Pedidos no Mês")
		# Card: ticket médio
		self.card_ticket = self._make_card(cards_row, "Ticket Médio (Mês)")

		self.card_clients.pack(side="left", expand=True, fill="x", padx=6)
		self.card_orders.pack(side="left", expand=True, fill="x", padx=6)
		self.card_ticket.pack(side="left", expand=True, fill="x", padx=6)

		# Botão atualizar
		footer = ttk.Frame(container)
		footer.pack(fill="x", pady=(12, 0))
		ttk.Button(footer, text="Atualizar", command=self._on_refresh).pack(side="right")

	def _make_card(self, parent, title):
		card = ttk.Frame(parent, padding=12, relief="raised")
		ttk.Label(card, text=title, font=("Segoe UI", 10)).pack(anchor="w")
		val = ttk.Label(card, text="—", font=("Segoe UI", 18, "bold"))
		val.pack(anchor="center", pady=(8, 0))
		# attach value label for updates
		card.value_label = val
		return card

	def update_dashboard(self):
		"""Executa consultas agregadas e atualiza os widgets do dashboard."""
		try:
			# total de clientes
			r = consultar("SELECT COUNT(*) FROM clientes")
			total_clients = r[0][0] if r and r[0] and r[0][0] is not None else 0

			# pedidos do mês corrente (usa prefixo YYYY-MM da coluna data)
			ym = datetime.now().strftime("%Y-%m")
			r2 = consultar("SELECT COUNT(*) FROM pedidos WHERE substr(data,1,7)=?", (ym,))
			total_orders = r2[0][0] if r2 and r2[0] and r2[0][0] is not None else 0

			# ticket médio do mês corrente
			r3 = consultar("SELECT AVG(total) FROM pedidos WHERE substr(data,1,7)=?", (ym,))
			avg = r3[0][0] if r3 and r3[0] and r3[0][0] is not None else 0.0

			# Formata valores (milhares com ponto e decimais com vírgula)
			def br_number(n):
				try:
					s = f"{int(n):,}"
				except Exception:
					s = "0"
				return s.replace(",", ".")

			def br_currency(x):
				s = f"{x:,.2f}"
				s = s.replace(",", "X").replace(".", ",").replace("X", ".")
				return f"R$ {s}"

			self.card_clients.value_label.config(text=br_number(total_clients))
			self.card_orders.value_label.config(text=br_number(total_orders))
			if total_orders == 0:
				# amigável quando não houver pedidos no mês
				self.card_ticket.value_label.config(text="R$ 0,00")
			else:
				self.card_ticket.value_label.config(text=br_currency(avg))

		except Exception as e:
			messagebox.showerror("Erro", f"Falha ao atualizar dashboard:\n{e}")

	def _on_refresh(self):
		self.update_dashboard()
		messagebox.showinfo("Atualização", "Dashboard atualizado com sucesso.")


__all__ = ["DashboardView"]

