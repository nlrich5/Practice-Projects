public class Pokemon {
    private int dexNum;
    private String name;
    private String type1;
    private String type2;
    private String evolution;
    private String region;
    private String tag;

    Pokemon() {
        this.dexNum = 0;
        this.name = "Unnamed";
        this.type1 = "NONE";
        this.type2 = "NONE";
        this.evolution = "N/A";
        this.region = "Unnamed";
        this.tag = "NONE";
    }

    public int getDexNum() {
        return this.dexNum;
    }
    public void setDexNum(int dexNum) {
        this.dexNum = dexNum;
    }
    public String getName() {
        return this.name;
    }
    public void setName(String name) {
        this.name = name;
    }
    public String getType1() {
        return this.type1;
    }
    public void setType1(String type1) {
        this.type1 = type1;
    }
    public String getType2() {
        return this.type2;
    }
    public void setType2(String type2) {
        this.type2 = type2;
    }
    public String getEvolution() {
        return this.evolution;
    }
    public void setEvolution(String evolution) {
        this.evolution = evolution;
    }
    public String getRegion() {
        return this.region;
    }
    public void setRegion(String region) {
        this.region = region;
    }
    public String getTag() {
        return this.tag;
    }
    public void setTag(String tag) {
        this.tag = tag;
    }
}