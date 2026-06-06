import sqlite3

conn = sqlite3.connect('c:/Users/LOQ/Downloads/IA/APP para Gym/backend/gym.db')
cursor = conn.cursor()
tables = ['members', 'plans', 'memberships', 'payments']
for t in tables:
    count = cursor.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]
    print(f'Tabla {t}: {count} registros')
conn.close()
