from flask import Flask
from flask import Response
from flask import render_template

class VideoApp:
    PORT = '8000'
    app = Flask(__name__)
    counter = 0

    def __init__(self):
        self.app.add_url_rule('/', 'index', index)
        self.app.add_url_rule('/video_on', 'video_on', self.video_on)
        self.app.add_url_rule('/video_off', 'video_off', self.video_off)

        self.app.run(host='0.0.0.0', port=self.PORT, threaded=True, use_reloader=False)

    def video_on(self):
        self.counter = self.counter + 1
        print(f'helooo!!!! {self.counter}')
        return f' you got a {self.counter}'

    def video_off(self):
        self.counter = 0
        print(f'helooo!!!! {self.counter}')
        return f' you got a {self.counter}'

def index():
    # return the rendered template
    return render_template("index.html")


if __name__ == '__main__':
    vs = VideoApp()