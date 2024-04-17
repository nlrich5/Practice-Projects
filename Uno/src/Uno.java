import java.util.Scanner;
import java.util.ArrayList;

public class Uno {
    public static void main (String[] args) {
        Scanner scnr = new Scanner(System.in);
        Deck deck = new Deck();
        int currCard = 0;
        int currDiscard = 0;
        int numPlayers = -1;
        int numUsers = -1;
        int currPlayer = 1;

        boolean reverse = false;

        deck = deck.createCards();
        deck.cards = deck.shuffleCards(deck.cards);

        while ((numPlayers < 2) || (numPlayers > 10)) {
            System.out.println("How many players?");
            numPlayers = scnr.nextInt();
        }
        while ((numUsers < 1) || (numUsers > numPlayers)) {
            System.out.println("How many AI players?");
            numUsers = numPlayers - scnr.nextInt();
        }
        System.out.println("" + numPlayers + " players, " + numUsers + " users");

        ArrayList<ArrayList<Card>> hands = new ArrayList<ArrayList<Card>>();
        for (int i = 0; i < numPlayers; i++) {
            hands.add(new ArrayList<Card>());
            for (int j = 0; j < 7; j++) {
                hands.get(i).add(deck.cards.get(currCard));
                currCard++;
            }
        }

        for (int i = 0; i < numPlayers; i++) {
            System.out.println("Player " + (i + 1) + "'s hand:");
            for (Card card: hands.get(i)) {
                System.out.println(card);
            }
        }

        
    }
}