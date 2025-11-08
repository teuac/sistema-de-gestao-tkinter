import sqlite3
from sqlite3 import Error


# ===========================================================
# Função para conectar ao banco de dados
# ===========================================================
def conectar():
    """Cria e retorna a conexão com o banco de dados SQLite."""
    try:
        conn = sqlite3.connect("banco_dados.db")
        return conn
    except Error as e:
        print(f"❌ Erro ao conectar ao banco de dados: {e}")
        return None


# ===========================================================
# Função para criar as tabelas
# ===========================================================
def inicializar_banco():
    """Cria as tabelas no banco de dados, se não existirem."""
    conexao = conectar()
    if conexao is None:
        print("❌ Falha ao conectar. O banco não foi inicializado.")
        return

    try:
        cursor = conexao.cursor()

        # Tabela de clientes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT,
                telefone TEXT
            );
        """)

        # Tabela de pedidos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pedidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_cliente INTEGER NOT NULL,
                data TEXT NOT NULL,
                total REAL DEFAULT 0,
                FOREIGN KEY (id_cliente) REFERENCES clientes (id)
            );
        """)

        # Tabela de itens do pedido
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS itens_pedido (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pedido_id INTEGER NOT NULL,
                produto TEXT NOT NULL,
                quantidade INTEGER NOT NULL,
                preco_unit REAL NOT NULL,
                FOREIGN KEY (pedido_id) REFERENCES pedidos (id)
            );
        """)

        conexao.commit()
        print("✅ Banco de dados inicializado com sucesso.")

    except Error as e:
        print(f"❌ Erro ao criar tabelas: {e}")

    finally:
        if conexao:
            conexao.close()


# ===========================================================
# Funções genéricas de execução de SQL
# ===========================================================
def executar_query(query, parametros=()):
    """Executa INSERT, UPDATE ou DELETE."""
    conexao = conectar()
    if conexao is None:
        return False

    try:
        cursor = conexao.cursor()
        cursor.execute(query, parametros)
        conexao.commit()
        return True
    except Error as e:
        print(f"❌ Erro ao executar query: {e}")
        return False
    finally:
        conexao.close()


def consultar(query, parametros=()):
    """Executa um SELECT e retorna os resultados."""
    conexao = conectar()
    if conexao is None:
        return []

    try:
        cursor = conexao.cursor()
        cursor.execute(query, parametros)
        resultados = cursor.fetchall()
        return resultados
    except Error as e:
        print(f"❌ Erro ao consultar banco: {e}")
        return []
    finally:
        conexao.close()


# ===========================================================
# Execução direta para teste
# ===========================================================
if __name__ == "__main__":
    inicializar_banco()
