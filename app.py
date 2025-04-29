from flask import Flask, render_template, jsonify, request
import random
import time

app = Flask(__name__)

current_game = {
    'number': None,
    'sequence': [],
    'start_time': None,
    'steps': 0
}

history = []

def get_next_number(n):
    if n % 2 == 0:
        return n // 2
    else:
        return 3 * n + 1

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_random')
def start_random():
    current_game['number'] = random.randint(1, 1000)
    current_game['sequence'] = [current_game['number']]
    current_game['start_time'] = time.time()
    current_game['steps'] = 0
    return jsonify({
        'number': current_game['number'],
        'sequence': current_game['sequence']
    })

@app.route('/start_custom', methods=['POST'])
def start_custom():
    number = int(request.json['number'])
    if number <= 0:
        return jsonify({'error': 'Число должно быть положительным'}), 400

    current_game['number'] = number
    current_game['sequence'] = [number]
    current_game['start_time'] = time.time()
    current_game['steps'] = 0
    return jsonify({
        'number': current_game['number'],
        'sequence': current_game['sequence']
    })

@app.route('/check_answer', methods=['POST'])
def check_answer():
    answer = int(request.json['answer'])
    next_number = get_next_number(current_game['number'])

    if answer == next_number:
        current_game['number'] = next_number
        current_game['sequence'].append(next_number)
        current_game['steps'] += 1

        if next_number == 1:
            game_time = time.time() - current_game['start_time']
            history.append({
                'start': current_game['sequence'][0],
                'steps': current_game['steps'],
                'time': game_time,
                'sequence': current_game['sequence']
            })
            return jsonify({
                'correct': True,
                'game_over': True,
                'sequence': current_game['sequence'],
                'time': game_time
            })

        return jsonify({
            'correct': True,
            'next_number': next_number,
            'sequence': current_game['sequence']
        })
    else:
        return jsonify({
            'correct': False,
            'expected': next_number
        })

@app.route('/history')
def get_history():
    return jsonify(history)

@app.route('/reset_history', methods=['POST'])
def reset_history():
    data = request.json
    if data.get('password') == 'qwerty12345':
        global history
        history = []
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Неверный пароль'}), 403

@app.route('/get_sequence', methods=['POST'])
def get_sequence():
    number = int(request.json['number'])
    seq = []
    n = number
    while n != 1:
        seq.append(n)
        n = get_next_number(n)
    seq.append(1)
    return jsonify({'sequence': seq})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
