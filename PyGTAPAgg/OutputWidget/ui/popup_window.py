from PyQt6 import QtWidgets as qtw
from PyQt6 import QtCore as qtc

class PopUpWindow(qtw.QWidget):
    """Popup window class for displaying progress and status of aggregation tasks.

    This class provides a user interface with a progress bar and labels to show
    the status of various components during the aggregation process. It also
    includes buttons to terminate or close the popup.

    Attributes:
        status_value (int): The current progress value for the progress bar.
        my_grid (QGridLayout): The layout manager for the popup window.
        bar (QProgressBar): The progress bar widget.
        bar_label (QLabel): The label for the progress bar.
        terminate_button (QPushButton): The button to terminate aggregation tasks.
        close_button (QPushButton): The button to close the popup window.
    """

    def __init__(self):
        """Initializes the popup window with a progress bar and status labels."""
        self.status_value = 0

        super().__init__(None, modal=True)

        self.my_grid=qtw.QGridLayout()
        self.setLayout(self.my_grid)
        

        self.bar = qtw.QProgressBar(self)
        self.bar.setGeometry(0, 0, 100, 25)
        self.bar_label=qtw.QLabel('<b>Progress:<\b>')    
        self.bar.setMaximum(100)

        self.first_column_label=qtw.QLabel('<b><u>Databases</b>')
        self.second_column_label=qtw.QLabel('<b></b>')
        self.third_column_label=qtw.QLabel('<b><u>Status</b>')

        self.base_data_label=qtw.QLabel('Basedata.har')
        self.sets_label=qtw.QLabel('Sets.har')
        self.param_label=qtw.QLabel('Param.har')
        self.gtapView_label=qtw.QLabel('gtapView.har')
        self.gtapSam_label=qtw.QLabel('gtapSam.har')
        self.vol_label=qtw.QLabel('vol.har')
        self.emiss_label=qtw.QLabel('emiss.har')

        self.base_data_text=qtw.QLabel('Not executed... ')
        self.sets_text=qtw.QLabel('Not executed...')
        self.param_text=qtw.QLabel('Not executed... ')
        self.gtapView_text=qtw.QLabel('Not executed... ')
        self.gtapSam_text=qtw.QLabel('Not executed... ')
        self.vol_text=qtw.QLabel('Not executed... ')
        self.emiss_text=qtw.QLabel('Not executed... ')

        self.terminate_button=qtw.QPushButton('Terminate', self)
        self.close_button=qtw.QPushButton('Close', self)
    
        self.my_grid.addWidget(self.bar_label,0,0)
        self.my_grid.addWidget(self.bar, 1,0,1,3)

        self.my_grid.addWidget(self.first_column_label,2,0)
        self.my_grid.addWidget(self.second_column_label,2,1)
        self.my_grid.addWidget(self.third_column_label,2,2)

        
        self.my_grid.addWidget(self.base_data_label,3,0)
        self.my_grid.addWidget(self.sets_label,4,0)
        self.my_grid.addWidget(self.param_label,5,0)
        self.my_grid.addWidget(self.gtapView_label,6,0)
        self.my_grid.addWidget(self.gtapSam_label,7,0)
        self.my_grid.addWidget(self.vol_label,8,0)
        self.my_grid.addWidget(self.emiss_label,9,0)

        self.my_grid.addWidget(self.base_data_text,3,2)
        self.my_grid.addWidget(self.sets_text,4,2)
        self.my_grid.addWidget(self.param_text,5,2)
        self.my_grid.addWidget(self.gtapView_text,6,2)
        self.my_grid.addWidget(self.gtapSam_text,7,2)
        self.my_grid.addWidget(self.vol_text,8,2)
        self.my_grid.addWidget(self.emiss_text,9,2)

        self.my_grid.addWidget(self.terminate_button,10,1)
        self.my_grid.addWidget(self.close_button, 10,2)

        self.close_button.clicked.connect(lambda: self.close())

        self.show()

    def shut_me(self):
        """Closes the popup window."""
        self.close()