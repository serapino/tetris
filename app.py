
import streamlit as st
import random
from streamlit_autorefresh import st_autorefresh

st.set_page_config(
    page_title="테트리스",
    page_icon="🧱",
    layout="centered"
)

st.title("🧱 TETRIS")
st.caption("블록을 움직여 줄을 완성하세요!")

WIDTH = 10
HEIGHT = 20

SHAPES = [
    [[1, 1, 1, 1]],
    [[1, 0, 0], [1, 1, 1]],
    [[0, 0, 1], [1, 1, 1]],
    [[1, 1], [1, 1]],
    [[0, 1, 1], [1, 1, 0]],
    [[0, 1, 0], [1, 1, 1]],
    [[1, 1, 0], [0, 1, 1]]
]

COLORS = [
    "🟦", "🟪", "🟧", "🟨",
    "🟩", "🟥", "🟫"
]


def new_piece():
    index = random.randrange(len(SHAPES))
    return {
        "shape": [row[:] for row in SHAPES[index]],
        "color": COLORS[index],
        "x": 3,
        "y": 0
    }


def init_game():
    st.session_state.board = [
        [0 for _ in range(WIDTH)]
        for _ in range(HEIGHT)
    ]
    st.session_state.piece = new_piece()
    st.session_state.score = 0
    st.session_state.game_over = False


if "board" not in st.session_state:
    init_game()


def valid_move(piece, dx=0, dy=0, shape=None):
    shape = shape or piece["shape"]

    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if not cell:
                continue

            nx = piece["x"] + x + dx
            ny = piece["y"] + y + dy

            if nx < 0 or nx >= WIDTH or ny >= HEIGHT:
                return False

            if ny >= 0 and st.session_state.board[ny][nx]:
                return False

    return True


def lock_piece():
    piece = st.session_state.piece

    for y, row in enumerate(piece["shape"]):
        for x, cell in enumerate(row):
            if cell:
                ny = piece["y"] + y
                nx = piece["x"] + x

                if ny < 0:
                    st.session_state.game_over = True
                    return

                st.session_state.board[ny][nx] = piece["color"]

    clear_lines()

    st.session_state.piece = new_piece()

    if not valid_move(st.session_state.piece):
        st.session_state.game_over = True


def clear_lines():
    board = st.session_state.board

    remaining = [
        row for row in board
        if any(cell == 0 for cell in row)
    ]

    cleared = HEIGHT - len(remaining)

    for _ in range(cleared):
        remaining.insert(0, [0] * WIDTH)

    st.session_state.board = remaining

    points = [0, 100, 300, 500, 800]
    st.session_state.score += points[cleared]


def move(dx, dy):
    piece = st.session_state.piece

    if valid_move(piece, dx, dy):
        piece["x"] += dx
        piece["y"] += dy
    elif dy == 1:
        lock_piece()


def rotate():
    piece = st.session_state.piece

    rotated = [
        list(row)
        for row in zip(*piece["shape"][::-1])
    ]

    if valid_move(piece, shape=rotated):
        piece["shape"] = rotated


def hard_drop():
    while valid_move(st.session_state.piece, dy=1):
        st.session_state.piece["y"] += 1

    lock_piece()


def get_display_board():
    board = [
        row[:] for row in st.session_state.board
    ]

    piece = st.session_state.piece

    if not st.session_state.game_over:
        for y, row in enumerate(piece["shape"]):
            for x, cell in enumerate(row):
                if cell:
                    ny = piece["y"] + y
                    nx = piece["x"] + x

                    if 0 <= ny < HEIGHT and 0 <= nx < WIDTH:
                        board[ny][nx] = piece["color"]

    return board


# 자동 낙하
if not st.session_state.game_over:
    st_autorefresh(interval=700, limit=None, key="tetris_timer")
    if "tick" not in st.session_state:
        st.session_state.tick = 0

    if st.session_state.tick != st.session_state._prev_tick if "_prev_tick" in st.session_state else True:
        st.session_state._prev_tick = st.session_state.tick
        move(0, 1)

    st.session_state.tick += 1


# 점수
st.metric("현재 점수", st.session_state.score)

# 게임판 출력
board = get_display_board()

for row in board:
    line = ""
    for cell in row:
        line += cell if cell else "⬛"
    st.markdown(
        f"<div style='font-size:22px; letter-spacing:2px; "
        f"font-family:monospace'>{line}</div>",
        unsafe_allow_html=True
    )

if st.session_state.game_over:
    st.error("GAME OVER!")
    st.write(f"최종 점수: {st.session_state.score}")


# 조작 버튼
st.subheader("🎮 게임 조작")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("⬅️ 왼쪽", use_container_width=True):
        if not st.session_state.game_over:
            move(-1, 0)

with col2:
    if st.button("🔄 회전", use_container_width=True):
        if not st.session_state.game_over:
            rotate()

with col3:
    if st.button("➡️ 오른쪽", use_container_width=True):
        if not st.session_state.game_over:
            move(1, 0)

col4, col5 = st.columns(2)

with col4:
    if st.button("⬇️ 아래로", use_container_width=True):
        if not st.session_state.game_over:
            move(0, 1)

with col5:
    if st.button("⏬ 즉시 내리기", use_container_width=True):
        if not st.session_state.game_over:
            hard_drop()

if st.button("🔄 새 게임 시작", use_container_width=True):
    init_game()
    st.session_state.tick = 0
    st.session_state._prev_tick = -1
    st.rerun()
