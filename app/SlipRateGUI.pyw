#!/usr/bin/env python
import sys
import os
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from IPython.qt.console.rich_ipython_widget import RichIPythonWidget
from IPython.qt.inprocess import QtInProcessKernelManager


import slipRateWindow

sys.path.append('../slip_rate_tools/')
import slip_rate_tools as srt

import pandas as pd
import matplotlib.pyplot as plt


'''
Test data.  This will be removed when the adding data interface is built.
'''

offset_df = pd.read_csv('../test_data/offsets.csv')
offset_df['offset_m'] = offset_df.offset_in * 200.

t1 = offset_df[offset_df.unit == 'T1']
qa = offset_df[offset_df.unit == 'Qa']
qao = offset_df[offset_df.unit == 'Qao']

#qa['offset_m'] += 200.

t1_age = {'mean': 24., 'sd':8.}
qa_age = {'mean': 50., 'sd':20.}
qao_age = {'mean':100., 'sd':32.}

#qao_age['mean'] += 200

T1 = srt.OffsetMarker(age_mean=t1_age['mean'], age_sd=t1_age['sd'],
                      offset_vals=t1.offset_m, offset_probs=t1.rel_prob)

Qa = srt.OffsetMarker(age_mean=qa_age['mean'], age_sd=qa_age['sd'],
                      offset_vals=qa.offset_m, offset_probs=qa.rel_prob)

Qao = srt.OffsetMarker(age_mean=qao_age['mean'], age_sd=qao_age['sd'],
                      offset_vals=qao.offset_m, offset_probs=qao.rel_prob)


offset_list = [T1, Qa, Qao]





class EmbedIPython(RichIPythonWidget):

    def __init__(self, **kwarg):
        super(RichIPythonWidget, self).__init__()
        self.kernel_manager = QtInProcessKernelManager()
        self.kernel_manager.start_kernel()
        self.kernel = self.kernel_manager.kernel
        self.kernel.gui = 'qt4'
        self.kernel.shell.push(kwarg)
        self.kernel_client = self.kernel_manager.client()
        self.kernel_client.start_channels()



class SlipRateWindow(QMainWindow, slipRateWindow.Ui_MainWindow):
    def __init__(self, parent=None):
        super(SlipRateWindow, self).__init__(parent)

        self.setupUi(self)
        self.setWindowTitle('Slip Rate Calculator')

        #self.textBrowser.append("Welcome to the Slip Rate Calculator!")


        # main running buttons
        self.runButton.clicked.connect(self.run_slip_history)
        self.cancelButton.clicked.connect(self.cancel_run)
        self.plotButton.clicked.connect(self.plot_results)

        # config buttons
        self.importButton.clicked.connect(self.import_config)
        self.exportButton.clicked.connect(self.export_config)


        # IPython console
        self.console = EmbedIPython(srt=srt, plt=plt)
        self.verticalLayout.addWidget(self.console)



    # main running functions
    def run_slip_history(self):
        # assemble variables from menu
        # start 
        # run (need to have some process)
        # report output (connect process to textBrowser)
        #self.console.execute("pwd")
        
        run_config_dict = self.concat_config_options()
        self.console.kernel.shell.push({'rc':run_config_dict, 
                                        'offset_list':offset_list})

        self.console.execute('srt.run_interp_from_gui(offset_list, rc)')

        #pass

    def cancel_run(self):
        # cancel run process

        self.console.execute("\x03\r\n")

        # pass

    def plot_results(self):
        # maybe plot some stuff, maybe open up a new window that
        # has lots of options before plotting
        pass


    # Config functions
    def concat_config_options(self):

    # TODO: Need to check to see how failures (empty boxes, etc.) affect
    # running of functions. Where to handle the failures? print custom errors?
        run_config = {}

        run_config['n_iters'] = int( self.nItersLineEdit.text() )
        run_config['zero_offset_age'] = float( self.zeroOffsetLineEdit.text() )
        run_config['random_seed'] = self.randSeedCheckBox.isChecked()
        run_config['random_seed_value'] = float( self.randSeedLineEdit.text() )
        run_config['force_increasing'] = self.forceIncrCheckBox.isChecked()
        run_config['slip_reversals'] = self.slipRevCheckBox.isChecked()
        run_config['fit_type'] = self.get_fit_type()
        run_config['n_linear_pieces'] = int( self.nPiecesSpinBox.value() ) 

        return run_config

    def get_fit_type(self):

        if self.linearFitRadio.isChecked():
            fit_type = 'linear'
        elif self.piecewiseFitRadio.isChecked():
            fit_type = 'piecewise'
        elif self.cubicFitRadio.isChecked():
            fit_type = 'cubic'

        return fit_type

    def concat_offset_markers(self):
        # don't really know how to deal with this right now
        pass

    def concat_all_variables(self):
        all_vars = {}

        for key, val in concat_config_options():
            all_vars[key] = val

        for key, val in concat_offset_markers():
            all_vars[key] = val

        return all_vars

    def import_config(self):
        # open file browser, select file
        # try reading as csv, json
        # output run_config dict
        pass

    def export_config(self):
        # open file browser
        # select either csv or json
        # write to appropriate file, don't allow others
        
        all_vars = concat_all_variables()
        
        pass



app = QApplication(sys.argv)
mainWindow = SlipRateWindow()
mainWindow.show()
app.exec_()