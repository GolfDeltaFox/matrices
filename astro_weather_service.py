from bs4 import BeautifulSoup
import numpy as np
from PIL import Image, ImageFont,ImageDraw
import requests
import io
from io import BytesIO

class AstroWeatherService:
    def __init__(self):
        self.ui_spec = [
            {'name':'hours', 'type': 'std', 'cmap': self.hours_cmap},
            {'name':'High Clouds (% Sky Obscured)', 'type': 'std', 'cmap': self.cloud_cmap},
            {'name':'Medium Clouds (% Sky Obscured)', 'type': 'std', 'cmap': self.cloud_cmap},
            {'name':'Low Clouds (% Sky Obscured)', 'type': 'std', 'cmap': self.cloud_cmap},
            {'name':'Visibility (miles)', 'type': 'std', 'cmap': self.vis_cmap},
            {'name':'Wind Speed/Direction (mph)', 'type': 'std', 'cmap': self.wind_cmap},
            {'name':'Precipitation Probability (%)', 'type': 'std', 'cmap': self.rain_cmap},
            {'name':'Precipitation Amount (mm)', 'type': 'std', 'cmap': self.rainmm_cmap},
            {'name':'Dew Point (°C)', 'type': 'std', 'cmap': self.temp_cmap},
            {'name':'Temperature (°C)', 'type': 'std', 'cmap': self.temp_cmap}
        ]
        
    @classmethod
    def get_li_hour(cls, li):
        return int(li.text.split(' ')[1])

    @classmethod
    def get_hours(cls, forecast_div, day=0):
        fc_hour_rating_div  = forecast_div.find_all('div', class_='fc_hour_ratings')[day]
        hours_lis = fc_hour_rating_div.ul.find_all('li')
        return [cls.get_li_hour(li) for li in hours_lis]



    @classmethod
    def detail_row_2_json(cls, detail_row):
        string_types = ['Precipitation Type']
        name = detail_row.find('span', class_='fc_detail_label').span.text
        lis = detail_row.ul.find_all('li')
        if name in string_types:
            data = [x.text for x in lis]
        else:
            data = [float(x.text) if x.text else None for x in lis]

        # print(name)
        return {name:data}


    @classmethod
    def merge_days(cls, data):
        result = data['days'][0]
        for day in data['days'][1:]:
            for k, v in day.items():
                result[k] = result[k]+v
        return result

    @classmethod
    def cloud_cmap(cls, x):
        return [x/100*255, x/100*255, 190]

    @classmethod
    def vis_cmap(cls, x, max_=10):
        x = min(x, max_)
        x = x/max_
        # return [255-(x/100*255), x/100*255, 0]
        return [255*(1-x), 255*(1-x), 255*(1-x)]

    @classmethod
    def wind_cmap(cls, x, max_=40):
        if x >= max_:
            return [255, 0, 0]
        x = min(x, max_)
        pc = x/max_*255
        return [pc, pc, pc]

    @classmethod
    def rain_cmap(cls, x):
        if x < 2:
            return [0, 154, 8]
        elif x < 20:
            return [30, 30, 100]
        elif x < 80:
            return [30, 30, 200]
        else:
            return [30, 30, 255]

    @classmethod
    def rainmm_cmap(cls, x):
        if x < .1:
            return [7, 49, 0]
        elif x < 1:
            return [30, 30, 200]
        else:
            return [30, 30, 255]

    @classmethod
    def temp_cmap(cls, x, min_=-10, max_=30):
        x = min(x, max_)
        x = max(x, min_)
        x = (x-min_)/(max_-min_)
        return [x*255, x*180, 255*(1-x)]

    @classmethod
    def hours_cmap(cls, x):
        if x==0:
            return [200,100,100]
        elif x % 6 == 0:
            return [150,150,100]
        else:
            return [0,0,0]


    @classmethod
    def generate_image(cls, data, UI_spec, x_max=64):
        matrix = []
        # print(data)
        for row in UI_spec:
            values = np.array(data[row['name']])[:x_max]
            cmap = row['cmap']
            row_pixels = list(map(cmap, values))
            matrix.append(row_pixels)
        mat = np.array(matrix, dtype=np.uint8)
        return Image.fromarray(mat, 'RGB')

    def parse_forecast_data(self, forecast_div):
        days_divs = forecast_div.find_all("div", class_="fc_day")
        days = []
        for days_div in days_divs:
            detail_row_divs = days_div.find_all("div", class_="fc_detail_row")
            days.append(detail_row_divs)
        data = {'days':[]}
        for i, day in enumerate(days):
            res_days = []
            for detail_row_div in day:
                res_day = self.detail_row_2_json(detail_row_div)
                res_day['hours'] = self.get_hours(forecast_div, i)
                res_days.append(res_day)
            data['days'].append({k: v for d in res_days for k, v in d.items()})
        data = self.merge_days(data)
        return data


    def retrieve_forcast(self, longitude, latitude):
        url = f"https://clearoutside.com/forecast/{longitude}/{latitude}"
        r = requests.get(url)
        soup = BeautifulSoup(r.content, "html.parser")
        forecast_div = soup.body.find("div", id="forecast")
        return forecast_div

    def plot_moon(self, forecast_div):
        moon_perc = forecast_div.find("span", class_="fc_moon_percentage").text
        moon_perc = int(moon_perc.rstrip('%'))
        if moon_perc < 10:
            return Image.open("./img/moon/0.png")
        elif moon_perc < 40:
            return Image.open("./img/moon/25.png")
        elif moon_perc < 60:
            return Image.open("./img/moon/50.png")
        elif moon_perc < 90:
            return Image.open("./img/moon/75.png")
        else:
            return Image.open("./img/moon/100.png")

    def plot_temp(self, forecast_data):
        out = Image.new("RGBA", (18, 8), (0, 0, 0, 0))
        d = ImageDraw.Draw(out)
        font = ImageFont.truetype("pixelated.ttf", 8)
        temp_value = int(forecast_data['Temperature (°C)'][0])
        d.multiline_text((0, 0), f"{temp_value}C", font=font, fill=(200, 200, 200))
        # print(forecast_data['Temperature (°C)'][0])
        return out

    @classmethod
    def paste(cls, orig, source, x, y):
        s_y, s_x, _ = orig.shape
        source[y:y+s_y, x:s_x] = orig
        return source


    def parse_card(self, object_card):
        name = object_card.find_all('div')[0].a.b.text.split(' / ')[0]
        img_url = object_card.find('img', class_='img-circle')['src']
        magnitude = object_card.find('span', title='Magnitude').text.split(' ')[-1]
        size = object_card.find('span', title='Apparent size').text.split(' ')[-1].replace('°','')
        return (name, img_url, magnitude, size)
        
    def filter_objects(self, object_cards, out=['Open Cluster']):
        res = []
        for object_card in object_cards:
            object_type = object_card.find_all("div")[1].small.b.text
            if object_type not in out:
                res.append(object_card)
        return res

    def object_image(self, object_tuple, h=22, w=47):
        name, img_url, magnitude, size = object_tuple
        font = ImageFont.truetype("pixelated.ttf", 8)
        out = Image.new("RGBA", (60, h), (0, 0, 0, 255))
        d = ImageDraw.Draw(out)
        image_req = requests.get(img_url)
        img = Image.open(BytesIO(image_req.content))
        img = img.resize((w, w), Image.Resampling.NEAREST)
        img = img.crop((0, int((w-h)/2), w, int((w-h)/2)+h))
        out.paste(img, (0,0))
        d.multiline_text((0, 12), name, font=font, fill=(200, 200, 200))
        d.multiline_text((0, 0), 'M:'+magnitude, font=font, fill=(200, 200, 200))
        d.multiline_text((0, 6), size, font=font, fill=(200, 200, 200))
        return out

    def retrieve_object(self):
        url = f"https://sky-tonight.com/?sort=alt"
        r = requests.get(url)
        soup = BeautifulSoup(r.content, "html.parser")
        print(soup.body)
        object_cards = soup.body.find_all("div", class_="object_card")
        object_cards = self.filter_objects(object_cards)
        object_tuple = self.parse_card(object_cards[0])
        return object_tuple

    def call(self, longitude, latitude, zoom=1):
        forecast_div = self.retrieve_forcast(longitude, latitude)
        object_tuple = self.retrieve_object()
        forecast_data = self.parse_forecast_data(forecast_div)
        forecast_img = self.generate_image(forecast_data, self.ui_spec, x_max=64)
        moon_img = self.plot_moon(forecast_div)
        temp_img = self.plot_temp(forecast_data)
        obj_img = self.object_image(object_tuple)
        # top = np.zeros((24, 64, 0), dtype=np.uint8  )
        result_img = Image.new("RGBA", (64, 32), (0, 0, 0, 255))
        result_img.paste(moon_img, (3,1), moon_img)
        result_img.paste(temp_img, (3,14), temp_img)
        result_img.paste(forecast_img, (0,22))
        result_img.paste(obj_img, (17,0))

        # print(forecast_data)
        # forecast_img = Image.fromarray(forecast_mat, 'RGB')
        # top = self.paste(moon_mat, top, 0, 0)
        # result_mat = np.concatenate([top,forecast_mat])
    # w, h = 64, 3
    # data = np.zeros((h, w, 3), dtype=np.uint8)
    # data[0:2, 0:2] = [137.7 , 137.7 , 255.] # red patch in upper left
        # img = Image.fromarray(result_mat, 'RGB')
        img = result_img
        img = img.resize((img.size[0]*zoom, img.size[1]*zoom), Image.NEAREST)
        b = io.BytesIO()
        img.save(b, 'bmp')
        b.seek(0)
        # fp = io.TextIOWrapper(b)
        return b
    # img = Image.fromarray(data, 'RGB')
    # img.save('my.png')
    # img.show()
    # img.resize((w*20, h*60), Image.NEAREST)