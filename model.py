import numpy as np

class Tensor:
	def __init__(self, name):
		self.current_state = {'time':0, 'depth':0}
		self.name = name
		self.__legend = {}
		self.__colors = []
		self.__selected_blank = { 'start_width':0, 'end_width':0, 'start_height':0, 'end_height':0 }

	def get_selected_blank(self):
		return self.__selected_blank

	def update_selected_blank(self, selected):
		for key in self.__selected_blank.keys():
			self.__selected_blank[key] = selected[key]

	def change_current_depth(self, value):
		self.current_state['depth'] = value

	def change_current_time(self, value):
		self.current_state['time'] = value

	def change_current_state(self, dim, value):
		self.current_state[dim] = value

	def load(self, loadedfile):
		# Wavelengths interval
		print(loadedfile)	
		self.axis_values = loadedfile['axis_values']
		self.data = loadedfile['data']
		self.time, self.depth, self.width, self.height = loadedfile['data'].shape
		self.selected = { 'start_width':0, 'end_width':0, 'start_height':0, 'end_height':0, 'start_depth':0, 'end_depth':0, 'start_time':0, 'end_time':0}


	def get_current_matrix(self):
		return self.data[self.current_state['time']][self.current_state['depth']]

	def get_selected(self):
		selected = self.selected
		return selected

	def get_selected_matrix(self, selected):
		start_row = selected['start_width']
		end_row = selected['end_width']
		start_column = selected['start_height']
		end_column = selected['end_height']
		start_depth = selected['start_depth'] 
		end_depth = selected['end_depth'] 
		start_time = selected['start_time']
		end_time = selected['end_time']
		return self.data[start_time:end_time+1, start_depth:end_depth+1, start_row:end_row+1, start_column:end_column+1]

	def update_selected_matrix(self, result, selected):
		start_row = selected['start_width']
		end_row = selected['end_width']
		start_column = selected['start_height']
		end_column = selected['end_height']
		start_depth = selected['start_depth'] 
		end_depth = selected['end_depth'] 
		start_time = selected['start_time']
		end_time = selected['end_time']
		self.data[start_time:end_time+1, start_depth:end_depth+1, start_row:end_row+1, start_column:end_column+1] = result

	def get_mean(self, selected):
		return round(np.nanmean(self.get_selected_matrix(selected)), 4)

	def get_mean_reduction(self, selected, dim):

		if dim == "wavelength":
			result = np.nanmean(self.get_selected_matrix(selected), axis=(0,2,3))
			result = np.round(result, 4)
			result = result.reshape((1, len(result),1,1))

		if dim == "time":
			result = np.nanmean(self.get_selected_matrix(selected), axis=(1,2,3))
			result = np.round(result, 4)
			result = result.reshape((len(result), 1,1,1))

		return result

	def get_std(self, selected):
		return round(np.nanstd(self.get_selected_matrix(selected)), 4)

	def get_axis_values(self):
		return self.axis_values

	def update_selected(self, selected):
		self.selected = selected

	def dim_exists(self, dim, step):
		if dim == 'depth':
			if self.current_state[dim] + step < self.depth and self.current_state[dim] + step >= 0:
				return True
		if dim == 'time':
			if self.current_state[dim] + step < self.time and self.current_state[dim] + step >= 0:
				return True
		return False

	def get_legend(self):
		return self.__legend

	def get_colors(self):
		return self.__colors


	def update_legend(self, selected, color):
		start_row = selected['start_width']
		end_row = selected['end_width']
		start_column = selected['start_height']
		end_column = selected['end_height']

		for i in range(start_row, end_row + 1):
			for j in range(start_column, end_column + 1):
				self.__legend[(i,j)] = color

		self.update_colors()

	def update_colors(self):
		# for color in list(set(self.__legend.values())): # remove duplicates from colors
		# 	if color is not in self.__colors.keys():
		# 		self.__colors[color] = "" 
		self.__colors = list(set(self.__legend.values()))

	# def update_legend_text(self, color, text):
	# 	self.__colors[color] = text


