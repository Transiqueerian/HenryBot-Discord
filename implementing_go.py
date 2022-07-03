N = 19
NN = N * N
WHITE, BLACK, EMPTY = 'O', 'X', '.'
EMPTY_BOARD = EMPTY * NN

def flatten(c): #takes a 2-tuple of coordinates and flattens it to a string index
    return N * c[0] + c[1]

def unflatten(fc): #"fc" = "flattened coordinate"
    return divmod(fc, N)

def is_on_board(c):
    return c[0] % N == c[0] and c[1] % N == c[1] #checks whether the given coordinates fit on grid of n*n
    #why not just check "c[0] < N and c[1] < N"?

def get_valid_neighbors(fc):
    x, y = unflatten(fc)
    possible_neighbors = ((x+1, y), (x-1, y), (x, y+1), (x, y-1))
    return [flatten(n) for n in possible_neighbors if is_on_board(n)]

NEIGHBORS = [get_valid_neighbors(fc) for fc in range(NN)]
assert sorted(NEIGHBORS[0]) == [1, N]
assert sorted(NEIGHBORS[1]) == [0, 2, N+1]
assert sorted(NEIGHBORS[N+1]) == [1, N, N+2, 2*N + 1]

def find_reached(board, fc):
    color == board[fc]
    chain = set([fc])
    reached = set()
    frontier = [fc]
    while frontier:
        current_fc = frontier.pop()
        chain.add(current_fc)
        for fn in NEIGHBORS[current_fc]:
            if board[fn] == color and not fn in chain:
                frontier.append(fn)
            elif board[fn] != color:
                reached.add(fn)
    return chain, reached

class IllegalMove(Exception): pass

def place_stone(color, board, fc):
    return board[:fc] + color + board[fc+1:]

def bulk_place_stones(color, board, stones):
    byteboard = bytearray(board, encoding='ascii')