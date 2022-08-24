"""
Copyright (c) 2022 YuaHyodo

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from snail_reversi.Board import BLACK, WHITE, DRAW, PASS
from snail_reversi.Board import Board

class Solver:
    def __init__(self):
        self.win_score = 10000
        self.lose_score = self.change_score(self.win_score)
        self.draw_score = 0
        self.root_board = Board()
        self.Ttable = {}
        self.Ordering_moves_table = {}

    def AB_change(self, AB):
        return [-AB[1], -AB[0]]

    def change_score(self, score):
        return score * -1

    def print_info(self):
        print('Pruning_count:', self.Pruning_count)
        return
    
    """
    def Ordering(self, board):
        sfen = board.return_sfen()
        if sfen in self.Ordering_moves_table.keys():
            return self.Ordering_moves_table[sfen]
        Lmoves = board.gen_legal_moves()
        moves = []
        yusen = ['a1', 'a8', 'h1', 'h8']
        for sq in yusen:
            if sq in Lmoves:
                moves.append(sq)
                Lmoves.remove(sq)
        moves.extend(Lmoves)
        self.Ordering_moves_table[sfen] = moves
        return moves
    """

    def Ordering(self, board):
        sfen = board.return_sfen()
        if sfen in self.Ordering_moves_table.keys():
            return self.Ordering_moves_table[sfen]
        Lmoves = board.gen_legal_moves()
        self.Ordering_moves_table[sfen] = Lmoves
        return Lmoves

    def search(self, depth, board, moves_list, AB):
        if board.is_gameover() or (len(moves_list) >= 2 and moves_list[-1] == moves_list[-2]):
            winner = board.return_winner()
            if winner == DRAW:
                return self.draw_score
            if winner == board.turn:
                return self.win_score
            return self.lose_score
        sfen = board.return_sfen()
        if sfen in self.Ttable.keys():
            return self.Ttable[sfen]
        if depth <= 2:
            moves = self.Ordering(board)
        else:
            moves = self.Ordering(board)
            #moves = board.gen_legal_moves()
        if PASS in moves:
            board.move_from_usix(PASS)
            moves_list.append(PASS)
            score = self.search(depth + 1, board, moves_list, AB)
            moves_list.pop(-1)
            return score
        for m in moves:
            board.move_from_usix(m)
            moves_list.append(m)
            score = self.change_score(self.search(depth + 1, board, moves_list, self.AB_change(AB)))
            moves_list.pop(-1)
            if score == self.win_score:
                self.Pruning_count['AlphaBeta'] += 1
                self.Ttable[sfen] = self.win_score
                return self.win_score
            if score >= AB[1]:
                self.Pruning_count['AlphaBeta'] += 1
                self.Ttable[sfen] = score
                return score
            AB[0] = max([AB[0], score])
            board.set_sfen(sfen)
        self.Ttable[sfen] = AB[0]
        return AB[0]

    def main(self, sfen):
        self.root_board.set_sfen(sfen)
        moves = self.Ordering(self.root_board)
        bestmove = None
        self.Pruning_count = {'AlphaBeta': 0}
        AB = [self.lose_score, self.win_score]
        moves_list = []
        for m in moves:
            self.root_board.move_from_usix(m)
            moves_list.append(m)
            score = self.change_score(self.search(1, self.root_board, moves_list, self.AB_change(AB)))
            moves_list.pop(-1)
            if score == self.win_score:
                self.Ttable[sfen] = self.win_score
                return m
            if score >= AB[0]:
                bestmove = m
                AB[0] = score
            self.root_board.set_sfen(sfen)
        self.Ttable[sfen] = AB[0]
        return bestmove

if __name__ == '__main__':
    solver = Solver()
