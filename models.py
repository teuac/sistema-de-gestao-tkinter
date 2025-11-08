import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db import executar_query, consultar


# ===========================================================
# Modelo: Cliente
# ===========================================================
class Cliente:
    def __init__(self, nome, email, telefone, id=None):
        self.id = id
        self.nome = nome
        self.email = email
        self.telefone = telefone

    def salvar(self):
        """Insere ou atualiza o cliente no banco."""
        if self.id:
            query = "UPDATE clientes SET nome=?, email=?, telefone=? WHERE id=?"
            parametros = (self.nome, self.email, self.telefone, self.id)
        else:
            query = "INSERT INTO clientes (nome, email, telefone) VALUES (?, ?, ?)"
            parametros = (self.nome, self.email, self.telefone)
        return executar_query(query, parametros)

    @staticmethod
    def listar():
        """Retorna todos os clientes."""
        return consultar("SELECT * FROM clientes")

    @staticmethod
    def pesquisar_por_email(email_parcial):
        """Pesquisa clientes pelo email (parcial ou completo)."""
        like_pattern = f"%{email_parcial}%"
        query = "SELECT * FROM clientes WHERE email LIKE ?"
        return consultar(query, (like_pattern,))

    @staticmethod
    def deletar(cliente_id):
        """Remove um cliente."""
        return executar_query("DELETE FROM clientes WHERE id=?", (cliente_id,))


# ===========================================================
# Modelo: Pedido
# ===========================================================
class Pedido:
    def __init__(self, id_cliente, data, total=0, id=None):
        self.id = id
        self.id_cliente = id_cliente
        self.data = data
        self.total = total

    def salvar(self):
        """Insere ou atualiza um pedido."""
        if self.id:
            query = "UPDATE pedidos SET id_cliente=?, data=?, total=? WHERE id=?"
            parametros = (self.id_cliente, self.data, self.total, self.id)
        else:
            query = "INSERT INTO pedidos (id_cliente, data, total) VALUES (?, ?, ?)"
            parametros = (self.id_cliente, self.data, self.total)
        return executar_query(query, parametros)

    @staticmethod
    def listar():
        """Retorna todos os pedidos."""
        return consultar("SELECT * FROM pedidos")

    @staticmethod
    def deletar(pedido_id):
        """Remove um pedido."""
        return executar_query("DELETE FROM pedidos WHERE id=?", (pedido_id,))


# ===========================================================
# Modelo: ItemPedido
# ===========================================================
class ItemPedido:
    def __init__(self, pedido_id, produto, quantidade, preco_unit, id=None):
        self.id = id
        self.pedido_id = pedido_id
        self.produto = produto
        self.quantidade = quantidade
        self.preco_unit = preco_unit

    def salvar(self):
        """Insere ou atualiza um item do pedido."""
        if self.id:
            query = """
                UPDATE itens_pedido
                SET pedido_id=?, produto=?, quantidade=?, preco_unit=?
                WHERE id=?
            """
            parametros = (self.pedido_id, self.produto, self.quantidade, self.preco_unit, self.id)
        else:
            query = """
                INSERT INTO itens_pedido (pedido_id, produto, quantidade, preco_unit)
                VALUES (?, ?, ?, ?)
            """
            parametros = (self.pedido_id, self.produto, self.quantidade, self.preco_unit)
        return executar_query(query, parametros)

    @staticmethod
    def listar_por_pedido(pedido_id):
        """Lista todos os itens de um pedido específico."""
        return consultar("SELECT * FROM itens_pedido WHERE pedido_id=?", (pedido_id,))

    @staticmethod
    def deletar(item_id):
        """Remove um item do pedido."""
        return executar_query("DELETE FROM itens_pedido WHERE id=?", (item_id,))
