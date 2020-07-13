import curses

class TextWindow():
    _screen = None
    _window = None
    _num_lines = None

    def __init__(self, stdscr, lines=20):
        self._screen = stdscr
        self._screen.nodelay(True)
        curses.curs_set(0)

        self._num_lines = lines

    def read_key(self):
        keycode = self._screen.getch()
        return keycode if keycode != -1 else None

    def clear(self):
        self._screen.erase()

    def write_line(self, lineno, message):
        if lineno < 0 or lineno >= self._num_lines:
            raise ValueError('lineno out of bounds')
        height, width = self._screen.getmaxyx()
        y = (height / self._num_lines) * lineno
        x = 5
        for text in message.split('\n'):
            text = text.ljust(width)
            self._screen.addstr(int(y), x, text)
            y += 1

    def refresh(self):
        self._screen.refresh()

    def beep(self):
        curses.flash()


class KeyTeleop():
    _interface = None

    _linear = None
    _angular = None

    def __init__(self, interface):
        self._interface = interface
        self.motor_speed= 1000
        self.img_res = 160
        self.mov_steps = 200
        self.move_single = False
        self.move_speed = 0

        self.servo_pos = [60,False]

        self.LED = True

        self.growLED = False

        self._running = False

        self.temp = 100
        self.hum = None

        self.limit_switch = False
        self.go_home = False
        self.home_cmd = False

        self.additional_text = ""

    def run(self):
        self._linear = 0
        self._running = True
        while self._running is True:
            keycode = self._interface.read_key()
            if keycode:
                if self._key_pressed(keycode):
                    self._publish()
            else:
                self._publish()

    def _key_pressed(self, keycode):

        speed_bindings = {
            curses.KEY_UP: 100,
            curses.KEY_DOWN: -100,
            ord('.'): 500,
            ord(','): -500,
        }
        res_bindings = {
            ord('1'): 160,
            ord('2'): 240,
            ord('3'): 360,
            ord('4'): 480,

        }
        steps_bindings = {
            curses.KEY_RIGHT: 100,
            curses.KEY_LEFT: -100,
        }

        servo_bindings = {
            ord('+'): 5,
            ord('-'): -5,
        }

        stop_bindings = {
            ord(' '): (0, 0),
        }

        single_bindings = {
            ord('m'): True
        }

        if keycode == ord('d'):
            self.LED = not self.LED

        if keycode == ord('g'):
            self.growLED = not self.growLED

        if keycode == ord('q'):
            self._running = False

        if keycode == ord('l'):
            self.move_speed = 1

        if keycode == ord('j'):
            self.move_speed = -1

        if keycode == ord('k'):
            self.move_speed = 0

        if keycode == ord('f'):
            self.mov_steps = -self.mov_steps

        if keycode == ord('h'):
            self.go_home = True
            self.home_cmd = True

        if keycode in speed_bindings:
            acc = speed_bindings[keycode]
            self.motor_speed = self.motor_speed + acc

        if keycode in steps_bindings:
            acc = steps_bindings[keycode]
            self.mov_steps = self.mov_steps + acc

        elif keycode in res_bindings:
            self.img_res = res_bindings[keycode]

        elif keycode in stop_bindings:
            acc = stop_bindings[keycode]
            self.motor_speed = 0

        elif keycode in servo_bindings:
            acc = servo_bindings[keycode]
            self.servo_pos = [self.servo_pos[0]+acc,True]

        elif keycode in single_bindings:
            self.move_single = True

        else:
            return False

        return True

    def _publish(self,add_text):
        self._interface.clear()
        self._interface.write_line(1, f'*** Stepper motor slider control UI ***')
        self._interface.write_line(2, f'Default motor speed: {self.motor_speed} [UP/DOWN or ,/.]')
        self._interface.write_line(3, f'Steps: {self.mov_steps} [LEFT/RIGHT]')
        self._interface.write_line(4, f'Image Resolution: {self.img_res} [1,2,3,4]')
        self._interface.write_line(5, f'Single movement: {self.move_single}')
        self._interface.write_line(6, f'Continuous movement: {self.move_speed}')
        self._interface.write_line(7, f'LED: {self.LED} | Grow LED: {self.growLED}')
        self._interface.write_line(8, f'Servo Position: {self.servo_pos[0]} ({self.servo_pos[1]}) [-/+]')
        self._interface.write_line(9, f'[f]-flip steps [m]-move steps [j,k,l]-move/stop continuous')
        self._interface.write_line(11, f'Temperature: {self.temp} C| Humidity: {self.hum} %')
        self._interface.write_line(12, f'Limit Switch: {self.limit_switch} (Go home? {self.go_home} [h]) ')
        self._interface.write_line(14, add_text)

        self._interface.refresh()

    def update_values(self,temp,hum):
        self.temp = temp
        self.hum = hum


def main(stdscr):

    app = KeyTeleop(TextWindow(stdscr))
    app.run()


if __name__ == '__main__':
    curses.wrapper(main)