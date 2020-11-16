"""
generate_heatmap.py

Parse GCG files (a standardized file format for analysis) and collect only the
information useful for creating a heatmap. Generate a heatmap and save to 
heatmap.png. Use the results to calculate the popularity of each quadrant of the 
board.

"""


import os
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from os.path import join as pjoin

DATA_DIR = 'example-boards'
SCRABBLE_SIZE = 15

def parse_gcg_files():    
    dfs = []
    for file in sorted(os.listdir(DATA_DIR)):
        if file.endswith('.gcg'):
            with open(pjoin(DATA_DIR, file)) as f:
                lines = f.readlines()

                # remove player info
                lines = [line for line in lines if not line.startswith('#')]
                lines = [line.split(': ')[1].strip() for line in lines]

                # remove unplayed tiles
                lines = [line for line in lines if "(" not in line]

                # remove exchanged tiles
                lines = [line for line in lines 
                         if "-" not in line.split()[1]]
                
                # get location, length, direction
                location = [line.split()[1] for line in lines]
                direction = ['horiz' if loc[0].isnumeric() 
                             else 'vert' for loc in location]
                length = [len(line.split()[2]) for line in lines]
                
                df = pd.DataFrame(index=range(len(length)))
                df['location'] = location
                df['direction'] = direction
                df['length'] = length
                dfs.append({
                    'file': file, 
                    'df': df
                })

    return dfs

def calculate_board_stats(dfs):
    total_board = np.zeros((SCRABBLE_SIZE, SCRABBLE_SIZE))

    # Turn dataframes into matrix segments
    for d in dfs:
        df = d['df']
        new_board = np.zeros((SCRABBLE_SIZE, SCRABBLE_SIZE))
        segments = [to_matrix(r) for i, r in df.iterrows()]
        for seg in segments:
            p1, p2 = seg
            x1, y1 = p1
            x2, y2 = p2

            # Place those segments onto a matrix of zeros and ones.
            if x1 == x2:
                y1, y2 = sorted([y1, y2])
                new_board[y1:(y2+1) , x1] = 1
            else:
                x1, x2 = sorted([x1, x2])
                new_board[y1, x1:(x2+1)] = 1
        total_board += new_board

    # Create heatmap
    plt.imshow(total_board)
    plt.axis('off')
    plt.show()
    plt.savefig('heatmap.png')

    # Calculate quadrant stats
    mid_inner = SCRABBLE_SIZE // 2
    mid_outer = mid_inner + 1
    tot = SCRABBLE_SIZE

    quad_1 = total_board[0:mid_inner, 0:mid_inner]
    quad_2 = total_board[mid_outer:tot, 0:mid_inner]
    quad_3 = total_board[0:mid_inner, mid_outer:tot]
    quad_4 = total_board[mid_outer:tot, mid_outer:tot]

    assert quad_1.shape == quad_2.shape == quad_3.shape == quad_4.shape

    stats = {
        'NW': round(quad_1.sum() / total_board.sum() * 100, 2),
        'NE': round(quad_2.sum() / total_board.sum() * 100, 2),
        'SW': round(quad_3.sum() / total_board.sum() * 100, 2),
        'SE': round(quad_4.sum() / total_board.sum() * 100, 2)
    }

    for cd, stat in stats.items():
        print(f'{cd}\t{stat}')

def to_matrix(r):
    loc_s = r['location']
    x1 = loc_s.strip('0123456789')
    y1 = loc_s.strip('ABCDEFGHIJKLMNO')

    assert x1.isalpha()
    assert y1.isnumeric()
    assert x1 in 'ABCDEFGHIJKLMNO', x1
    assert y1 in [str(y) for y in range(16)], y1

    x1 = ord(x1) - 65
    y1 = int(y1) - 1
    
    if r['direction'] == 'vert':
        x2 = x1
        y2 = y1 + r['length'] - 1
    else:
        y2 = y1
        x2 = x1 + r['length'] - 1
    
    assert not any([t < 0 for t in [x1, x2, y1, y2]])

    return [[x1, y1], [x2, y2]]

def main():
    dfs = parse_gcg_files()
    calculate_board_stats(dfs)

if __name__ == '__main__':
    main()