import java.io.File;
import java.io.Writer;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Scanner;

public class csvEditor {
    public static void main(String[] args) {
        String filepath = "downloaded_pokemon.csv";

        try {
            Scanner scnr = new Scanner(new File(filepath));
            Scanner output_scnr = new Scanner(new File("output_pokemon.csv"));
            Scanner inp_scnr = new Scanner(System.in);
            Writer writer = new FileWriter("output_pokemon.csv", true);

            String line = scnr.nextLine();      //get rid of header line
            String trash = output_scnr.nextLine();
            String[] parsed = new String[13];
            boolean skip = false;
            Integer startPoint = 1;

            while(scnr.hasNextLine()) {
                if (!output_scnr.hasNextLine()) {
                    line = scnr.nextLine();
                    parsed = line.split(",");
                    
                    if (parsed[4].equals(" ")) {
                        parsed[4] = "NONE";
                    }

                    switch(parsed[12]) {
                        case "1":
                            parsed[12] = "Kanto";
                            break;

                        case "2":
                            parsed[12] = "Johto";
                            break;

                        case "3":
                            parsed[12] = "Hoenn";
                            break;

                        case "4":
                            parsed[12] = "Sinnoh";
                            break;

                        case "5":
                            parsed[12] = "Unova";
                            break;

                        case "6":
                            parsed[12] = "Kalos";
                            break;

                        case "7":
                            parsed[12] = "Alola";
                            break;

                        case "8":
                            parsed[12] = "Galar";
                            break;

                        case "9":
                            parsed[12] = "Paldea";
                            break;
                    }

                    String[] desired = new String[9];
                    desired[0] = parsed[0]; desired[1] = parsed[1]; desired[2] = parsed[2]; desired[3] = parsed[3]; desired[4] = parsed[4]; desired[5] = parsed[12]; desired[7] = "NONE"; desired[8] = "NONE";

                    if (Integer.parseInt(parsed[0]) >= startPoint) {
                        if (!skip) {
                            System.out.println("" + desired[1] + " " + desired[2]+ "\nEvo_Stage:\n");
                            desired[6] = inp_scnr.nextLine();
                            /*
                            System.out.println("" + desired[1] + " " + desired[2]+ "\nEvo_Tag:\n");
                            desired[7] = inp_scnr.nextLine();
                            System.out.println("" + desired[1] + " " + desired[2]+ "\nCategory_Tag:\n");
                            desired[8] = inp_scnr.nextLine();
                            */
                            if(desired[6].equals("q") /*|| desired[7].equals("q") || desired[8].equals("q")*/) {
                                skip = true;
                                System.out.println("Data entry ended at point " + desired[0]);
                            }
                        }
                    }

                    String desired_string = String.join(",", desired) + "\n";

                    writer.write(desired_string);
                }
            }

            scnr.close();
            inp_scnr.close();
            output_scnr.close();
            writer.close();
        }
        catch (IOException e) {
            System.out.println("Error reading file");
        }

    }
}