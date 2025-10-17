import subprocess
import json

# 고정된 실행 설정
KATAGO_PATH = "./katago"
MODEL_PATH = "../../models/kata1-b28c512nbt-s8476434688-d4668249792.bin"
CONFIG_PATH = "analysis.cfg"
'''
input_moves= [
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
    ["B", "R13"],
    ["W", "C6"],
    ["B", "F3"],
    ["W", "C4"],
    ["B", "C3"],
    ["W", "B3"],
    ["B", "B2"],
    ["W", "B4"],
    ["B", "D3"],
    ["W", "D5"],
    ["B", "N3"],
    ["W", "O3"],
    ["B", "O4"],
    ["W", "M3"],
    ["B", "N2"],
    ["W", "M2"],
    ["B", "N4"],
    ["W", "N1"],
    ["B", "J3"],
    ["W", "Q13"],
    ["B", "Q12"],
    ["W", "P12"],
    ["B", "Q11"],
    ["W", "P11"],
    ["B", "P10"],
    ["W", "O10"],
    ["B", "O9"],
    ["W", "N10"],
    ["B", "P9"],
    ["W", "R14"],
    ["B", "S13"],
    ["W", "K16"],
    ["B", "C14"],
    ["W", "D14"],
    ["B", "D13"],
    ["W", "E14"],
    ["B", "C16"],
    ["W", "C17"],
    ["B", "C15"],
    ["W", "D17"],
    ["B", "C10"],
    ["W", "D11"],
    ["B", "E13"],
    ["W", "F13"],
    ["B", "F12"],
    ["W", "E12"],
    ["B", "C12"],
    ["W", "G13"],
    ["B", "F11"],
    ["W", "D10"],
    ["B", "C9"],
    ["W", "D9"],
    ["B", "D8"],
    ["W", "E8"],
    ["B", "C8"],
    ["W", "E7"],
    ["B", "H11"],
    ["W", "G10"],
    ["B", "J12"],
    ["W", "H12"],
    ["B", "G11"],
    ["W", "J13"],
    ["B", "J11"],
    ["W", "K13"],
    ["B", "H8"]
]
'''

input_moves= [
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

def get_winrate_candidates(input_moves, threshold=0.02, max_candidates=10):
    """
    KataGo 분석 실행 및 승률 Top 착점 추출 (한 줄 JSON 형식 대응)

    Args:
        input_moves (list): [["B", "D4"], ["W", "Q16"]] 형식의 수순
        threshold (float): Top1 수와 승률 차이가 threshold 이상인 수는 제외
        max_candidates (int): 출력할 최대 착점 수

    Returns:
        tuple: (input_moves, top_moves)
    """
    query = {
        "id": "final_eval",
        "initialStones": [],
        "moves": input_moves,
        "rules": "japanese",
        "komi": 6.5,
        "boardXSize": 19,
        "boardYSize": 19,
        "analyzeTurns": [len(input_moves)],
        "maxVisits": 5000,
        "includePolicy": True
    }

    input_line = json.dumps(query)  # JSON 한 줄 문자열로 변환
    process = subprocess.Popen(
        [KATAGO_PATH, "analysis", "-model", MODEL_PATH, "-config", CONFIG_PATH],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        universal_newlines=True
    )
    stdout, _ = process.communicate(input=input_line + "\n")

    katago_json = None
    for line in stdout.strip().split('\n'):
        try:
            obj = json.loads(line)
            if "moveInfos" in obj:
                katago_json = obj
                break
        except json.JSONDecodeError:
            continue
    if katago_json is None:
        raise RuntimeError("KataGo 분석 JSON 응답을 찾을 수 없습니다.")

    move_infos = katago_json["moveInfos"]
    moves_and_wr = sorted([(m["move"], m["winrate"]) for m in move_infos], key=lambda x: x[1], reverse=True)
    if not moves_and_wr:
        raise ValueError("분석 결과에서 착점을 찾지 못했습니다.")

    top1_wr = moves_and_wr[0][1]
    filtered = [(m, wr) for m, wr in moves_and_wr if top1_wr - wr <= threshold]
    top_k = filtered[:max_candidates]

    print(f"📈 Top {len(top_k)} 착점 (Top1 대비 {threshold*100:.1f}% 이내):")
    for i, (move, winrate) in enumerate(top_k, start=1):
        print(f"{i:2d}. Move: {move:4s} | Winrate: {winrate*100:.2f}%")

    top_moves = [m for m, _ in top_k]
    return input_moves, top_moves

if __name__ == "__main__":

    input_moves, top_moves = get_winrate_candidates(input_moves, threshold=0.02, max_candidates=10)
