import sqlite3

class DATABASE:
	def __init__(self, db_name="films.db"):
		try:
			self.conn = sqlite3.connect(db_name)
		except Exception as e:
			print("[ ERROR ] - " +e)

		self.c = self.conn.cursor()


	def create_table(self, table_name=None, table_rows=None):
		trow_typesemp = ""
		
		for c,v in table_rows.items():
			row_types += c + "  " + v + ","

		self.c.execute("CREATE TABLE IF NOT EXISTS " + table_name + " (" + row_types + ");")
		self.conn.commit()


	def insert(self, table_name=None, args=[]):
		col_count = "("

		for i in range(len(args)):
			col_count+= "?" + (" " if i == len(args)-1 else ", ")

		col_count += ")"

		self.c.execute("INSERT INTO " + table_name + " VALUES " + col_count, args)
		self.conn.commit()


	def delete(self, table_name=None, where=None):
		if where:
			self.c.execute("DELETE FROM " + table_name + " WHERE " + where + ";")
		else:
			self.c.execute("DELETE FROM " + table_name)

		self.conn.commit()


	def read(self, table_name=None, where=None, what="*"):
		if where:
			self.c.execute("SELECT " + what + " FROM " + table_name + " WHERE " + where + ";")
			return self.c.fetchall()
		else:
			self.c.execute("SELECT " + what + " FROM " + table_name)
			return self.c.fetchall()


	def close(self):
		self.conn.close()

