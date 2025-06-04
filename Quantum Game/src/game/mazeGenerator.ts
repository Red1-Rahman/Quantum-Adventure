import { BlockType } from './types/blockType';

export class MazeGenerator {
    wallProbability: number;

    // ...existing code...

    generateMaze(width: number, height: number): BlockType[][] {
        const maze = Array(height).fill(0).map(() => Array(width).fill(BlockType.EMPTY));
        
        for (let y = 0; y < height; y++) {
            for (let x = 0; x < width; x++) {
                if ((x === 0 && y === 0) || (x === width - 1 && y === height - 1)) {
                    maze[y][x] = BlockType.EMPTY;
                    continue;
                }
                
                const random = Math.random();
                if (random < this.wallProbability) {
                    maze[y][x] = BlockType.WALL;
                } else if (random < this.wallProbability + 0.1) {
                    maze[y][x] = BlockType.ICE;
                } else if (random < this.wallProbability + 0.15) {
                    maze[y][x] = BlockType.SPIKES;
                } else if (random < this.wallProbability + 0.18) {
                    maze[y][x] = BlockType.TELEPORT;
                }
            }
        }

        // Ensure path to goal
        this.createSafePath(maze);
        return maze;
    }

    private createSafePath(maze: BlockType[][]) {
        let x = 0, y = 0;
        while (x < maze[0].length - 1 || y < maze.length - 1) {
            maze[y][x] = BlockType.EMPTY;
            if (x < maze[0].length - 1 && (y === maze.length - 1 || (x + y) % 2 === 0)) {
                x++;
            } else if (y < maze.length - 1) {
                y++;
            }
        }
        maze[maze.length - 1][maze[0].length - 1] = BlockType.EMPTY;
    }
}