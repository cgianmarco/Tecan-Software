#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import widgets


class Stack():
    # This should be __init__(self, shape, axis_values, listener)
    def __init__(self, name, shape, axis_values, listener):
        self.name = name
        self.time = shape['time']
        self.depth = shape['depth']
        self.width_value = shape['width']
        self.height_value = shape['height']
        self.axis_values = axis_values

        self.grid = widgets.Grid(self.width_value, self.height_value)

        # self.selection_grid = widgets.SelectionGrid(shape)
        self.selection_grid = widgets.SelectionGrid(shape, self.axis_values)
        self.selection_grid.connect(listener)

        self.control_bar = {}

        if self.depth > 1:
            self.control_bar['depth'] = widgets.ControlBar('depth', self.axis_values['depth'])
            self.control_bar['depth'].connect(listener)

        if self.time > 1:
            self.control_bar['time'] = widgets.ControlBar('time', self.axis_values['time'])
            self.control_bar['time'].connect(listener)

        self.__legend = widgets.Legend()

        self.widget = QWidget()
        self.layout = QHBoxLayout()
        vertical_layout = QVBoxLayout()
        self.layout.addLayout(vertical_layout)
        self.layout.addWidget(self.__legend)
        

        # for child_layout in self.child_layouts:
        #     self.layout.addLayout(child_layout)


        vertical_layout.addWidget(self.selection_grid)

        # change to one widget
        Hlayout = QHBoxLayout()
        if 'depth' in self.control_bar:
            Hlayout.addWidget(self.control_bar['depth'])
        if 'time' in self.control_bar:
            Hlayout.addWidget(self.control_bar['time'])
        Hlayout.addStretch(1)
        vertical_layout.addLayout(Hlayout)


        vertical_layout.addWidget(self.grid)

        vertical_layout.addStretch(1)
        self.widget.setLayout(self.layout)

    # @property
    # def child_layouts(self):
    #     yield self.selection_grid.layout
    #     Hlayout = QHBoxLayout()
    #     if 'depth' in self.control_bar:
    #         Hlayout.addLayout(self.control_bar['depth'].layout)
    #     if 'time' in self.control_bar:
    #         Hlayout.addLayout(self.control_bar['time'].layout)
    #     Hlayout.addStretch(1)
    #     yield Hlayout
    #     # yield self.grid.layout

    def update_grid(self, matrix):
        self.grid.update(matrix)

    def get_selected(self):
        return self.selection_grid.get_selected()

    def update_control_value(self, dim, value):
        if dim in self.control_bar:
            self.control_bar[dim].value.setText(str(value + self.axis_values[dim][0]))

    def get_control_value(self, dim):
        return int(self.control_bar[dim].value.text()) - self.axis_values[dim][0]

    def clear_datagrid_color(self):
        self.grid.clear_color()

    def is_in_range(self, dim, start, end):
        if dim in self.control_bar:
            current = self.get_control_value(dim)
            return start <= current and current <= end
        else: 
            return True

    def update_datagrid_color(self, selected):
        start_row = selected['start_width']
        end_row = selected['end_width']
        start_column = selected['start_height']
        end_column = selected['end_height']
        start_depth = selected['start_depth']
        end_depth = selected['end_depth']
        start_time = selected['start_time']
        end_time = selected['end_time']



        if start_row <= end_row and start_column <= end_column and self.is_in_range('depth', start_depth, end_depth) and self.is_in_range('time', start_time, end_time):
            self.grid.update_color(start_row, end_row, start_column, end_column)

    def update_datagrid_background(self, selected, color):

        start_row = selected['start_width']
        end_row = selected['end_width']
        start_column = selected['start_height']
        end_column = selected['end_height']
        start_depth = selected['start_depth']
        end_depth = selected['end_depth']
        start_time = selected['start_time']
        end_time = selected['end_time']

        if start_row <= end_row and start_column <= end_column:
            self.grid.update_background_color(start_row, end_row, start_column, end_column, color)

    def update_colors(self, colors):
        self.__legend.update(colors)

    def add_color(self, color):
        self.__legend.add_item(color)



def DEFAULT_ACTION(*args, **kwargs):
    raise NotImplementedError("Action not yet implemented")


       


