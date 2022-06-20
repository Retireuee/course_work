import sqlite3 as sql
import aiosqlite


class Database:
    def __init__(self):
        self.db = "./SQLiteData/Database.db"
        self.connection = sql.connect(self.db)
        self.cur = self.connection.cursor()
        try:
            query = """
                CREATE TABLE IF NOT EXISTS users(
                supplierid INTEGER PRIMARY KEY AUTOINCREMENT,
                suppliername TEXT,
                INNcode TEXT,
                KPPcode TEXT);
                INSERT INTO users(supplierid, suppliername, INNcode, KPPcode)
                VALUES  (1, 'Игорь', '1', '11'),
                        (2, 'Маша', '2', '22'),        
                        (3, 'Коля', '3', '33'),        
                        (4, 'Павел', '4', '44');
            """
            self.cur.executescript(query)
            self.connection.commit()

            query = """
                CREATE TABLE IF NOT EXISTS orders(
                orderid INT PRIMARY KEY,
                date TEXT,
                supplierid int,
                invoicecode TEXT,            
                productcode TEXT,
                SIZE INT,
                FOREIGN KEY (supplierid) REFERENCES users(supplierid) ON DELETE CASCADE ON UPDATE NO ACTION);
                INSERT INTO users(orderid, date, supplierid, invoicecode, productcode, SIZE)
                VALUES  (1, '2022-05-01', 4, '123', '23', 10),
                        (2, '2022-11-25', 3, '678', '76', 9),   
                        (3, '2022-06-08', 4, '667', '93', 67),   
                        (4, '2022-05-12', 1, '976', '34', 50),
                        (5, '2022-08-16', 2, '567', '64', 18);
            """
            self.cur.executescript(query)
            self.connection.commit()

        except sql.Error as e:
            self.error = f"Ошибка выполнения запроса {e}"
        if self.connection:
            self.connection.close()

    async def suppliers_dict_id(self):
        suppliers_dict = {}
        async with aiosqlite.connect(self.db) as db:
            async with db.execute("SELECT supplierid, suppliername FROM users") as cursor:
                async for i in cursor:
                    suppliers_dict[i[1]] = i[0]
            return suppliers_dict

    async def orders_data(self):
        query = """ SELECT orderid, date, suppliername, invoicecode, INNcode, KPPcode, productcode, size
                    FROM orders
                    INNER JOIN users USING(supplierid)"""

        async with aiosqlite.connect(self.db) as db:
            async with db.execute(query) as cursor:
                return await cursor.fetchall()

    async def users_data(self):
        query = """ SELECT * FROM users"""

        async with aiosqlite.connect(self.db) as db:
            async with db.execute(query) as cursor:
                return await cursor.fetchall()

    async def orders_save(self, data):
        query = """INSERT INTO orders (orderid, date, supplierid, invoicecode, productcode, size)
                   VALUES (?, ?, ?, ?, ?, ?)"""
        async with aiosqlite.connect(self.db) as db:
            async with db.cursor() as cursor:
                await cursor.execute("DELETE FROM orders")
                await cursor.executemany(query, data)
                count_rows = cursor.rowcount
            await db.commit()
            return count_rows

    async def users_save(self, data):
        query = """INSERT INTO users (supplierid, suppliername, INNcode, KPPcode)
                   VALUES (?, ?, ?, ?)"""
        async with aiosqlite.connect(self.db) as db:
            async with db.cursor() as cursor:
                await cursor.execute("DELETE FROM users")
                await cursor.executemany(query, data)
                count_rows = cursor.rowcount
            await db.commit()
            return count_rows