class Model(object):
	def __init__(self, listener):
		self.tensors = []
		self.currentTensor = -1
		self.values = {}
		self.last_index = -1
		self.listener = listener

	def update_legend(self, selected, color):
		print(self.get_current_tensor().get_colors())
		self.get_current_tensor().update_legend(selected, color)
		self.listener.on_legend_changed({ 'selected' : selected, 'color' : color})
		print(self.get_current_tensor().get_colors())

		self.get_current_tensor().update_colors()
		self.listener.on_colors_changed(self.get_current_tensor().get_colors())


		


	def add_value(self, name, value):
		self.values[name] = value
		self.listener.on_values_list_changed({'values':self.values})

	def add_new_tensor(self, name, loadedfile):
		new_tensor = Tensor(name)
		new_tensor.load(loadedfile)
		self.tensors.append(new_tensor)
		self.currentTensor = self.tensors.index(new_tensor)
		# self.tensors[new_key].load(loadedfile)
		self.listener.on_tensor_loaded({'shape':{"width":new_tensor.width, "height":new_tensor.height, "depth":new_tensor.depth, "time":new_tensor.time}, 'axis_values':new_tensor.get_axis_values(), 'name':name})
		self.listener.on_matrix_changed({"matrix":self.get_current_matrix(), "wavelength":self.current_depth, "time":self.current_time})
		self.listener.on_selected_changed(self.get_current_tensor().get_selected())
		

	def remove_tensor(self, key):
		del self.tensors[key]


	############################################
	# Interface with current Tensor properties
	############################################

	@property
	def depth(self):
		return self.get_current_tensor().depth

	@property
	def time(self):
		return self.get_current_tensor().time


	@property
	def current_depth(self):
		return self.get_current_tensor().current_state['depth']

	# This
	@property
	def current_time(self):
		return self.get_current_tensor().current_state['time']

	############################################
	# Interface with current Tensor methods
	############################################

	def get_current_tensor(self):
		return self.tensors[self.currentTensor]

	def get_current_matrix(self):
		return self.get_current_tensor().get_current_matrix()


	def change_current_dim(self, dim, value):
		self.get_current_tensor().change_current_state(dim, value)
		self.listener.on_matrix_changed({"matrix":self.get_current_matrix(), "wavelength":self.current_depth, "time":self.current_time})
		self.listener.on_selected_changed(self.get_current_tensor().get_selected())


	def add_value_to_dim(self, dim, value):
		if self.get_current_tensor().dim_exists(dim, value):
			self.change_current_dim(dim, self.get_current_tensor().current_state[dim] + value)
		self.listener.on_matrix_changed({"matrix":self.get_current_matrix(), "wavelength":self.current_depth, "time":self.current_time})
		self.listener.on_selected_changed(self.get_current_tensor().get_selected())


	def change_current_tensor(self, value):
		self.currentTensor = value
		self.listener.on_changed_current_tensor({"i":value})


	def get_selected_blank(self):
		return self.get_current_tensor().get_selected_blank()


	def get_selected_matrix(self, selected):
		return self.get_current_tensor().get_selected_matrix(selected)

	def get_selected_value(self, sel_value):
		return float(self.values[sel_value])

	def update_selected_matrix(self, result, selected):
		self.get_current_tensor().update_selected_matrix(result, selected)
		self.listener.on_matrix_changed({"matrix":self.get_current_matrix(), "wavelength":self.current_depth, "time":self.current_time})
		self.listener.on_selected_changed(self.get_current_tensor().get_selected())

	def update_selected_blank(self, selected):
		self.get_current_tensor().update_selected_blank(selected)
		# self.listener.on_selected_blank_changed(self.get_current_tensor().get_selected_blank())

	def get_mean(self, selected):
		return self.get_current_tensor().get_mean(selected)

	def get_mean_reduction(self, selected, dim):
		return self.wrap_tensor(self.get_current_tensor().get_mean_reduction(selected, dim))

	def get_std(self, selected):
		return self.get_current_tensor().get_std(selected)

	def subtract(self, x, y):
		return np.round(x - y, 4)

	def update_selected(self, selected):
		self.get_current_tensor().update_selected(selected)
		self.listener.on_selected_changed(self.get_current_tensor().get_selected())

	def update_legend_text(self, color, text):
		self.get_current_tensor().update_legend_text(color, text)

	def wrap_tensor(self, tensor):
		wrapped = {}
		wrapped['data'] = tensor
		time, depth, width, height = tensor.shape
		wrapped['axis_values'] = { 'time' : range(time), 
						'depth' : range(depth), 
						'width' : range(width), 
						'height' : range(height) }
		return wrapped

	