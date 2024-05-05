import requests


class Connector:
    def send_command(self, cmd):
        return requests.post('http://192.168.162.238:6666/command', json={'cmd': cmd}).json()

    def send_grip_book_command(self, marker_id):
        return requests.post('http://192.168.162.238:6666/grip_book', json={'marker_id': marker_id}).json()


if __name__ == '__main__':
    connector = Connector()
    connector.send_command("detect_marker")
    connector.send_command("grip_up_book_0")
