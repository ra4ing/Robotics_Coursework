import time

from flask import Flask, request
from Camera import Camera
from Arm import Arm

app = Flask(__name__)
arm = Arm()
camera = Camera()


@app.route('/command', methods=['POST'])
def command():
    result = "no such cmd!"
    cmd = request.json.get('cmd')
    if cmd == 'over?':
        if shelf == 4:
            return {'output': '', 'over': True}
        else:
            return {'output': '', 'over': False}



    elif cmd == 'grip_up_book_0':
        arm.grip_book_0()
        arm.send_book()
        arm.set_init_angle()
        result = 'picked up book: 0'

    elif cmd == 'grip_up_book_1':
        arm.grip_book_1()
        arm.send_book()
        arm.set_init_angle()
        result = 'picked up book: 1'

    elif cmd == 'grip_up_book_2':
        arm.grip_book_2()
        arm.send_book()
        arm.set_init_angle()
        result = 'picked up book: 2'

    elif cmd == 'grip_up_book_3':
        arm.grip_book_3()
        arm.send_book()
        arm.set_init_angle()
        result = 'picked up book: 3'

    elif cmd == 'detect_marker':
        camera.detect_marker()
        result = 'detecting...'

    elif cmd == 'have_marker?':
        if camera.have_marker:
            result = True
        else:
            result = False

    elif cmd == 'start_detect':
        arm.set_detect_state_angle()
        result = 'started detecting'

    return {'output': result, 'marker_id': camera.marker_id}


@app.route('/grip_book', methods=['POST'])
def grip_book():
    id_array = []
    result = ''
    marker_id = request.json.get('marker_id')

    arm.detect_book_0()
    camera.detect_marker()
    print(camera.marker_id, marker_id)
    if camera.marker_id == marker_id:
        result = 'detected book'
        arm.grip_book_0()
        arm.send_book()
        arm.set_init_angle()
        id_array.append(0)

    arm.detect_book_1()
    camera.detect_marker()
    print(camera.marker_id, marker_id)
    if camera.marker_id == marker_id:
        result = 'detected book'
        arm.grip_book_1()
        arm.send_book()
        arm.set_init_angle()
        id_array.append(1)

    arm.detect_book_2()
    camera.detect_marker()
    print(camera.marker_id, marker_id)
    if camera.marker_id == marker_id:
        result = 'detected book'
        arm.grip_book_2()
        arm.send_book()
        arm.set_init_angle()
        id_array.append(2)

    arm.detect_book_3()
    camera.detect_marker()
    print(camera.marker_id, marker_id)
    if camera.marker_id == marker_id:
        result = 'detected book'
        arm.grip_book_3()
        arm.send_book()
        arm.set_init_angle()
        id_array.append(3)

    if result == '':
        result = 'no correct book'

    arm.set_init_angle()

    return {'output': result, 'id_array': id_array}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6666)

# result = subprocess.check_output(cmd, shell=True)
