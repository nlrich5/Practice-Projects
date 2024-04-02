public class Uno {
    public static void main (String[] args) {
        Deck deck = new Deck();
        int currCard = 0;
        int currDiscard = 0;
        int playerNum = -1;
        int currPlayer = 1;

        boolean reverse = false;

        deck = deck.createCards();
        deck = deck.shuffleCards();
    }
}
