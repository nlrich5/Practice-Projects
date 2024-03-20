import java.io.File;
import java.io.FileNotFoundException;
import java.io.Writer;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Scanner;

public class csvLoader {
    public Pokemon[] loadCSV() throws FileNotFoundException {
        Pokemon[] list = new Pokemon[1213];
        File file = new File("pokedoku_clone\\src\\pokemon.csv");
        Scanner scnr = new Scanner(file);

        String line = scnr.nextLine();      //gets rid of first line
        String[] parsed = new String[9];
        int i = 0;

        while(scnr.hasNextLine()) {
            Pokemon currPokemon= new Pokemon();
            
            line = scnr.nextLine();
            parsed = line.split(",");

            currPokemon.setDexNum(Integer.parseInt(parsed[0]));
            currPokemon.setName(parsed[1]);
            currPokemon.setForm(parsed[2]);
            currPokemon.setType1(parsed[3]);
            currPokemon.setType2(parsed[4]);
            currPokemon.setRegion(parsed[5]);
            currPokemon.setEvolution(parsed[6]);
            currPokemon.setEvoTag(parsed[7]);
            currPokemon.setCategory(parsed[8]);

            list[i] = currPokemon;
            i++;
        }

        scnr.close();

        return list;
    }
}
