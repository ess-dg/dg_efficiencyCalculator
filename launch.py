import efficiencyCalculator.efficiencyCalculator as effc

import sys
from PyQt5 import QtWidgets

if __name__ == '__main__':
    if (sys.version_info > (3, 0)):
        app = QtWidgets.QApplication(sys.argv)
        # initialize app's main controller
        # controller = MainController()
        window = effc.Window()
        sys.exit(app.exec_())
        print(sys.path)
    else:
        print("use python3")
