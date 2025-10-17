import matplotlib
matplotlib.use('Agg')  # GUI 없는 환경용 백엔드
import matplotlib.pyplot as plt

# 좌표 변환: 'D4' → (3, 15)
def coord_to_xy(move):
    col_str = "ABCDEFGHJKLMNOPQRST"
    if len(move) < 2 or move[0] not in col_str:
        raise ValueError(f"잘못된 좌표: {move}")
    col = col_str.index(move[0])
    try:
        row = int(move[1:]) - 1  # 상단이 19, 하단이 1 그대로 출력
    except ValueError:
        raise ValueError(f"좌표 숫자 파싱 실패: {move}")
    return col, row

# 바둑판 그리기: 수순만 시각화
def draw_board_from_moves(moves, filename="board_state.png"):
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.set_xticks(range(19))
    ax.set_yticks(range(19))
    ax.set_xticklabels(list("ABCDEFGHJKLMNOPQRST"))
    ax.set_yticklabels(range(1, 20))  # 1~19 위쪽부터 정렬되게
    ax.set_xlim(-0.5, 18.5)
    ax.set_ylim(-0.5, 18.5)
    ax.grid(True)

    # Y축을 반전시켜서 19가 위로 가도록
    ax.invert_yaxis()

    # 바둑판 점선
    for x in range(19):
        for y in range(19):
            ax.plot(x, y, 'k.', markersize=2)

    # 착수 표시
    for i, (color, pos) in enumerate(moves):
        stone_color = 'black' if color == "B" else 'white'
        edge = 'black' if stone_color == 'white' else 'none'
        x, y = coord_to_xy(pos)
        ax.plot(x, y, 'o', markersize=16, color=stone_color, markeredgecolor=edge)
        ax.text(x, y, str(i+1), color='red', fontsize=7, ha='center', va='center')

    ax.set_title("Current Board State")
    plt.tight_layout()
    plt.savefig(filename)
    print(f"✅ 현재 바둑판 이미지 저장 완료: {filename}")

# 예시 실행
if __name__ == "__main__":
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
    ["W", "F8"],
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
    draw_board_from_moves(INPUT_MOVES)