import os


class Config:
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASS = os.environ.get('DB_PASS', 'rootpass')
    DB_HOST = os.environ.get('DB_HOST', '0.0.0.0')
    DB_PORT = os.environ.get('DB_PORT', 3306)
    DATABASE = os.environ.get('DATABASE', 'links')
