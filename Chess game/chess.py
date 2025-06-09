import pygame
import sys
import random
from copy import deepcopy

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 800
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BROWN = (139, 69, 19)
CREAM = (255, 253, 208)
LIGHT_BROWN = (210, 180, 140)

# Set up the display
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Chess')

# Load piece images (you'll need these image files)
def create_piece_image(symbol, color):
    surf = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
    pygame.draw.circle(surf, color, (SQUARE_SIZE//2, SQUARE_SIZE//2), SQUARE_SIZE//2-5)
    font = pygame.font.SysFont('Arial', SQUARE_SIZE//2)
    text = font.render(symbol, True, (255,255,255) if color == (0,0,0) else (0,0,0))
    surf.blit(text, text.get_rect(center=(SQUARE_SIZE//2, SQUARE_SIZE//2)))
    return surf

def create_piece_image(piece_type, color):
    """Create more detailed chess piece images using Pygame drawing functions"""
    surf = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
    piece_color = color
    outline_color = (100, 100, 100) if color == (255, 255, 255) else (200, 200, 200)
    highlight_color = (color[0]+30, color[1]+30, color[2]+30) if color == (0, 0, 0) else (color[0]-30, color[1]-30, color[2]-30)
    
    # Base circle
    pygame.draw.circle(surf, piece_color, (SQUARE_SIZE//2, SQUARE_SIZE//2), SQUARE_SIZE//2-5)
    pygame.draw.circle(surf, outline_color, (SQUARE_SIZE//2, SQUARE_SIZE//2), SQUARE_SIZE//2-5, 2)
    pygame.draw.circle(surf, highlight_color, (SQUARE_SIZE//2, SQUARE_SIZE//2-5), SQUARE_SIZE//4, 1)
    
    # Piece-specific details
    if piece_type in ['p', 'P']:  # Pawn
        # Base
        pygame.draw.circle(surf, outline_color, (SQUARE_SIZE//2, SQUARE_SIZE//2+5), SQUARE_SIZE//4-5, 2)
        # Top
        pygame.draw.circle(surf, outline_color, (SQUARE_SIZE//2, SQUARE_SIZE//3), SQUARE_SIZE//6, 2)
        
    elif piece_type in ['r', 'R']:  # Rook
        # Castle-like top
        pygame.draw.rect(surf, outline_color, (SQUARE_SIZE//2-15, SQUARE_SIZE//3, 30, 15), 2)
        pygame.draw.rect(surf, outline_color, (SQUARE_SIZE//2-10, SQUARE_SIZE//3-10, 20, 10), 2)
        
    elif piece_type in ['n', 'N']:  # Knight
        # Horse head shape
        points = [
            (SQUARE_SIZE//2, SQUARE_SIZE//3),
            (SQUARE_SIZE//2+15, SQUARE_SIZE//3+5),
            (SQUARE_SIZE//2+10, SQUARE_SIZE//3+15),
            (SQUARE_SIZE//2-10, SQUARE_SIZE//3+10)
        ]
        pygame.draw.polygon(surf, outline_color, points, 2)
        
    elif piece_type in ['b', 'B']:  # Bishop
        # Mitre hat shape
        pygame.draw.polygon(surf, outline_color, [
            (SQUARE_SIZE//2, SQUARE_SIZE//4),
            (SQUARE_SIZE//2+10, SQUARE_SIZE//3),
            (SQUARE_SIZE//2-10, SQUARE_SIZE//3)
        ], 2)
        pygame.draw.line(surf, outline_color, 
                        (SQUARE_SIZE//2-8, SQUARE_SIZE//3+5),
                        (SQUARE_SIZE//2+8, SQUARE_SIZE//3+5), 2)
        
    elif piece_type in ['q', 'Q']:  # Queen
        # Crown with circle
        pygame.draw.circle(surf, outline_color, (SQUARE_SIZE//2, SQUARE_SIZE//3), 5, 2)
        # Crown points
        for x in [-10, 0, 10]:
            pygame.draw.polygon(surf, outline_color, [
                (SQUARE_SIZE//2+x, SQUARE_SIZE//3+5),
                (SQUARE_SIZE//2+x+5, SQUARE_SIZE//3+15),
                (SQUARE_SIZE//2+x-5, SQUARE_SIZE//3+15)
            ], 2)
            
    elif piece_type in ['k', 'K']:  # King
        # Cross on top
        pygame.draw.line(surf, outline_color, 
                        (SQUARE_SIZE//2, SQUARE_SIZE//4),
                        (SQUARE_SIZE//2, SQUARE_SIZE//3+10), 3)
        pygame.draw.line(surf, outline_color, 
                        (SQUARE_SIZE//2-8, SQUARE_SIZE//3),
                        (SQUARE_SIZE//2+8, SQUARE_SIZE//3), 3)
        # Base
        pygame.draw.polygon(surf, outline_color, [
            (SQUARE_SIZE//2, SQUARE_SIZE//3+10),
            (SQUARE_SIZE//2+10, SQUARE_SIZE//3+20),
            (SQUARE_SIZE//2-10, SQUARE_SIZE//3+20)
        ], 2)
    
    return surf

def load_images():
    """Load or create all piece images"""
    images = {}
    # White pieces
    images['wp'] = create_piece_image('p', (255, 255, 255))
    images['wR'] = create_piece_image('R', (255, 255, 255))
    images['wN'] = create_piece_image('N', (255, 255, 255))
    images['wB'] = create_piece_image('B', (255, 255, 255))
    images['wQ'] = create_piece_image('Q', (255, 255, 255))
    images['wK'] = create_piece_image('K', (255, 255, 255))
    # Black pieces
    images['bp'] = create_piece_image('p', (0, 0, 0))
    images['bR'] = create_piece_image('R', (0, 0, 0))
    images['bN'] = create_piece_image('N', (0, 0, 0))
    images['bB'] = create_piece_image('B', (0, 0, 0))
    images['bQ'] = create_piece_image('Q', (0, 0, 0))
    images['bK'] = create_piece_image('K', (0, 0, 0))
    
    return images

class Piece:
    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.x = 0
        self.y = 0
        self.calc_pos()
        self.selected = False
        self.moved = False

    def calc_pos(self):
        self.x = self.col * SQUARE_SIZE
        self.y = self.row * SQUARE_SIZE

    def move(self, row, col):
        self.row = row
        self.col = col
        self.calc_pos()
        self.moved = True

    def draw(self, win, images):
        if images.get(self.piece):
            win.blit(images[self.piece], (self.x, self.y))
        else:
            # Fallback drawing if images aren't available
            radius = SQUARE_SIZE // 2 - 10
            center = (self.x + SQUARE_SIZE // 2, self.y + SQUARE_SIZE // 2)
            pygame.draw.circle(win, self.color, center, radius)
            font = pygame.font.SysFont('Arial', 30)
            text = font.render(self.symbol, True, BLACK if self.color == WHITE else WHITE)
            text_rect = text.get_rect(center=center)
            win.blit(text, text_rect)

        if self.selected:
            pygame.draw.rect(win, BLUE, (self.x, self.y, SQUARE_SIZE, SQUARE_SIZE), 3)

    def __repr__(self):
        return self.color + self.symbol

class Pawn(Piece):
    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.piece = color + 'p'
        self.symbol = 'P'
        self.direction = -1 if color == 'w' else 1
        self.en_passant = False

    def valid_moves(self, board):
        moves = []
        
        # Move forward
        if 0 <= self.row + self.direction < ROWS and board[self.row + self.direction][self.col] == 0:
            moves.append((self.row + self.direction, self.col))
            
            # Double move from starting position
            if not self.moved and board[self.row + 2*self.direction][self.col] == 0:
                moves.append((self.row + 2*self.direction, self.col))
        
        # Capture diagonally
        for dc in [-1, 1]:
            if 0 <= self.col + dc < COLS and 0 <= self.row + self.direction < ROWS:
                piece = board[self.row + self.direction][self.col + dc]
                if piece != 0 and piece.color != self.color:
                    moves.append((self.row + self.direction, self.col + dc))
                
                # En passant
                if piece == 0 and isinstance(board[self.row][self.col + dc], Pawn):
                    adjacent_pawn = board[self.row][self.col + dc]
                    if adjacent_pawn.en_passant and adjacent_pawn.color != self.color:
                        moves.append((self.row + self.direction, self.col + dc))
        
        return moves

class Rook(Piece):
    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.piece = color + 'R'
        self.symbol = 'R'

    def valid_moves(self, board):
        moves = []
        
        # Horizontal and vertical moves
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for dr, dc in directions:
            for i in range(1, 8):
                r, c = self.row + i*dr, self.col + i*dc
                if 0 <= r < ROWS and 0 <= c < COLS:
                    if board[r][c] == 0:
                        moves.append((r, c))
                    else:
                        if board[r][c].color != self.color:
                            moves.append((r, c))
                        break
                else:
                    break
        
        return moves

class Knight(Piece):
    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.piece = color + 'N'
        self.symbol = 'N'

    def valid_moves(self, board):
        moves = []
        
        # All L-shaped moves
        knight_moves = [(2, 1), (2, -1), (-2, 1), (-2, -1),
                        (1, 2), (1, -2), (-1, 2), (-1, -2)]
        
        for dr, dc in knight_moves:
            r, c = self.row + dr, self.col + dc
            if 0 <= r < ROWS and 0 <= c < COLS:
                if board[r][c] == 0 or board[r][c].color != self.color:
                    moves.append((r, c))
        
        return moves

class Bishop(Piece):
    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.piece = color + 'B'
        self.symbol = 'B'

    def valid_moves(self, board):
        moves = []
        
        # Diagonal moves
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        for dr, dc in directions:
            for i in range(1, 8):
                r, c = self.row + i*dr, self.col + i*dc
                if 0 <= r < ROWS and 0 <= c < COLS:
                    if board[r][c] == 0:
                        moves.append((r, c))
                    else:
                        if board[r][c].color != self.color:
                            moves.append((r, c))
                        break
                else:
                    break
        
        return moves

class Queen(Piece):
    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.piece = color + 'Q'
        self.symbol = 'Q'

    def valid_moves(self, board):
        moves = []
        
        # Combine rook and bishop moves
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1),
                      (1, 1), (1, -1), (-1, 1), (-1, -1)]
        
        for dr, dc in directions:
            for i in range(1, 8):
                r, c = self.row + i*dr, self.col + i*dc
                if 0 <= r < ROWS and 0 <= c < COLS:
                    if board[r][c] == 0:
                        moves.append((r, c))
                    else:
                        if board[r][c].color != self.color:
                            moves.append((r, c))
                        break
                else:
                    break
        
        return moves

class King(Piece):
    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.piece = color + 'K'
        self.symbol = 'K'

    def valid_moves(self, board):
        moves = []
        
        # All adjacent squares
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                r, c = self.row + dr, self.col + dc
                if 0 <= r < ROWS and 0 <= c < COLS:
                    if board[r][c] == 0 or board[r][c].color != self.color:
                        moves.append((r, c))
        
        # Castling
        if not self.moved:
            # Kingside
            if (board[self.row][7] != 0 and isinstance(board[self.row][7], Rook) and 
                not board[self.row][7].moved and 
                board[self.row][5] == 0 and board[self.row][6] == 0):
                moves.append((self.row, 6))  # Castling kingside
            
            # Queenside
            if (board[self.row][0] != 0 and isinstance(board[self.row][0], Rook) and 
                not board[self.row][0].moved and 
                board[self.row][1] == 0 and board[self.row][2] == 0 and board[self.row][3] == 0):
                moves.append((self.row, 2))  # Castling queenside
        
        return moves

class Board:
    def __init__(self):
        self.board = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        self.create_board()
        self.white_turn = True
        self.selected_piece = None
        self.valid_moves = []
        self.white_king = (7, 4)
        self.black_king = (0, 4)
        self.check = False
        self.checkmate = False
        self.stalemate = False
        self.captured_pieces = []

    def draw_squares(self, win):
        win.fill(LIGHT_BROWN)
        for row in range(ROWS):
            for col in range(row % 2, ROWS, 2):
                pygame.draw.rect(win, CREAM, (row * SQUARE_SIZE, col * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def create_board(self):
        # Create black pieces
        self.board[0][0] = Rook(0, 0, 'b')
        self.board[0][1] = Knight(0, 1, 'b')
        self.board[0][2] = Bishop(0, 2, 'b')
        self.board[0][3] = Queen(0, 3, 'b')
        self.board[0][4] = King(0, 4, 'b')
        self.board[0][5] = Bishop(0, 5, 'b')
        self.board[0][6] = Knight(0, 6, 'b')
        self.board[0][7] = Rook(0, 7, 'b')
        for col in range(COLS):
            self.board[1][col] = Pawn(1, col, 'b')
        
        # Create white pieces
        self.board[7][0] = Rook(7, 0, 'w')
        self.board[7][1] = Knight(7, 1, 'w')
        self.board[7][2] = Bishop(7, 2, 'w')
        self.board[7][3] = Queen(7, 3, 'w')
        self.board[7][4] = King(7, 4, 'w')
        self.board[7][5] = Bishop(7, 5, 'w')
        self.board[7][6] = Knight(7, 6, 'w')
        self.board[7][7] = Rook(7, 7, 'w')
        for col in range(COLS):
            self.board[6][col] = Pawn(6, col, 'w')

    def draw(self, win, images):
        self.draw_squares(win)
        
        # Highlight valid moves
        for move in self.valid_moves:
            row, col = move
            pygame.draw.rect(win, GREEN, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)
        
        # Highlight king in check
        if self.check:
            king_pos = self.white_king if not self.white_turn else self.black_king
            pygame.draw.rect(win, RED, (king_pos[1] * SQUARE_SIZE, king_pos[0] * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)
        
        # Draw pieces
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != 0:
                    piece.draw(win, images)

    def select(self, row, col):
        piece = self.board[row][col]
        
        # If a piece is already selected
        if self.selected_piece:
            # If clicking on a valid move
            if (row, col) in self.valid_moves:
                self.move(self.selected_piece, row, col)
                self.selected_piece = None
                self.valid_moves = []
                return True
            
            # If clicking on another piece of the same color
            if piece != 0 and piece.color == ('w' if self.white_turn else 'b'):
                self.selected_piece = piece
                self.valid_moves = self.get_valid_moves(piece)
                return False
            
            # If clicking elsewhere
            self.selected_piece = None
            self.valid_moves = []
            return False
        
        # If no piece is selected yet
        if piece != 0 and piece.color == ('w' if self.white_turn else 'b'):
            self.selected_piece = piece
            self.valid_moves = self.get_valid_moves(piece)
            return False
        
        return False

    def move(self, piece, row, col):
        # Handle castling
        if isinstance(piece, King) and abs(piece.col - col) == 2:
            # Kingside castling
            if col > piece.col:
                rook = self.board[row][7]
                self.board[row][5] = rook
                self.board[row][7] = 0
                rook.move(row, 5)
            # Queenside castling
            else:
                rook = self.board[row][0]
                self.board[row][3] = rook
                self.board[row][0] = 0
                rook.move(row, 3)
        
        # Handle en passant
        if isinstance(piece, Pawn) and self.board[row][col] == 0 and piece.col != col:
            # Capture the pawn that was en passant
            captured_pawn = self.board[piece.row][col]
            self.captured_pieces.append(captured_pawn)
            self.board[piece.row][col] = 0
        
        # Handle pawn promotion
        if isinstance(piece, Pawn) and (row == 0 or row == 7):
            # Promote to queen by default (can implement a promotion menu later)
            self.board[piece.row][piece.col] = Queen(row, col, piece.color)
            piece = self.board[row][col]
        
        # Handle capture
        if self.board[row][col] != 0:
            self.captured_pieces.append(self.board[row][col])
        
        # Move the piece
        self.board[piece.row][piece.col] = 0
        self.board[row][col] = piece
        piece.move(row, col)
        
        # Set en passant flag for pawns that moved two squares
        if isinstance(piece, Pawn) and abs(piece.row - row) == 2:
            piece.en_passant = True
        else:
            piece.en_passant = False
        
        # Update king position
        if isinstance(piece, King):
            if piece.color == 'w':
                self.white_king = (row, col)
            else:
                self.black_king = (row, col)
        
        # Switch turns
        self.white_turn = not self.white_turn
        
        # Reset en passant flags for opponent's pawns
        for r in range(ROWS):
            for c in range(COLS):
                p = self.board[r][c]
                if isinstance(p, Pawn) and p.color != piece.color:
                    p.en_passant = False
        
        # Check for check/checkmate/stalemate
        self.update_game_state()

    def get_valid_moves(self, piece):
        moves = piece.valid_moves(self.board)
        valid_moves = []
        
        # Filter moves that would leave king in check
        for move in moves:
            temp_board = deepcopy(self)
            temp_piece = temp_board.board[piece.row][piece.col]
            
            # Simulate the move
            temp_board.board[piece.row][piece.col] = 0
            temp_board.board[move[0]][move[1]] = temp_piece
            temp_piece.row, temp_piece.col = move
            
            # Update king position if moving king
            if isinstance(piece, King):
                if piece.color == 'w':
                    temp_board.white_king = (move[0], move[1])
                else:
                    temp_board.black_king = (move[0], move[1])
            
            # Check if king is in check after move
            king_pos = temp_board.white_king if piece.color == 'w' else temp_board.black_king
            if not temp_board.is_square_under_attack(king_pos[0], king_pos[1], 'b' if piece.color == 'w' else 'w'):
                valid_moves.append(move)
        
        return valid_moves

    def is_square_under_attack(self, row, col, color):
        for r in range(ROWS):
            for c in range(COLS):
                piece = self.board[r][c]
                if piece != 0 and piece.color == color:
                    moves = piece.valid_moves(self.board)
                    if (row, col) in moves:
                        return True
        return False

    def update_game_state(self):
        # Check if current player's king is in check
        king_pos = self.white_king if self.white_turn else self.black_king
        self.check = self.is_square_under_attack(king_pos[0], king_pos[1], 'b' if self.white_turn else 'w')
        
        # Check for checkmate or stalemate
        has_legal_move = False
        for r in range(ROWS):
            for c in range(COLS):
                piece = self.board[r][c]
                if piece != 0 and piece.color == ('w' if self.white_turn else 'b'):
                    if self.get_valid_moves(piece):
                        has_legal_move = True
                        break
            if has_legal_move:
                break
        
        if not has_legal_move:
            if self.check:
                self.checkmate = True
            else:
                self.stalemate = True

    def get_all_valid_moves(self, color):
        moves = []
        for r in range(ROWS):
            for c in range(COLS):
                piece = self.board[r][c]
                if piece != 0 and piece.color == color:
                    piece_moves = self.get_valid_moves(piece)
                    for move in piece_moves:
                        moves.append(((r, c), move))
        return moves

class Game:
    def __init__(self):
        self.board = Board()
        self.images = load_images()
        self.ai_thinking = False

    def draw(self):
        self.board.draw(WIN, self.images)
        pygame.display.update()

    def human_turn(self, pos):
        row, col = pos[1] // SQUARE_SIZE, pos[0] // SQUARE_SIZE
        if self.board.select(row, col):
            return True  # Move was made
        return False  # Move wasn't made

    def ai_turn(self):
        # Simple AI: choose a random valid move
        valid_moves = self.board.get_all_valid_moves('b' if self.board.white_turn else 'w')
        if valid_moves:
            (start_row, start_col), (end_row, end_col) = random.choice(valid_moves)
            piece = self.board.board[start_row][start_col]
            self.board.move(piece, end_row, end_col)
            return True
        return False

def main():
    clock = pygame.time.Clock()
    game = Game()
    
    while True:
        clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN and not game.board.checkmate and not game.board.stalemate:
                if game.board.white_turn:  # Human's turn (white)
                    if game.human_turn(pygame.mouse.get_pos()):
                        # After human moves, AI moves if game isn't over
                        if not game.board.checkmate and not game.board.stalemate:
                            game.ai_turn()
                # else:  # AI's turn (black) - handled automatically after human move
        
        game.draw()
        
        # Display game over message
        if game.board.checkmate or game.board.stalemate:
            font = pygame.font.SysFont('Arial', 50)
            if game.board.checkmate:
                text = font.render('Checkmate!', True, RED)
            else:
                text = font.render('Stalemate!', True, BLUE)
            text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
            WIN.blit(text, text_rect)
            pygame.display.update()

if __name__ == '__main__':
    main()