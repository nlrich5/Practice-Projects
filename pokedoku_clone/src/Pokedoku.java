import java.io.FileNotFoundException;

public class Pokedoku {
    public static void main(String[] args) {
        csvLoader csvLoader = new csvLoader();
        Pokemon[] list = new Pokemon[1000];

        try {
            list = csvLoader.loadCSV();
        }
        catch (FileNotFoundException e) {
            System.out.println("File could not be loaded.");
        }
    }
}
