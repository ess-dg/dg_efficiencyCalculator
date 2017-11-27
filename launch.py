import efficiencyCalculator.efficiencyCalculator as effc

import sys
from PyQt5 import QtWidgets

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    # initialize app's main controller
    # controller = MainController()
    window = effc.Window()
    sys.exit(app.exec_())
