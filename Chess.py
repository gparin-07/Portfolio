import tkinter as tk
import random
import copy

PIECES = {
    "r": "♜", "n": "♞", "b": "♝", "q": "♛", "k": "♚", "p": "♟",
    "R": "♖", "N": "♘", "B": "♗", "Q": "♕", "K": "♔", "P": "♙", " ": ""
}
PIECE_VALUE = {"K": 1000, "Q": 9, "R": 5, "B": 3, "N": 3, "P": 1,
               "k": 1000, "q": 9, "r": 5, "b": 3, "n": 3, "p": 1, " ": 0}

START_BOARD = [
    ["r","n","b","q","k","b","n","r"],
    ["p","p","p","p","p","p","p","p"],
    [" "," "," "," "," "," "," "," "],
    [" "," "," "," "," "," "," "," "],
    [" "," "," "," "," "," "," "," "],
    [" "," "," "," "," "," "," "," "],
    ["P","P","P","P","P","P","P","P"],
    ["R","N","B","Q","K","B","N","R"]
]

class ChessGame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Chess Game (with Checkmate & Promotion)")
        self.cell_size = 60
        self.board = [row[:] for row in START_BOARD]
        self.selected = None
        self.turn = "white"
        self.canvas = tk.Canvas(self, width=8*self.cell_size, height=8*self.cell_size)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_click)
        self.status = tk.Label(self, text="", font=("Arial", 16))
        self.status.pack()
        self.draw_board()
        self.after(500, self.computer_move_if_needed)

    def draw_board(self):
        self.canvas.delete("all")
        for i in range(8):
            for j in range(8):
                x1 = j * self.cell_size
                y1 = i * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                color = "#f0d9b5" if (i + j) % 2 == 0 else "#b58863"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color)
                piece = self.board[i][j]
                if piece != " ":
                    self.canvas.create_text(
                        x1 + self.cell_size//2, y1 + self.cell_size//2,
                        text=PIECES[piece], font=("Arial", 32)
                    )
        if self.selected:
            i, j = self.selected
            x1 = j * self.cell_size
            y1 = i * self.cell_size
            x2 = x1 + self.cell_size
            y2 = y1 + self.cell_size
            self.canvas.create_rectangle(x1, y1, x2, y2, outline="red", width=3)
        self.status.config(text=self.get_status_text())

    def get_status_text(self):
        if self.is_checkmate("white"):
            return "Checkmate! Black wins."
        if self.is_checkmate("black"):
            return "Checkmate! White wins."
        if self.is_in_check(self.turn):
            return f"{self.turn.capitalize()} is in check!"
        return f"{self.turn.capitalize()}'s turn"

    def on_click(self, event):
        if self.turn != "white" or self.is_checkmate("white") or self.is_checkmate("black"):
            return
        row = event.y // self.cell_size
        col = event.x // self.cell_size
        if self.selected:
            if (row, col) != self.selected:
                if self.is_valid_move(self.selected, (row, col), "white"):
                    self.move_piece(self.selected, (row, col))
                    self.selected = None
                    self.turn = "black"
                    self.draw_board()
                    self.after(500, self.computer_move_if_needed)
                    return
            self.selected = None
        elif self.board[row][col] in "RNBQKP":
            self.selected = (row, col)
        self.draw_board()

    def is_valid_move(self, src, dst, color, board=None):
        # Use a copy of the board if provided (for simulation)
        board = board if board else self.board
        sr, sc = src
        dr, dc = dst
        piece = board[sr][sc]
        target = board[dr][dc]
        if color == "white" and piece not in "RNBQKP":
            return False
        if color == "black" and piece not in "rnbqkp":
            return False
        if color == "white" and target in "RNBQKP":
            return False
        if color == "black" and target in "rnbqkp":
            return False
        if (sr, sc) == (dr, dc):
            return False
        # Pawn moves
        if piece == "P":
            if sc == dc and dr == sr - 1 and board[dr][dc] == " ":
                return True
            if sc == dc and sr == 6 and dr == 4 and board[5][dc] == " " and board[4][dc] == " ":
                return True
            if abs(sc - dc) == 1 and dr == sr - 1 and board[dr][dc] in "rnbqkp":
                return True
        if piece == "p":
            if sc == dc and dr == sr + 1 and board[dr][dc] == " ":
                return True
            if sc == dc and sr == 1 and dr == 3 and board[2][dc] == " " and board[3][dc] == " ":
                return True
            if abs(sc - dc) == 1 and dr == sr + 1 and board[dr][dc] in "RNBQKP":
                return True
        # Rook
        if piece in "Rr":
            if sr == dr or sc == dc:
                return self.clear_path(src, dst, board)
        # Bishop
        if piece in "Bb":
            if abs(sr - dr) == abs(sc - dc):
                return self.clear_path(src, dst, board)
        # Queen
        if piece in "Qq":
            if sr == dr or sc == dc or abs(sr - dr) == abs(sc - dc):
                return self.clear_path(src, dst, board)
        # Knight
        if piece in "Nn":
            if (abs(sr - dr), abs(sc - dc)) in [(2, 1), (1, 2)]:
                return True
        # King
        if piece in "Kk":
            if max(abs(sr - dr), abs(sc - dc)) == 1:
                # Don't allow moving into check
                temp_board = copy.deepcopy(board)
                temp_board[dr][dc] = piece
                temp_board[sr][sc] = " "
                if not self.is_in_check(color, temp_board):
                    return True
        return False

    def clear_path(self, src, dst, board=None):
        board = board if board else self.board
        sr, sc = src
        dr, dc = dst
        d_r = (dr - sr)
        d_c = (dc - sc)
        steps = max(abs(d_r), abs(d_c))
        if steps == 0:
            return False
        step_r = d_r // steps if d_r != 0 else 0
        step_c = d_c // steps if d_c != 0 else 0
        for i in range(1, steps):
            r = sr + step_r * i
            c = sc + step_c * i
            if board[r][c] != " ":
                return False
        return True

    def move_piece(self, src, dst):
        sr, sc = src
        dr, dc = dst
        piece = self.board[sr][sc]
        self.board[dr][dc] = piece
        self.board[sr][sc] = " "
        # Pawn promotion
        if piece == "P" and dr == 0:
            self.board[dr][dc] = "Q"
        if piece == "p" and dr == 7:
            self.board[dr][dc] = "q"

    def computer_move_if_needed(self):
        if self.turn == "black" and not self.is_checkmate("black") and not self.is_checkmate("white"):
            moves = self.all_valid_moves("black")
            if moves:
                # Harder bot: prefer capturing, avoid moving into check
                best_score = -float("inf")
                best_moves = []
                for move in moves:
                    temp_board = copy.deepcopy(self.board)
                    src, dst = move
                    captured = PIECE_VALUE[temp_board[dst[0]][dst[1]]]
                    temp_board[dst[0]][dst[1]] = temp_board[src[0]][src[1]]
                    temp_board[src[0]][src[1]] = " "
                    # Pawn promotion
                    if temp_board[dst[0]][dst[1]] == "p" and dst[0] == 7:
                        temp_board[dst[0]][dst[1]] = "q"
                    if self.is_in_check("black", temp_board):
                        continue  # Don't move into check
                    # Score: prefer capturing, avoid checks
                    score = captured
                    if self.is_in_check("white", temp_board):
                        score += 0.5  # Prefer putting white in check
                    if score > best_score:
                        best_score = score
                        best_moves = [move]
                    elif score == best_score:
                        best_moves.append(move)
                if best_moves:
                    move = random.choice(best_moves)
                    self.move_piece(move[0], move[1])
            self.turn = "white"
            self.draw_board()

    def all_valid_moves(self, color, board=None):
        board = board if board else self.board
        moves = []
        for i in range(8):
            for j in range(8):
                piece = board[i][j]
                if (color == "white" and piece in "RNBQKP") or (color == "black" and piece in "rnbqkp"):
                    for di in range(8):
                        for dj in range(8):
                            if self.is_valid_move((i, j), (di, dj), color, board):
                                # Don't allow moves that leave king in check
                                temp_board = copy.deepcopy(board)
                                temp_board[di][dj] = temp_board[i][j]
                                temp_board[i][j] = " "
                                # Pawn promotion
                                if temp_board[di][dj] == "P" and di == 0:
                                    temp_board[di][dj] = "Q"
                                if temp_board[di][dj] == "p" and di == 7:
                                    temp_board[di][dj] = "q"
                                if not self.is_in_check(color, temp_board):
                                    moves.append(((i, j), (di, dj)))
        return moves

    def is_in_check(self, color, board=None):
        board = board if board else self.board
        king = "K" if color == "white" else "k"
        # Find king position
        for i in range(8):
            for j in range(8):
                if board[i][j] == king:
                    king_pos = (i, j)
        # Check if any enemy piece can capture the king
        enemy = "rnbqkp" if color == "white" else "RNBQKP"
        for i in range(8):
            for j in range(8):
                if board[i][j] in enemy:
                    if self.is_valid_move((i, j), king_pos, "black" if color == "white" else "white", board):
                        return True
        return False

    def is_checkmate(self, color):
        if not self.is_in_check(color):
            return False
        moves = self.all_valid_moves(color)
        return len(moves) == 0

if __name__ == "__main__":
    app = ChessGame()
    app.mainloop()
    