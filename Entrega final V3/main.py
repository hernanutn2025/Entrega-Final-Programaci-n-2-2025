from PyQt5.QtWidgets import QApplication
from ventanaLogin import VentanaLogin
import sys

def main():
    app = QApplication(sys.argv)
    login = VentanaLogin()
    login.show()
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    main()