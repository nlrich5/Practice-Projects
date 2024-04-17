import java.util.ArrayList;

public class Deck {
    public ArrayList<Card> cards;

    Deck() {
        cards = new ArrayList<Card>();
    }

    public Deck createCards() {
        Deck deck = new Deck();
        Card currCard;

        for (int i = 0; i < 4; i++) {
            Color currColor;
            switch (i) {
                case 0:
                    currColor = Color.red;
                    break;

                case 1:
                    currColor = Color.yellow;
                    break;

                case 2:
                    currColor = Color.green;
                    break;

                case 3:
                    currColor = Color.blue;
                    break;

                default:
                    currColor = null;
                    break;
            }

            for (int j = 1; j < 10; j++) {
                for (int k = 0; k < 2; k++) {
                    currCard = new Card(currColor, j, "NONE");
                    deck.cards.add(currCard);
                }
            }

            for (int j = 0; j < 2; j++) {
                currCard = new Card(currColor, -1, "skip");
                deck.cards.add(currCard);

                currCard = new Card(currColor, -2, "reverse");
                deck.cards.add(currCard);

                currCard = new Card(currColor, -3, "+2");
                deck.cards.add(currCard);
            }

            currCard = new Card(currColor, 0, "NONE");
            deck.cards.add(currCard);

            currCard = new Card(Color.any, -4, "wild");
            deck.cards.add(currCard);

            currCard = new Card(Color.any, -5, "wild plus 4");
            deck.cards.add(currCard);
        }

        return deck;
    }

    public ArrayList<Card> shuffleCards(ArrayList<Card> inputList) {
        ArrayList<Card> shuffled = new ArrayList<Card>();

        for (int i = 0; i < 3; i++) {
            while (inputList.size() > 0) {
                int index = (int)(Math.random() * inputList.size());
                shuffled.add(inputList.remove(index));
            }
            inputList = shuffled;
            shuffled = new ArrayList<Card>();
        }

        return inputList;
    }
}