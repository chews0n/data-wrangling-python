
# Importing the libraries
from weather_predictor.data import DownloadWeatherData
from weather_predictor.data import ProcessData

import os
from datetime import date


def main():
    # Initial variables
    test_year = 2019
    start_year = 2010
    end_year = date.today().year

    # Initialize the weather class data
    weather_data = DownloadWeatherData(start_year=start_year, end_year=end_year)

    # create the directory to download the data into (for cleanliness)
    if not os.path.exists(os.path.join(os.getcwd(), "calgary_weather_data")):
        os.makedirs(os.path.join(os.getcwd(), "calgary_weather_data"))

    output_dir = os.path.join(os.getcwd(), "calgary_weather_data", "en_climate_daily_AB_3031094_{}_P1D.csv")

    # Download the data into the correct folder
    weather_data.download_data(download_location=output_dir)

    # Processing the data, we are going to make a training and a test set for the data
    model_data = ProcessData(output_dir=output_dir)

    model_data.load_data(start_year=start_year, end_year=end_year, test_year=test_year)

    model_data.clean_loaded_data()

    model_data.create_new_variable()

    model_data.plot_column_data(year=2020, column_name='Max Temp (°C)')

    model_data.normalize_datasets()

    model_data.binning_temps()


if __name__ == '__main__':
    main()
