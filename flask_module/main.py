from flask import Flask, render_template, jsonify
import threading, logging

class Main(threading.Thread):
    def __init__(self, game_server_instance):
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR) # Para que flask no de la tabarra en la terminal.

        threading.Thread.__init__(self)
        self.daemon = True
        self.server = game_server_instance
        
        self.app = Flask(__name__, template_folder="views")
        
        self.app.add_url_rule('/api/estado', view_func=self.get_full_state) # Devuelve JSON
        self.app.add_url_rule('/api/puntos', view_func=self.get_scores) # Devuelve JSON
        self.app.add_url_rule('/', view_func=self.index)

    def get_full_state(self):
        return jsonify(self.server.game_state.to_dict())
    
    def get_scores(self):
        scores = self.server.game_state.score
        return jsonify(scores)

    def index(self):
        return render_template('index.html')

    def run(self):
        self.app.run(debug=True, use_reloader=False, port=8000, host="0.0.0.0")