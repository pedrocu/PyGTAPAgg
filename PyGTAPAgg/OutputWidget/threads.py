import subprocess 
import os 
import re
from PyQt6 import QtCore as qtc

class AggThread(qtc.QThread):
    """Executes aggregation processes in a separate thread.

    This class is responsible for handling long-running aggregation tasks 
    asynchronously in a separate thread, preventing the main application 
    from freezing during execution. It supports emitting signals for real-time 
    updates and results from the aggregation process.

    Attributes:
        read_file (pyqtSignal): Signal emitted to provide updates on the progress 
            of the aggregation process. This typically contains status messages 
            or logs generated during execution.
        args (list): List of arguments to be passed to the subprocess for the 
            aggregation task.
    """
    aggdone    = qtc.pyqtSignal()
    read_file  = qtc.pyqtSignal(str, str)
    write_file = qtc.pyqtSignal(str,str)
    error_file = qtc.pyqtSignal(str,str)

    def __init__(self, *args):

        """Initializes the AggThread object.

        Args:
            *args: Arguments for the aggregation subprocess. These typically 
                include the path to the aggregation program and any necessary 
                parameters or input files.
        """
        self.args=list(args)  #A list is required for subprocess.popen to parse correct
        super().__init__()

    def run(self):
        """Executes the aggregation subprocess and emits a signal upon completion.

        This method starts the subprocess using the provided arguments during
        initialization, waits for the process to complete, and then emits the
        `aggdone` signal to notify that the aggregation process has finished.

        Raises:
            Note this is not done as an exception, it should be recast as one.
            subprocess.SubprocessError: If an error occurs during the execution of the
                subprocess.

                 try:
            # Start the subprocess
            p = subprocess.Popen(self.args, encoding='UTF-8')
            p.wait()  # Wait for the subprocess to complete

            # Emit the signal indicating that the aggregation is done
            self.aggdone.emit()
            except subprocess.SubprocessError as e:
            print(f"Error during subprocess execution: {e}")
            raise
        """
        
        if os.path.exists(self.args[0]):
            p=subprocess.Popen(self.args, 
                            stdout=subprocess.PIPE,
                            encoding='UTF-8')
            
        else:
            cwd = os.getcwd()
            print(cwd)
            print('file not found:  ' , self.args[0])
        self.read_file.emit('<b>Initilizing…<\b>', self.args[0])
        self.write_file.emit('<b>Initilizing…<\b>', self.args[0])
        

        #Write to log and to the interface

        with open('output' + '.log', 'a') as log:
        
            while p.poll() is None:
                outdata=p.stdout.readline()
                my_match=re.search(r'(.*)Reading(.*)', outdata, re.M|re.I)
                if my_match:
                    self.read_file.emit(my_match.group(0), self.args[0])
                
                my_match=re.search(r'(.*)Writing(.*)', outdata, re.M|re.I)
                if my_match:
                   self.write_file.emit(my_match.group(0), self.args[0])

                my_match=re.search(r'(.*)Error(.*)', outdata, re.M|re.I)
                if my_match:
                    self.error_file.emit(my_match.group(0), self.args[0])

                my_match=re.search(r'(.*)Warning(.*)', outdata, re.M|re.I)
                if my_match:
                    self.error_file.emit(my_match.group(0), self.args[0])
 
                log.write(outdata)
                
        
        self.read_file.emit('<b>…DONE<\b>', self.args[0])
        self.write_file.emit('<b>…DONE<\b>', self.args[0])
        
        self.aggdone.emit()
class AggHar(qtc.QObject):
    """Executes aggregation processes for HAR files using a subprocess.

    This class runs aggregation tasks synchronously in a separate process and
    emits a signal upon completion. It is primarily used to execute external
    aggregation programs or scripts.

    Attributes:
        aggdone (pyqtSignal): Signal emitted when the aggregation process is completed.
        args (list): List of arguments to be passed to the subprocess.
    """
    aggdone=qtc.pyqtSignal()

    def __init__(self, *args):
        """Initializes the AggHar object and executes the subprocess.

        Args:
            *args: Arguments to be passed to the subprocess for execution. These
                typically include the path to the aggregation program and any
                necessary parameters or input files.
        """
        self.args=args
        super().__init__()

        p=subprocess.Popen(self.args, encoding='UTF-8')
        p.wait()
        
        self.aggdone.emit()