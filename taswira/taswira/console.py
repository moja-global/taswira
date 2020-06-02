from terracotta.server.app import app
from terracotta import update_settings

def start_terracotta():
    app.run(port=5000)

if __name__ == "__main__":
    start_terracotta()