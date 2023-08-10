import tkinter as tk
from tkinter import ttk, font
import math
import requests
from datetime import timedelta
from skyfield.api import load, EarthSatellite


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.sat_data = None
        self.sat_cords = None
        self.button = None
        self.entry = None
        self.question_menu = None
        self.option_var = None
        self.sat = Satellite()
        self.title("ClearSky")
        self.geometry("1047x720")
        self.map_image = tk.PhotoImage(file="../img/world_map.png")
        self.iss_image = tk.PhotoImage(file="../img/iss.png")
        self.satellite_image = tk.PhotoImage(file="../img/satellite.png")
        self.image_label = None
        self.sat_dot = None
        self.sat_id = None
        self.canvas = None
        self.sat_pass = []
        self.image_x = 840
        self.image_y = 720
        self.setup_ui()
        self.localization_coordinates = {"Warsaw": "52N,21E", "Melbourne": "37S,144E",
                                         "Recife": "8S,35W", "Chicago": "42N,87W"}
        self.update_satellite_position()

    def setup_ui(self):
        self.canvas = tk.Canvas(self, width=840, height=720)
        self.canvas.grid(row=0, column=0, rowspan=45)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.map_image)
        self.location_dot("52N,21E")
        custom_font = font.Font(family="Helvetica", size=19)
        label = tk.Label(self, text="Satellite Live Tracker", font=custom_font)
        label.grid(row=0, column=1, pady=10)
        separator = tk.Canvas(self, width=150, height=2, highlightthickness=0, bg="gray")
        separator.grid(row=1, column=1)
        label_loc = tk.Label(self, text="Choose location:")
        label_loc.grid(row=2, column=1)
        options_list = ["Warsaw", "Melbourne", "Recife", "Chicago"]
        self.option_var = tk.StringVar(self)
        self.question_menu = tk.ttk.OptionMenu(self, self.option_var,
                                               options_list[0], *options_list, command=self.localization_changed)
        self.question_menu.grid(row=3, column=1)
        label_ent = tk.Label(self, text="Enter NORAD ID:")
        label_ent.grid(row=4, column=1)
        self.entry = tk.Entry(self)
        self.entry.grid(row=5, column=1)
        self.button = tk.Button(self, text="Search satellite", command=self.process_satellite_data)
        self.button.grid(row=7, column=1)
        separator = tk.Canvas(self, width=200, height=2, highlightthickness=0, bg="grey")
        separator.grid(row=8, column=1, pady=30)
        self.label_empty1 = tk.Label(self, text="")
        self.label_empty2 = tk.Label(self, text="")
        self.label_norad_id = tk.Label(self, text="")
        self.label_norad_id.grid(row=9, column=1)
        self.label_sat_name = tk.Label(self, text="")
        self.label_sat_name.grid(row=10, column=1)
        self.label_sat_class = tk.Label(self, text="")
        self.label_sat_class.grid(row=11, column=1)
        self.label_empty1.grid(row=12, column=1)
        self.label_sat_start = tk.Label(self, text="")
        self.label_sat_start.grid(row=13, column=1)
        self.label_empty2.grid(row=14, column=1)
        self.label_math_data = tk.Label(self, text="")
        self.label_math_data.grid(row=15, column=1)


    def localization_changed(self, *args):
        self.canvas.delete(self.image_label)
        self.location_dot(self.localization_coordinates[self.option_var.get()])

    def location_dot(self, coordinate):
        latitude, longitude = coordinate.split(",")
        cords_x, cords_y = self.merkator_projection(latitude, longitude, self.image_x, self.image_y)
        dot_loc = [cords_x - 7, cords_y - 7, cords_x + 7, cords_y + 7]
        self.image_label = self.canvas.create_oval(dot_loc, fill="red")

    def merkator_projection(self, lat, lon, map_width, map_height):
        if "N" in lat:
            lat = (int(lat[:-1]))
        else:
            lat = -(int(lat[:-1]))
        if "E" in lon:
            lon = (int(lon[:-1]))
        else:
            lon = -(int(lon[:-1]))
        x = (lon + 180) * (map_width / 360)
        y = (map_height / 2) - (map_width * math.log(math.tan((math.pi / 4) + (lat * math.pi / 360))) / (2 * math.pi))
        return int(x), int(y)

    def process_satellite_data(self):
        self.sat_id = self.read_entry_value()
        self.sat = Satellite()
        self.sat.sat_info = None
        self.sat_data = self.sat.get_satellite_data(self.sat_id)
        if self.sat_data['tle'] == "":
            self.label_norad_id.config(text="Wrong NORAD ID", fg="red")
            return None
        self.get_info_sat()
        self.sat_cords = self.sat.calculate_satellite_position(self.sat_data)
        self.draw_satellite_on_map(self.sat_cords)
        mapped_point = self.sat.predict_pass(self.sat_data)
        transformed_points = [self.refactor_minus_coordinates((x, y)) for x, y in mapped_point]
        points_to_line = [self.merkator_projection(x, y, self.image_x, self.image_y) for x, y in transformed_points]
        part1, part2 = self.split_list(points_to_line)
        for elm in self.sat_pass:
            self.canvas.delete(elm)
        self.draw_pass(part1)
        self.draw_pass(part2)

    def get_info_sat(self):
        self.label_norad_id.config(text=f"SAT ID: \n{self.sat_data['info']['satid']}", fg="white")
        self.label_sat_name.config(text=f"SAT NAME: \n{self.sat_data['info']['satname']}", fg="white")
        if self.sat_data['tle'][7:8] == "U":
            self.label_sat_class.config(text="CLASS: \nunclassified", fg="white")
        if self.sat_data['tle'][7:8] == "U":
            self.label_sat_class.config(text="CLASS: \nunclassified", fg="white")
        if self.sat_data['tle'][7:8] == "C":
            self.label_sat_class.config(text="CLASS: \nclassified", fg="white")
        if self.sat_data['tle'][7:8] == "S":
            self.label_sat_class.config(text="CLASS: \nsecret", fg="white")
        if 50 < int(self.sat_data['tle'][9:11]) <= 99:
            year_of_start = f"19{self.sat_data['tle'][9:11]}"
        else:
            year_of_start = f"20{self.sat_data['tle'][9:11]}"
        self.label_sat_start.config(text=f"DAY OF LAUNCH:\n{self.sat_data['tle'][11:14]}\n"
                                         f"YEAR OF LAUNCH:\n{year_of_start}\n"
                                         f"PIECE OF LAUNCH:\n{self.sat_data['tle'][14:18].split(' ')[0]}",
                                    fg="white")
        self.label_math_data.config(text=f"INCLINATION:\n{self.sat_data['tle'][79:87]}°\n"
                                         f"RIGHT ASCENSION:\n{self.sat_data['tle'][89:96]}°\n"
                                         f"ARGUMENT OF PERIGEE:\n{self.sat_data['tle'][106:113]}°\n"
                                         f"REVOLUTION PER DAY:\n{self.sat_data['tle'][123:134]}\n"
                                         f"REVOLUTION FROM START:\n{self.sat_data['tle'][134:139]}", fg="white")

    def split_list(self, points):
        for i, point in enumerate(points):
            if (points[i + 1][0] - points[i][0]) > 800 or (points[i + 1][0] - points[i][0]) < -800:
                return points[:i], points[i + 1:]
        return points, []

    def read_entry_value(self):
        value = self.entry.get()
        return value

    def draw_satellite_on_map(self, coordinate):
        self.canvas.delete(self.sat_dot)
        coordinate = self.refactor_minus_coordinates(coordinate)
        latitude, longitude = coordinate
        cords_x, cords_y = self.merkator_projection(latitude, longitude, self.image_x, self.image_y)
        if self.sat_id == "25544":
            self.sat_dot = self.canvas.create_image(cords_x - 25, cords_y - 15, anchor=tk.NW, image=self.iss_image)
        else:
            self.sat_dot = self.canvas.create_image(cords_x - 25, cords_y - 25, anchor=tk.NW,
                                                    image=self.satellite_image)
        self.canvas.update()

    def update_satellite_position(self):
        if self.sat_id is not None:
            sat_data = self.sat.get_satellite_data(self.sat_id)
            if self.sat_data['tle'] == "":
                self.label_norad_id.config(text="Wrong NORAD ID", fg="red")
                return None
            sat_cords = self.sat.calculate_satellite_position(sat_data)
            self.draw_satellite_on_map(sat_cords)
        self.after(5000, self.update_satellite_position)

    def draw_pass(self, mapped_points):
        self.sat_pass.append(self.canvas.create_line(mapped_points, smooth=True, fill="yellow", width=2))

    def refactor_minus_coordinates(self, coordinate):
        latitude, longitude = coordinate
        if latitude < 0:
            latitude = str(int(abs(latitude))) + "S"
        else:
            latitude = str(int(latitude)) + "N"
        if longitude < 0:
            longitude = str(int(abs(longitude))) + "W"
        else:
            longitude = str(int(longitude)) + "E"
        return latitude, longitude


