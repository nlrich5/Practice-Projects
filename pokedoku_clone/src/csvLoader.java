import java.io.File;
import java.io.FileNotFoundException;
import java.util.Scanner;

public class csvLoader {
    public Pokemon[] loadCSV() throws FileNotFoundException {
        Pokemon[] list = new Pokemon[1000];
        File file = new File("pokemon.csv");
        Scanner scnr = new Scanner(file);

        String line = scnr.nextLine();      //gets rid of first line
        String[] parsed = new String[7];
        int i = 0;

        while(scnr.hasNextLine()) {
            Pokemon currPokemon= new Pokemon();
            
            line = scnr.nextLine();
            parsed = line.split(",");

            currPokemon.setDexNum(Integer.parseInt(parsed[0]));
            currPokemon.setName(parsed[1]);
            currPokemon.setType1(parsed[2]);
            currPokemon.setType2(parsed[3]);
            currPokemon.setEvolution(parsed[4]);
            currPokemon.setRegion(parsed[5]);
            currPokemon.setTag(parsed[6]);

            list[i] = currPokemon;
            i++;
        }

        scnr.close();

        return list;
    }
}
