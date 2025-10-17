import json
import subprocess
import numpy as np
from collections import defaultdict

# 실행 설정
KATAGO_PATH = "./katago"
MODEL_PATH = "../../models/kata1-b28c512nbt-s8476434688-d4668249792.bin"
CONFIG_PATH = "analysis.cfg"
EVAL_FILE = "eval_input.jsonl"

def load_eval_queries(jsonl_path):
    print(f"📥 '{jsonl_path}' 파일 로드 중...")
    with open(jsonl_path, "r") as f:
        lines = [json.loads(line.strip()) for line in f if line.strip()]
    print(f"✅ 총 {len(lines)}개의 분석 요청 로드 완료\n")
    return lines

def run_katago_analysis_batch(queries):
    print("🧠 KataGo 실행 중... (모든 요청 일괄 분석)")
    process = subprocess.Popen(
        [KATAGO_PATH, "analysis", "-model", MODEL_PATH, "-config", CONFIG_PATH],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True
    )

    for i, query in enumerate(queries, 1):
        json_str = json.dumps(query)
        process.stdin.write(json_str + "\n")
        if i % 10 == 0 or i == len(queries):
            print(f"  ↳ 요청 전송 {i}/{len(queries)}")
    process.stdin.flush()
    process.stdin.close()

    results = {}
    for line in process.stdout:
        if line.strip().startswith("{") and '"id"' in line:
            data = json.loads(line)
            id_ = data["id"]
            winrate = data["rootInfo"]["winrate"]
            results[id_] = winrate
            print(f"    🟢 받은 응답: {id_} → Winrate={winrate:.4f}")
    process.stdout.close()
    process.wait()
    print("\n✅ 모든 응답 수신 완료!\n")
    return results

def summarize_by_move(id_winrate_dict):
    grouped = defaultdict(list)
    for id_, winrate in id_winrate_dict.items():
        move = id_.split("_")[0]
        grouped[move].append(winrate)

    summary = []
    for move, winrates in grouped.items():
        avg = np.mean(winrates)
        std = np.std(winrates)
        summary.append((move, avg, std, len(winrates)))

    # 평균 승률 기준 내림차순 정렬
    summary.sort(key=lambda x: x[1], reverse=True)

    print("[착점별 평균 승률 및 표준편차]")
    for move, avg, std, count in summary:
        print(f"▶ {move}: 평균 = {avg*100:.2f}%, 표준편차 = {std*100:.2f}% ({count}회)")

    # Human Spot 선정
    best_move = summary[0][0]
    print(f"\n🧠 Human Spot = {best_move}")

if __name__ == "__main__":
    queries = load_eval_queries(EVAL_FILE)
    results = run_katago_analysis_batch(queries)
    summarize_by_move(results)