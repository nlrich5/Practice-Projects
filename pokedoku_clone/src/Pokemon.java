public class Pokemon {
    private int dexNum;
    private String name;
    private String form;
    private String type1;
    private String type2;
    private String region;
    private String evolution_stage;
    private String evo_tag;
    private String category;

    Pokemon() {
        this.dexNum = 0;
        this.name = "Unnamed";
        this.form = "NONE";
        this.type1 = "NONE";
        this.type2 = "NONE";
        this.region = "Unnamed";
        this.evolution_stage = "N/A";
        this.evo_tag = "NONE";
        this.category = "NONE";
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
    public String getForm() {
        return form;
    }
    public void setForm(String form) {
        this.form = form;
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
        return this.evolution_stage;
    }
    public void setEvolution(String evolution) {
        this.evolution_stage = evolution;
    }
    public String getRegion() {
        return this.region;
    }
    public void setRegion(String region) {
        this.region = region;
    }
    public String getEvoTag() {
        return this.evo_tag;
    }
    public void setEvoTag(String tag) {
        this.evo_tag = tag;
    }
    public String getCategory() {
        return category;
    }
    public void setCategory(String category) {
        this.category = category;
    }
}