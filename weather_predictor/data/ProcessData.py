from datetime import date
from datetime import datetime as dt
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

col_list = ['Date/Time', 'Year', 'Month', 'Day', 'Max Temp (°C)', 'Min Temp (°C)', 'Mean Temp (°C)',
			'Total Precip (mm)', 'Snow on Grnd (cm)']


class ProcessData:

	def __init__(self, output_dir=""):

		self.load_general_path = str(output_dir)
		self.df_test = pd.DataFrame()
		self.df_train = pd.DataFrame()
		self.date_test = pd.DataFrame()

	def load_data(self, start_year=2010, end_year=date.today().year, test_year=date.today().year):
		global col_list

		df_load_list = list()
		nrows = 366
		this_year = date.today().year
		for year in range(start_year, end_year + 1):
			# Importing the datasets
			# Note: the dataset is served as a CSV from the website, alternatively you can also use
			# pd.read_excel() to load an excel sheet in the same way

			# Check if we're in the current year and truncate the number of rows to read in accordingly
			if (year == this_year):
				# Get the number of days until today
				d0 = date(this_year, 1, 1)
				d1 = date.today()
				delta = d1 - d0
				nrows = delta.days
			else:
				nrows = 366


			# check whether to load this to the test or train dataframe


			if year == test_year:
				self.df_test = pd.read_csv(self.load_general_path.format(year), usecols=col_list, nrows=nrows)
			else:
				self.df_train = pd.concat([self.df_train, pd.read_csv(self.load_general_path.format(year), usecols=col_list, nrows=nrows)], ignore_index=True)

		# Let's print out the column headers so we know what we have
		for col in self.df_train.columns:
			print(col)

		## How many rows are there?
		print(len(self.df_train))

		## Getting the first n-rows of the dataset
		print(self.df_train.head(10))
		# similarly, for the last n-rows it would be .tail(n-rows)


	def clean_loaded_data(self):
		# If you look through the csv files, there are missing values for some of the days, we need to handle these in a way that makes sense in order to get accurate data and avoid exceptions
		# Remove any rows where Max Temp = NaN
		# NaN's are removed as making a prediction for
		self.df_train.replace(r"[a-zA-Z]", 0.0, inplace=True)
		self.df_test.replace(r"[a-zA-Z]", 0.0, inplace=True)

		self.df_train.fillna(method="ffill", inplace=True)
		self.df_test.fillna(method="ffill", inplace=True)

	def create_new_variable(self):
		# Create new column with max Temp from teh previous day
		# If day is missing, we use the next available day
		self.df_train['Max Temp Prev (°C)'] = self.df_train['Max Temp (°C)'].shift(periods=1)
		self.df_test['Max Temp Prev (°C)'] = self.df_test['Max Temp (°C)'].shift(periods=1)

		# check if the first entry is nan, if so just use that day's temperature
		if np.isnan(self.df_test['Max Temp Prev (°C)'][0]):
			self.df_test.at[0, 'Max Temp Prev (°C)'] = self.df_test['Max Temp (°C)'].values[0]

		if np.isnan(self.df_train['Max Temp Prev (°C)'][0]):
			self.df_train.at[0, 'Max Temp Prev (°C)'] = self.df_train['Max Temp (°C)'].values[0]

	def filter_by_year(self, df, year):

		return df[df['Year'].isin([year])]


	def plot_column_data(self, year=date.today().year, column_name=''):
		# Format the dates and combine with the predictions, test variables
		# https://stackoverflow.com/questions/53863600/reduce-number-of-ticks-on-x-axis-where-labels-are-date

		plot_date = list()
		plot_vals = list()

		if year in self.df_test['Year'].unique():
			plot_date = [dt.strptime(dstr, '%Y-%m-%d') for dstr in self.df_test['Date/Time']]
			plot_vals = self.df_test[column_name]
		else:
			one_year_df = self.filter_by_year(self.df_train, year)

			plot_date = [dt.strptime(dstr, '%Y-%m-%d') for dstr in one_year_df['Date/Time']]
			plot_vals = one_year_df[column_name]

		# Visualize the predictions vs the results
		plt.plot(plot_date, plot_vals, 'b-', label=column_name)
		plt.gca().xaxis.set_major_locator(mdates.DayLocator((1, 15)))
		plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
		plt.setp(plt.gca().get_xticklabels(), rotation=60, ha="right")
		plt.legend()
		plt.xlabel('Date')
		plt.ylabel(column_name)
		plt.title(column_name)

		# save the outputted figure
		plt.savefig('plot_{}_{}.png'.format(column_name, year), dpi=300, bbox_inches='tight')

		plt.close()


	def normalize_datasets(self):
		# use the z-score method to normalize the data and plot it
		self.df_train['zscaled Max Temp (°C)'] = (self.df_train['Max Temp (°C)'] - self.df_train['Max Temp (°C)'].mean()) / self.df_train['Max Temp (°C)'].std()

		# use the min-max scaling
		self.df_train['minmax scaled Max Temp (°C)'] = (self.df_train['Max Temp (°C)'] - self.df_train['Max Temp (°C)'].min()) / (self.df_train['Max Temp (°C)'].max() - self.df_train['Max Temp (°C)'].min())

		# self.df_train.to_clipboard(sep=',')
		# plot the scalings to compare
		self.plot_column_data(year=2020, column_name='zscaled Max Temp (°C)')
		self.plot_column_data(year=2020, column_name='minmax scaled Max Temp (°C)')

	def binning_temps(self):

		self.df_train['bin'] = pd.cut(self.df_train['Max Temp (°C)'], 6, labels=["Freezing", "Cold", "Spring?", "Probably Spring", "Perfect", "Hotter than the sun"]).astype(str)
		self.df_train['bin'].value_counts().plot(kind='bar')
		# save the outputted figure
		plt.savefig('plot_categories.png', dpi=300, bbox_inches='tight')

		plt.close()




