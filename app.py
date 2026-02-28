import os

from flask import Flask, request

from okd4.okd4 import push_to_dockerhub, okd4_login

app = Flask(__name__)


@app.route('/push-image-to-dockerhub', methods=['POST'])
def post_image_to_dockerhub():
    try:
        data = request.get_json()
        image_and_tag = data.get('image', 'no_image_passed')
        dockerfile = data.get('dockerfile', None)
        push_to_dockerhub(image_and_tag, dockerfile)
        return {'status': 'success'}, 200
    except Exception as e:
        return {'status': "error", "message": str(e)}, 500


if os.getenv('ENABLE_LOGIN_ENDPOINT') == 'true':
    @app.route('/login', methods=['POST'])
    def login():
        try:
            data = request.get_json()
            username = data.get('username', None)
            password = data.get('password', None)
            server = data.get('server', None)
            okd4_login(username, password, server)
            return {'status': 'success'}, 200
        except Exception as e:
            return {'status': "error", "message": str(e)}, 500


if __name__ == '__main__':
    app.run()
