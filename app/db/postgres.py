import psycopg2

def get_pg_data():
    with psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="postgres",
        host="citus_master",
        port="5432"
    ) as pg_conn:
        with pg_conn.cursor() as pg_cur:
            pg_cur.execute("SET citus.enable_repartition_joins TO on;")

            pg_cur.execute("SELECT id, nama, email FROM users LIMIT 10")
            users = [dict(id=r[0], nama=r[1], email=r[2]) for r in pg_cur.fetchall()]

            pg_cur.execute("SELECT sku, nama, harga FROM produk LIMIT 10")
            produk_list = [dict(sku=r[0], nama=r[1], harga=r[2]) for r in pg_cur.fetchall()]

            pg_cur.execute("SELECT id, user_id, sku, jumlah, total FROM orders LIMIT 10")
            orders = [dict(id=r[0], user_id=r[1], sku=r[2], jumlah=r[3], total=r[4]) for r in pg_cur.fetchall()]

            pg_cur.execute("""
                SELECT o.id, o.jumlah, o.total, o.created_at,
                       u.nama AS pemesan,
                       p.nama AS nama_produk, p.harga
                FROM orders o
                JOIN users u ON o.user_id = u.id
                JOIN produk p ON o.sku = p.sku
                ORDER BY o.created_at DESC
                LIMIT 5
            """)
            order_detail = [dict(
                id=r[0], jumlah=r[1], total=r[2], created_at=r[3],
                pemesan=r[4], nama_produk=r[5], harga=r[6]
            ) for r in pg_cur.fetchall()]

    return users, produk_list, orders, order_detail
def insert_produk(sku, nama, harga):
    with psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="postgres",
        host="citus_master",
        port="5432"
    ) as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO produk (sku, nama, harga) VALUES (%s, %s, %s)", (sku, nama, harga))
            conn.commit()

def update_produk(sku, nama, harga):
    with psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="postgres",
        host="citus_master",
        port="5432"
    ) as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE produk SET nama = %s, harga = %s WHERE sku = %s", (nama, harga, sku))
            conn.commit()

def delete_produk(sku):
    with psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="postgres",
        host="citus_master",
        port="5432"
    ) as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM produk WHERE sku = %s", (sku,))
            conn.commit()

def get_produk(sku):
    with psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="postgres",
        host="citus_master",
        port="5432"
    ) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT sku, nama, harga FROM produk WHERE sku = %s", (sku,))
            row = cur.fetchone()
            if row:
                return {"sku": row[0], "nama": row[1], "harga": row[2]}
            return None

