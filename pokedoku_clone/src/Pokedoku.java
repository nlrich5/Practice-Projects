import java.io.FileNotFoundException;

public class Pokedoku {
    public static void main(String[] args) {
        csvLoader csvLoader = new csvLoader();
        Pokemon[] list = new Pokemon[1000];

        try {
            list = csvLoader.loadCSV();
        }
        catch (FileNotFoundException e) {
            e.printStackTrace();
        }
    }

    public Grid generateGrid() {
        Grid grid = new Grid();

        return grid;
    }
}
