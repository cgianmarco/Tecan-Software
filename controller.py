from model import Model
from view import View
from fileloader import *
from extractor import FileParser
from filesaver import *
import os
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from random import randint


class Listener:
	def __init__(self, view):
		self.view = view

	def on_tensor_loaded(self, event):
		name = event['name']
		shape = event['shape']
		axis_values = event['axis_values']
		# self.view.add_new_stack(shape)
		self.view.add_new_stack(name, shape, axis_values)

	def on_matrix_changed(self, event):
		matrix = event['matrix']
		depth = event['wavelength']
		time = event['time']
		self.view.update_grid(matrix)
		self.view.update_control_value('depth', depth)
		self.view.update_control_value('time', time)

	def on_changed_current_tensor(self, event):
		i = event['i']
		# colors = event['colors']
		self.view.set_stack_index(i)
		# self.view.update_legend_texts(colors)

	def on_values_list_changed(self, event):
		values = event['values']
		self.view.update_values_list(values)

	def on_selected_changed(self, event):
		self.view.clear_datagrid_color()
		selected = event
		self.view.update_datagrid_color(selected)

	def on_legend_changed(self, event):
		selected = event['selected']
		color = event['color']
		self.view.update_datagrid_background(selected, color)

	def on_colors_changed(self, event):
		colors = event
		print(len(colors))
		self.view.update_colors(colors)



class ViewListener():
	def __init__(self):
		self.model = None
		self.inputs = []
		self.recorded_ops = []
		self.recorded = []
		self.recording = False

	def add_model(self, model):
		self.model = model

	def on_tensor_load(self, filename):
		fileparser = FileParser(str(filename))
		
		names, tensors = fileparser.tensors()
		for name, tensor in zip(names, tensors):
			self.model.add_new_tensor(name, tensor)

	def record_op(self, command):
		self.recorded.append(command)
		if 'tensor' in command[-1]:
			self.model.add_new_tensor(command[-1], self.model.wrap_tensor(np.zeros((8,8,8,8))))
		else:
			self.model.add_value(command[-1], None)

	def on_mean_action(self, selected, sel_value=None, result_name=None):
		if self.recording == True:
			self.record_op((self.on_mean_action, selected, None, 'mean' + str(randint(0,1000000))))
		else:
			mean = self.model.get_mean(selected)
			self.model.add_value("Mean", str(mean))

	def on_mean_wavelengths_action(self, selected):
		mean = self.model.get_mean_reduction(selected, "wavelength")
		self.model.add_new_tensor('Result', mean)

	def on_mean_times_action(self, selected):
		mean = self.model.get_mean_reduction(selected, "time")
		self.model.add_new_tensor('Result', mean)

	def on_std_action(self, selected, value=None):
		if self.recording == True:
			self.record_op(self.on_mean_action, selected)
		std = self.model.get_std(selected)
		self.model.add_value("std", str(std))

	def on_subtract_action(self, selected, sel_value, result_name=None):
		if self.recording == True:
			self.record_op((self.on_mean_action, selected, sel_value, 'tensor-subt' + str(randint(0,1000000))))
		else:
			v1 = self.model.get_selected_matrix(selected)
			v2 = self.model.get_selected_value(sel_value)
			print(v2)
			result = self.model.subtract(v1, v2)
			self.model.update_selected_matrix(result, selected)

	def on_start_recording_action(self):
		self.recording = True

	def on_end_recording_action(self):
		self.recording = False

	def on_custom_operation_action(self, selected):
		for entry in self.recorded:
			op, sel_indeces, sel_value, result_name = entry
			sel_indeces['start_time'] = selected['start_time']
			sel_indeces['end_time'] = selected['end_time']
			sel_indeces['start_depth'] = selected['start_depth']
			sel_indeces['end_depth'] = selected['end_depth']
			op(sel_indeces, sel_value, result_name)



	def on_move_back(self, dim):
		self.model.add_value_to_dim(dim, -1)

	def on_move_forward(self, dim):
		self.model.add_value_to_dim(dim, 1)

	def on_text_changed(self, text, dim, axis_values):
		try:
			value = int(text)
			if axis_values[0] <= value <= axis_values[:1]:
				self.model.change_current_dim(dim, value - axis_values[0])
		except ValueError:
			pass

	def on_changed_selection(self, selected):
		self.model.update_selected(selected)

	def on_changed_stack(self, i):
		self.model.change_current_tensor(i)

	def on_export_current_matrix(self, selected):
		exporter = Exporter()
		exporter.export_up_to_three_dim_tensor(self.model.get_current_tensor().name, self.model.get_selected_matrix(selected))


	def on_add_legend_action(self, selected, color):
		self.model.update_legend(selected, color)

	# def on_legend_text_changed(self, text, color):
	# 	self.model.update_legend_text(color, text)

	def on_blank_selection_action(self, selected):
		self.model.update_selected_blank(selected)

	def on_blank_reduction_action(self, selected):

		selected_blank = self.model.get_selected_blank()
		selected_blank['start_time'] = selected['start_time']
		selected_blank['end_time'] = selected['end_time']
		selected_blank['start_depth'] = selected['start_depth']
		selected_blank['end_depth'] = selected['end_depth']

		blank_mean = self.model.get_mean(selected_blank)
		result = self.model.subtract(self.model.get_selected_matrix(selected), blank_mean)
		self.model.update_selected_matrix(result, selected)

	def on_blank_reduction_wavelengths_action(self, selected):

		selected_blank = self.model.get_selected_blank()
		selected_blank['start_depth'] = selected['start_depth']
		selected_blank['end_depth'] = selected['end_depth']
		for wavelength in range(selected['start_depth'], selected['end_depth']):
			selected_blank['start_depth'] = wavelength
			selected_blank['end_depth'] = wavelength
			selected_blank['start_time'] = 0
			selected_blank['end_time'] = 0

			selected['start_depth'] = wavelength
			selected['end_depth'] = wavelength
			selected['start_time'] = 0
			selected['end_time'] = 0

			blank_mean = self.model.get_mean(selected_blank)
			result = self.model.subtract(self.model.get_selected_matrix(selected), blank_mean)
			self.model.update_selected_matrix(result, selected)

	def on_blank_reduction_time_action(self, selected):

		selected_blank = self.model.get_selected_blank()
		for time in range(selected['start_time'], selected['end_time']):
			selected_blank['start_depth'] = 0
			selected_blank['end_depth'] = 0
			selected_blank['start_time'] = time
			selected_blank['end_time'] = time

			selected['start_depth'] = 0
			selected['end_depth'] = 0
			selected['start_time'] = time
			selected['end_time'] = time

			blank_mean = self.model.get_mean(selected_blank)
			result = self.model.subtract(self.model.get_selected_matrix(selected), blank_mean)
			self.model.update_selected_matrix(result, selected)




class Controller:
	def __init__(self):
		viewListener = ViewListener()
		self.view = View(viewListener)
		self.model = Model(Listener(self.view))
		viewListener.add_model(self.model)

	def load_tensor(self, filename):
		self.view.listener.on_tensor_load(filename)

	def show(self):
		self.view.show()
		


