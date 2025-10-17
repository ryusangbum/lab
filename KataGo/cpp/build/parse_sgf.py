import re
import json
import os
import argparse

def parse_sgf_to_input_moves(sgf_path: str):
    """
    SGF 파일 경로를 받아서 input_moves를 반환하는 함수
    반환값: [["B", "D4"], ["W", "Q16"], ...]
    """
    with open(sgf_path, "r", encoding="utf-8") as f:
        sgf_text = f.read()

    moves = []
    sgf_moves = re.findall(r";([BW])\[([a-s]{2})\]", sgf_text)

    for color, coord in sgf_moves:
        col_sgf, row_sgf = coord
        col = ord(col_sgf) - ord('a')
        row = ord(row_sgf) - ord('a')

        # GTP 좌표로 변환 (I 생략 주의)
        gtp_col = chr(ord('A') + col + (1 if col >= 8 else 0))
        gtp_row = str(19 - row)
        move = [color, gtp_col + gtp_row]
        moves.append(move)

    return moves

def save_input_moves_as_json(input_moves, json_path="moves.json"):
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(input_moves, f, indent=2)
    print(f"✅ input_moves 저장 완료: {json_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SGF 파일에서 input_moves 추출 및 moves.json 저장")
    parser.add_argument("--sgf", required=True, help="SGF 파일 경로")
    args = parser.parse_args()

    if not os.path.isfile(args.sgf):
        print(f"❌ 파일이 존재하지 않음: {args.sgf}")
        exit(1)

    input_moves = parse_sgf_to_input_moves(args.sgf)
    print("✅ 추출된 INPUT_MOVES:")
    for move in input_moves:
        print(move)

    save_input_moves_as_json(input_moves)