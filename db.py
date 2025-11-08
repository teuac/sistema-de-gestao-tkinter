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

        # Tabela de itens do pedido (modelo novo: apenas referencia produto_id e quantidade)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS itens_pedido (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pedido_id INTEGER NOT NULL,
                produto_id INTEGER NOT NULL,
                quantidade INTEGER NOT NULL,
                FOREIGN KEY (pedido_id) REFERENCES pedidos (id),
                FOREIGN KEY (produto_id) REFERENCES produtos (id)
            );
        """)

        # Tabela de produtos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                preco_unit REAL NOT NULL
            );
        """)

        # Migração para versões antigas: se a tabela itens_pedido existia com colunas antigas (produto, preco_unit,
        # etc), recria a tabela migrando produto_id quando possível.
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='itens_pedido_old_migration_check'")
        # Check current columns
        cursor.execute("PRAGMA table_info(itens_pedido)")
        existing_cols = [row[1] for row in cursor.fetchall()]
        # If existing columns include 'produto' or 'preco_unit' (old schema) but not only new schema, attempt migration
        old_cols = set(["produto", "preco_unit"]) & set(existing_cols)
        if old_cols:
            # We assume current table already matches new schema if it has produto_id and quantidade only — skip
            # To be safe, create a temp table, copy mapped data, drop old and rename
            try:
                cursor.execute("ALTER TABLE itens_pedido RENAME TO itens_pedido_old")
                cursor.execute("""
                    CREATE TABLE itens_pedido (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        pedido_id INTEGER NOT NULL,
                        produto_id INTEGER NOT NULL,
                        quantidade INTEGER NOT NULL,
                        FOREIGN KEY (pedido_id) REFERENCES pedidos (id),
                        FOREIGN KEY (produto_id) REFERENCES produtos (id)
                    );
                """)
                # Copy data: try to map produto name to produto_id in produtos, otherwise NULL (will fail NOT NULL)
                cursor.execute("SELECT id, pedido_id, produto, quantidade FROM itens_pedido_old")
                rows = cursor.fetchall()
                for r in rows:
                    old_id, pedido_id, produto_nome, quantidade = r
                    # find produto_id by name
                    cursor.execute("SELECT id FROM produtos WHERE nome=?", (produto_nome,))
                    res = cursor.fetchone()
                    if res:
                        produto_id = res[0]
                    else:
                        produto_id = None
                    if produto_id is not None:
                        cursor.execute("INSERT INTO itens_pedido (pedido_id, produto_id, quantidade) VALUES (?, ?, ?)", (pedido_id, produto_id, quantidade))
                cursor.execute("DROP TABLE itens_pedido_old")
            except Error:
                # If migration fails, ignore and continue with the new (empty) table
                pass

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
