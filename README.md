# Satellite Position Tracker - ClearSky

This project provides a Python script that show live position and predicts the route of a satellite using Two-Line Element (TLE) data. The script includes a graphical user interface (GUI) built using the Tkinter library.

The script first downloads TLE data via the API from the n2yo website based on the entered NORAD ID, then converts the satellite values into geocentric coordinates, then converts these values ​​back to geographic coordinates and determines their location on a flat map. In the meantime, it recalculates the flight route for the next few hours.



## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/satellite-position-prediction.git
```
Navigate to the project directory.
Install the required dependencies using pip:

```bash
pip install -r requirements.txt
```
## Usage
To predict the position of a satellite using the GUI, follow these steps:

Run the GUI script:
```bash
python src/main.py
```
The GUI window will open.

Choose your locatation.

Enter the NORAD ID in the format specified  in the input field.
[NORAD ID FORMAT](https://en.wikipedia.org/wiki/Satellite_Catalog_Number)

Click the "Search satellite" button.

The GUI will display the satellite's current position, predicted route and information about this object.

## Testing
The project includes unit tests to ensure the accuracy of the calculations. To run the tests, use the following command:

``` bash
python -m unittest tests/tests.py
```
## Contributing
Contributions to this project are welcome. If you find any issues or have improvements to suggest, please create a pull request or open an issue.

## License
This project is licensed under the MIT License.