class View(QMainWindow):
    
    def __init__(self, listener, parent=None):
        super(View, self).__init__(parent)
        self.listener = listener
        # self.init_listeners()
        self.init_menu_bar()
        self.init_ui()
        self.init_ops()

    def init_ops(self):
        self.actions = {}
        self.actions['Load Tensor'] = (self.listener.on_tensor_load, [self.get_file_name])
        self.actions['Export Matrix'] = (self.listener.on_export_current_matrix, [self.get_selected])


        self.actions['Mean Single'] = (self.listener.on_mean_action, [self.get_selected])
        self.actions['Mean Wavelengths'] = (self.listener.on_mean_wavelengths_action, [self.get_selected])
        self.actions['Mean Time'] = (self.listener.on_mean_times_action, [self.get_selected])

        self.actions['Value from Selected'] = (self.listener.on_subtract_action, [self.get_selected, self.get_list_selected])
        self.actions['Standard deviation'] = (self.listener.on_std_action, [self.get_selected])
        self.actions['Add legend'] = (self.listener.on_add_legend_action, [self.get_selected, self.get_color])
        self.actions['Start recording'] = (self.listener.on_start_recording_action, [])
        self.actions['End recording'] = (self.listener.on_end_recording_action, [])
        self.actions['Operation 1'] = (self.listener.on_custom_operation_action, [self.get_selected])
        self.actions['Blank Selection'] = (self.listener.on_blank_selection_action, [self.get_selected])
        self.actions['Blank Reduction Single'] = (self.listener.on_blank_reduction_action, [self.get_selected])
        self.actions['Blank Reduction Wavelengths'] = (self.listener.on_blank_reduction_wavelengths_action, [self.get_selected])
        self.actions['Blank Reduction Time'] = (self.listener.on_blank_reduction_time_action, [self.get_selected])



    def get_color(self):
        color = QColorDialog.getColor()
        return color



    def init_menu_bar(self):
    	# menubar
        bar = self.menuBar()

        # File
        file = bar.addMenu("File")
        file.triggered[QAction].connect(self.process_trigger)

        file.addAction("Load Tensor")
        file.addAction("Export Matrix")

        # Operations
        operations = bar.addMenu("Operations")
        operations.triggered[QAction].connect(self.process_trigger)

        mean = operations.addMenu("Mean")
        mean.addAction("Mean Single")
        mean.addAction("Mean Wavelengths")
        mean.addAction("Mean Time")

        std = operations.addMenu("Standard deviation")
        std.addAction("Standard deviation Single")
        std.addAction("Standard deviation Wavelengths")
        std.addAction("Standard deviation Time")

        # operations.addAction("Start recording")
        # operations.addAction("End recording")

        operations.addAction("Blank Selection")
        blank_reduction = operations.addMenu("Blank Reduction")
        blank_reduction.addAction('Blank Reduction Single')
        blank_reduction.addAction('Blank Reduction Wavelengths')

        subtract = operations.addMenu("Subtract")
        subtract.addAction("Value from Selected")

        # custom = operations.addMenu("Custom")
        # custom.addAction("Operation 1")

        # View
        viewmenu = bar.addMenu("View")
        viewmenu.triggered[QAction].connect(self.process_trigger)

        viewmenu.addAction("Add legend")

      
    def init_ui(self):
        # main layout
        vlayout = QVBoxLayout()

        self.stacks = []
        self.current_stack = -1
        self.last_index = -1
        

        self.stack_container = widgets.StackContainer()
        self.stack_container.list_widget.currentRowChanged.connect(self.listener.on_changed_stack)    
        self.listValue = widgets.listWidget()



        # Add Child Layouts
        vlayout.addWidget(self.stack_container)
        vlayout.addWidget(self.listValue)


        mainWidget = QWidget()
        mainWidget.setLayout(vlayout)
        self.setCentralWidget(mainWidget)        
        self.move(300, 150)
        self.setWindowTitle('TECAN Reader')


    def add_new_stack(self, name, shape, axis_values):
        new_stack = Stack(name, shape, axis_values, self.listener)
        self.stacks.append(new_stack)
        self.stack_container.add_stack(name, new_stack.widget)
        self.current_stack = self.stacks.index(new_stack)

    def add_color(self, color):
        self.stack.add_color(color)

    # def remove_stack(self, index):
        # del self.stacks[index]
        # self.stack_container.stacks_widget.removeWidget(self.values_widget.widget(index))
        # self.stack_container.list_widget.takeItem(index)
    
    def set_stack_index(self, index):
        self.current_stack = index
        self.stack_container.stacks_widget.setCurrentIndex(index)


    def update_values_list(self, values):
        self.listValue.clear()
        for key in values.keys():
            self.listValue.addItem(key + ":" + str(values[key]))

    @property
    def stack(self):
        return self.stacks[self.current_stack]

    def get_file_name(self):
        filename = QFileDialog.getOpenFileName(self, 'Open file')
        return filename

    def process_trigger(self, q):
        op, params = self.actions[str(q.text())]
        params = (param() for param in params)
        op(*params)

        # if q.text() == 'Load Tensor':
        #     self.listener.on_tensor_load(self.get_file_name())
        # elif q.text() == 'Export Matrix':
        #     self.listener.on_export_current_matrix(self.get_selected())
        # elif q.text() == 'Mean':
        #     self.listener.on_mean_action(self.get_selected())
        # elif q.text() == 'Mean Reduction':
        #     self.listener.on_mean_reduction_action(self.get_selected())
        # elif q.text() == 'Value from Selected':
        #     self.listener.on_subtract_action(self.get_selected(), self.get_list_selected())
        # elif q.text() == 'Standard deviation':
        #     self.listener.on_std_action(self.get_selected())
        # elif q.text() == 'Add legend':
        #     self.update_datagrid_background(self.get_selected())
        # elif q.text() == 'Start recording':
        #     self.listener.on_start_recording_action()
        # elif q.text() == 'End recording':
        #     self.listener.on_end_recording_action()
        # elif q.text() == 'Operation 1':
        #     self.listener.on_custom_operation_action(self.get_selected())

    def update_grid(self, matrix):
        self.stack.update_grid(matrix)
    
    def get_selected(self):
        return self.stack.get_selected()
    
    def update_control_value(self, dim, value):
        self.stack.update_control_value(dim, value)
    
    def get_list_selected(self):
        return str(self.listValue.currentItem().text()).split(":")[0]

    def get_control_value(self, dim):
        return self.stack.get_control_value(dim)

    def clear_datagrid_color(self):
        self.stack.clear_datagrid_color()

    def update_datagrid_color(self, selected):
        self.stack.update_datagrid_color(selected)

    def update_datagrid_background(self, selected, color):
        self.stack.update_datagrid_background(selected, color)

    def update_colors(self, colors):
        self.stack.update_colors(colors)






