class Card {

    private Color card_color;
    private int value;
    private String action;

    public Card() {
        card_color = null;
        value = -20;
        action = "N/A";
    }
    public Card(Color color, int value, String action) {
        this.card_color = color;
        this.value = value;
        this.action = action;
    }

    public Color getCard_color() {
        return card_color;
    }
    public void setCard_color(Color card_color) {
        this.card_color = card_color;
    }
    public int getValue() {
        return value;
    }
    public void setValue(int value) {
        this.value = value;
    }
    public String getAction() {
        return action;
    }
    public void setAction(String action) {
        this.action = action;
    }

    @Override
    public String toString() {
        if (value >= 0) {
            return "" + this.card_color + " " + this.value;
        }
        else if (this.card_color != Color.any) {
            return "" + this.card_color + " " + this.action;
        }
        else {
            return "" + this.action;
        }
    }
}