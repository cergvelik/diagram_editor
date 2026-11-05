import sys
from PyQt6.QtWidgets import QApplication
from database import init_db

def main():
    init_db()
    print("База данных успешно инициализирована")

    app = QApplication(sys.argv)
    

if __name__ == "__main__":
    main()