import java.io.File;
import java.io.FileNotFoundException;
import java.io.Writer;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Scanner;

public class csvLoader {
    public Pokemon[] loadCSV() throws FileNotFoundException {
        Pokemon[] list = new Pokemon[1213];
        File file = new File("output_pokemon2.csv");
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
        /*
        String[][] evoTags = new String[7][1000];
        evoTags[0][0] = "1/1"; evoTags[1][0] = "1/2"; evoTags[2][0] = "2/2"; evoTags[3][0] = "1/3"; evoTags[4][0] = "2/3"; evoTags[5][0] = "3/3"; evoTags[6][0] = "Other";
        Integer[] evoTagsCount = new Integer[7];
        for (i = 0; i < 7; i++) {
            evoTagsCount[i] = 0;
        }

        for(i = 0; i < 1213; i++) {
            switch(list[i].getEvolution()) {
                case "1/1":
                    evoTags[0][evoTagsCount[0] + 1] = list[i].getName();
                    evoTagsCount[0]++;
                    break;

                case "1/2":
                    evoTags[1][evoTagsCount[1] + 1] = list[i].getName();
                    evoTagsCount[1]++;
                    break;

                case "2/2":
                    evoTags[2][evoTagsCount[2] + 1] = list[i].getName();
                    evoTagsCount[2]++;
                    break;

                case "1/3": 
                    evoTags[3][evoTagsCount[3] + 1] = list[i].getName();
                    evoTagsCount[3]++;
                    break;

                case "2/3":
                    evoTags[4][evoTagsCount[4] + 1] = list[i].getName();
                    evoTagsCount[4]++;
                    break;

                case "3/3":
                    evoTags[5][evoTagsCount[5] + 1] = list[i].getName();
                    evoTagsCount[5]++;
                    break;

                default:
                    evoTags[6][evoTagsCount[6] + 1] = list[i].getName();
                    evoTagsCount[6]++;
                    break;
            }
        }

        try {
            Writer writer = new FileWriter("evo_stage_check.txt");

            for (int j = 0; j < 7; j++) {
                for (int k = 0; k < evoTags[j].length; k++) {
                    writer.write(evoTags[j][k] + "\n");
                }
                writer.write("\n\n");
            }
            
            writer.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
        */

        scnr.close();

        return list;
    }
}