class ApiService:
    def __init__(self):
        pass

    def call(self, sat_number):
        response = requests.get(
            f"https://api.n2yo.com/rest/v1/satellite/tle/{sat_number}&apiKey=HABQJE-75QA93-HYUNQD-53DC")
        return response.json()


class Satellite:
    def __init__(self):
        self.sat_info = None

    def get_tle(self, sat_number):
        api = ApiService()
        return api.call(sat_number)

    def get_satellite_data(self, sat_id):
        if self.sat_info is None:
            self.sat_info = self.get_tle(sat_id)
        return self.sat_info

    def predict_pass(self, sat_data):
        line1, line2 = sat_data['tle'].split("\r\n")
        ts = load.timescale()
        satellite = EarthSatellite(line1, line2, 'SAT', ts)
        prediction_route = []
        for il in range(1, 300):
            now = ts.now() + timedelta(seconds=20 * il)
            geocentric = satellite.at(now)
            subpoint = geocentric.subpoint()
            latitude = subpoint.latitude.degrees
            longitude = subpoint.longitude.degrees
            prediction_route.append((latitude, longitude))
        return prediction_route

    def calculate_satellite_position(self, sat_data):
        line1, line2 = sat_data['tle'].split("\r\n")
        ts = load.timescale()
        satellite = EarthSatellite(line1, line2, 'SAT', ts)
        now = ts.now()
        geocentric = satellite.at(now)
        subpoint = geocentric.subpoint()
        latitude = subpoint.latitude.degrees
        longitude = subpoint.longitude.degrees
        return latitude, longitude


if __name__ == "__main__":
    app = App()
    app.mainloop()
