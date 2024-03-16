import java.io.File;
import java.io.Writer;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Scanner;

public class csvEditor2 {
    public static void main(String[] args) {
        
        try {
            Scanner scnr = new Scanner(System.in);
            Scanner input_scnr = new Scanner(new File("output_pokemon.csv"));
            Writer writer = new FileWriter("output_pokemon2.csv", true);

            String line = input_scnr.nextLine();        // getting rid of the header
            String[] parsed = new String[9];

            while(input_scnr.hasNextLine()) {
                line = input_scnr.nextLine();
                parsed = line.split(",");

                String[] desired = new String[9];
                desired[0] = parsed[0]; desired[5] = parsed[5]; desired[6] = parsed[6]; desired[7] = parsed[7]; desired[8] = parsed[8];

                desired[1] = parsed[1].substring(1, parsed[1].length() - 1);
                
                if(parsed[2].equals("\" \"")) {
                    desired[2] = "NONE";
                }
                else {
                    desired[2] = parsed[2].substring(1, parsed[2].length() - 1);
                }

                desired[3] = parsed[3].substring(1, parsed[3].length() - 1);

                if (parsed[4].equals("\" \"")) {
                    desired[4] = "NONE";
                }
                else {
                    desired[4] = parsed[4].substring(1, parsed[4].length() - 1);
                }

                String desired_string = String.join(",", desired) + "\n";

                writer.write(desired_string);
            }

            scnr.close();
            input_scnr.close();
            writer.close();
        }
        catch (Exception e) {
            System.out.println("Error");
        }
    }
}
