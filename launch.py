import efficiencyCalculator.efficiencyCalculator as effc

import sys
from PyQt4 import QtGui

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    # initialize app's main controller
    # controller = MainController()
    window = effc.Window()
    sys.exit(app.exec_())
