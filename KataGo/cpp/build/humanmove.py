from humanspot import get_winrate_candidates
from convert import convert_result_to_jsonl  # 따로 py 파일에 저장했다면
import json
import subprocess
import numpy as np
import copy
import time

# ------------------------ 설정 ------------------------
KATAGO_PATH = "./katago"
MODEL_PATH = "../../models/kata1-b28c512nbt-s8476434688-d4668249792.bin"
HUMAN_MODEL_PATH = "../../models/b18c384nbt-humanv0.bin.gz"
CONFIG_PATH = "human_9d.cfg"

'''
with open("moves.json", "r", encoding="utf-8") as f:
    INPUT_MOVES = json.load(f)
'''   
'''
INPUT_MOVES = [
    ["B", "D4"],
    ["W", "Q4"],
    ["B", "Q16"],
    ["W", "D16"],
    ["B", "C14"],
    ["W", "F17"],
    ["B", "C16"],
    ["W", "C17"],
    ["B", "B17"],
    ["W", "C15"],
    ["B", "B16"],
    ["W", "D15"],
    ["B", "B15"],
    ["W", "D14"],
    ["B", "C13"],
    ["W", "C3"],
    ["B", "C4"],
    ["W", "D3"],
    ["B", "E4"],
    ["W", "F2"],
    ["B", "O3"],
    ["W", "D13"]
]
'''

INPUT_MOVES= [
    ["B", "Q4"],
    ["W", "D16"],
    ["B", "D4"],
    ["W", "Q16"],
    ["B", "R17"],
    ["W", "Q17"],
    ["B", "R16"],
    ["W", "Q15"],
    ["B", "S14"],
    ["W", "R3"],
    ["B", "R4"],
    ["W", "Q3"],
    ["B", "P4"],
    ["W", "O2"],
    ["B", "C14"],
    ["W", "F17"],
    ["B", "C16"],
    ["W", "C17"],
    ["B", "B17"],
    ["W", "C15"],
    ["B", "B16"],
    ["W", "D15"],
    ["B", "B15"],
    ["W", "D14"],
    ["B", "C13"],
    ["W", "D13"]
]


# ------------------------ 사용자 파라미터 ------------------------
ROLLOUT_STEPS = 6
NUM_TRIALS = 100
THRESHOLD = 0.02
MAX_CANDIDATES = 5
# -------------------------------------------------------

class KataGoServer:
    def __init__(self):
        self.process = subprocess.Popen(
            [KATAGO_PATH, "analysis", "-model", MODEL_PATH, "-human-model", HUMAN_MODEL_PATH, "-config", CONFIG_PATH],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            universal_newlines=True,
            bufsize=1
        )

    def send_query(self, query):
        json_str = json.dumps(query)
        self.process.stdin.write(json_str + "\n")
        self.process.stdin.flush()
        while True:
            line = self.process.stdout.readline()
            if line.startswith('{') and '"id"' in line:
                return json.loads(line)

    def close(self):
        self.process.terminate()

def index_to_gtp(idx):
    col = idx % 19
    row = idx // 19
    col_letter = "ABCDEFGHJKLMNOPQRST"[col]
    row_number = str(19 - row)
    return col_letter + row_number

def sample_from_human_policy(policy):
    probs = np.array(policy)
    probs[probs < 0] = 0
    probs = probs / probs.sum()
    idx = np.random.choice(len(probs), p=probs)
    return idx, index_to_gtp(idx), probs[idx]

def rollout(server, base_input, steps=5):
    data = copy.deepcopy(base_input)
    moves = data["moves"]
    for _ in range(steps):
        data["analyzeTurns"] = [len(moves)]
        response = server.send_query(data)
        idx, move_str, prob = sample_from_human_policy(response["humanPolicy"])
        player = "B" if len(moves) % 2 == 0 else "W"
        moves.append([player, move_str])
        data["moves"] = moves
        print(f"{player} {move_str} (π={prob * 100:.1f}%)")

def simulate_rollouts(server, base_input, steps=8, trials=50):
    rollout_results = []
    for i in range(trials):
        print(f"[{i+1}/{trials}] Rollout 시작...")
        data = copy.deepcopy(base_input)
        moves = data["moves"][:]
        for step in range(steps):
            data["analyzeTurns"] = [len(moves)]
            response = server.send_query(data)
            idx, move_str, prob = sample_from_human_policy(response["humanPolicy"])
            player = "B" if len(moves) % 2 == 0 else "W"
            moves.append([player, move_str])
            data["moves"] = moves
            print(f"  {player} {move_str} (π={prob * 100:.1f}%)")
        rollout_results.append(moves[:])
        print(f"[{i+1}/{trials}] 완료된 수순 길이: {len(moves)} 수\n")
    return rollout_results

def run_human_rollouts():

    input_moves, candidates = get_winrate_candidates(
    input_moves=INPUT_MOVES,
    threshold=THRESHOLD,
    max_candidates=MAX_CANDIDATES
    )

    print("\n[현재 바둑판 수순]")
    for i, (player, move) in enumerate(input_moves, 1):
        print(f"{i}. {player} {move}")

    print("\n[후보 수 리스트]")
    for i, move in enumerate(candidates, 1):
        print(f"{i}. Move: {move}")

    all_rollouts = {}
    server = KataGoServer()
    try:
        for i, move in enumerate(candidates, 1):
            print(f"\n===== {i}번째 후보: {move} {NUM_TRIALS}회 rollout 시작 =====")
            first_player = "B" if len(input_moves) % 2 == 0 else "W"

            base_input = {
                "id": f"rollout_{i}",
                "initialStones": [],
                "moves": input_moves + [[first_player, move]],
                "rules": "japanese",
                "komi": 6.5,
                "boardXSize": 19,
                "boardYSize": 19,
                "analyzeTurns": [len(input_moves) + 1],
                "maxVisits": 50,
                "includePolicy": True,
                "overrideSettings": {
                    "humanSLProfile": "rank_9d"
                }
            }

            rollout_sequences = simulate_rollouts(
                server,
                base_input,
                steps=ROLLOUT_STEPS,
                trials=NUM_TRIALS
            )

            all_rollouts[move] = rollout_sequences
    finally:
        server.close()

    return input_moves, all_rollouts

if __name__ == "__main__":
    input_moves, result = run_human_rollouts()
    convert_result_to_jsonl(result, "eval_input.jsonl")


    print("\n[모든 후보 수에 대한 rollout 결과]")
    for move, sequences in result.items():
        print(f"\n▶ Move: {move} ({len(sequences)}회)")
        for i, seq in enumerate(sequences, 1):
            print(f"  Trial {i}: {seq}")