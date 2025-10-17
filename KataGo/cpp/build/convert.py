import json

def convert_result_to_jsonl(result_dict, output_path, komi=6.5):
    """
    rollout 결과(result_dict)를 KataGo analysis용 JSONL 형식으로 변환하여 저장
    각 착점별 trial들을 분석 요청으로 만듦
    """
    with open(output_path, "w") as f:
        for move, sequences in result_dict.items():
            for i, seq in enumerate(sequences, 1):
                query = {
                    "id": f"{move}_{i}",
                    "initialStones": [],
                    "moves": seq,
                    "rules": "japanese",
                    "komi": komi,
                    "boardXSize": 19,
                    "boardYSize": 19,
                    "analyzeTurns": [len(seq)],
                    "maxVisits": 100,
                    "includePolicy": False
                }
                json.dump(query, f)
                f.write("\n")  # JSONL 형식: 한 줄 = 하나의 JSON 객체
    print(f"✅ 저장 완료: {output_path}")