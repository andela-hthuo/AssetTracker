from app import create_app
app = create_app('FLASK_CONFIG_FILE')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
