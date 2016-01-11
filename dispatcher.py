# A1 for COMPSCI340/SOFTENG370 2015
# Prepared by Robert Sheehan
# Modified by edso681

# You are not allowed to use any sleep calls.

from threading import Lock, Event
from process import State
from process import Type

class Dispatcher():
    """The dispatcher."""

    MAX_PROCESSES = 8

    def __init__(self):
        """Construct the dispatcher."""
        # ...
        self.stack= []
        self.waitList = [None]*8
        #self.tosI=0
        self.tos=0
			

    def set_io_sys(self, io_sys):
        """Set the io subsystem."""
        self.io_sys = io_sys

    def add_process(self, process):
        """Add and start the process."""
         #if self.tos < self.MAX_PROCESSES-1:
         #       self.stack.append(process)
         #       self.io_sys.allocate_window_to_process(process,self.tos)
         #       process.start()
         #       self.tos += 1
        #if process.type == Type.background: 
        if self.tos<self.MAX_PROCESSES:
            self.pause_system()
            self.stack.append(process)
            self.io_sys.allocate_window_to_process(process, len(self.stack)-1)
            process.start() 
            self.tos+=1
        #elif process.type == Type.interactive:
        #     if self.tosI<self.MAX_PROCESSES:
        #            self.pause_system()
        #            process.state = State.waiting
        #            self.stackI.append(process)
        #            self.io_sys.allocate_window_to_process(process, len(self.stackI)-1)
        #            self.tosI+=1

    def dispatch_next_process(self):
        """Dispatch the process at the top of the stack."""
        # ...
        if len(self.stack):
                self.stack[-1].event.set()

    def to_top(self, process):
        """Move the process to the top of the stack."""
        # ...
        self.pause_system()
        if process.state == State.runnable:
            self.stack.remove(process)
            self.stack.append(process)
        elif process.state == State.waiting:
            index = self.waitList.index(process)
            self.waitList[index] = None
            process.state = State.runnable
            self.stack.append(process)

        self.io_sys.move_process(process,len(self.stack)-1)
        for i , j in enumerate(self.stack):
            self.io_sys.move_process(j,i)
        self.resume_system()

    def pause_system(self):
        """Pause the currently running process.
        As long as the dispatcher doesn't dispatch another process this
        effectively pauses the system.
        """
        # ...
        if len(self.stack):
                self.stack[-1].event.clear()

    def resume_system(self):
        """Resume running the system."""
        # ...
        if len(self.stack):
                self.stack[-1].event.set()
        
    def wait_until_finished(self):
        """Hang around until all runnable processes are finished."""
        # ...
        for i in self.stack:
            i.join()



    def proc_finished(self, process):
        """Receive notification that "proc" has finished.
        Only called from running processes.
        """
        if process.state == State.runnable:
            process.state = State.killed
            self.stack.remove(process)
            self.io_sys.remove_window_from_process(process)

            for i , j in enumerate(self.stack):
                self.io_sys.move_process(j,i)
        elif  process.state == State.waiting:
            process.state = State.killed
            index = self.waitList.index(process)
            self.waitList[index] = None
            self.io_sys.remove_window_from_process(process)
        self.dispatch_next_process()
        self.tos-=1
        # ...

    def proc_waiting(self, process):
        """Receive notification that process is waiting for input."""
        # ...
        process.event.clear()
        process.state = State.waiting
        self.stack.remove(process)

        for i , j in enumerate(self.waitList):
            if j is None:
                self.waitList[i] = process
                self.io_sys.move_process(process,i)
                break


        for i , j in enumerate(self.stack):
            self.io_sys.move_process(j,i)
        self.dispatch_next_process()

    def process_with_id(self, id):
        """Return the process with the id."""
        # ...
        for x in self.stack:
            if x.id == id:
                return x
        for x in self.waitList:
            if x is not None:
                if x.id == id:
                    return x

        return None
