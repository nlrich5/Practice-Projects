public class Grid {
    public Square[][] grid;

    public Grid() {
        for (int i = 0; i < 3; i++) {
            for (int j = 0; j  < 3; j++) {
                this.grid[i][j] = new Square();
            }
        }
    }
}
