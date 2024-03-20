public class Requirement {
    private int type;
    //0 = Pokemon Type
    //1 = Pokemon Region
    //2 = Evolution Stage
    //3 = Evolution Tag
    //4 = Category
    private String req;

    public int getType() {
        return type;
    }
    public void setType(int type) {
        this.type = type;
    }
    public String getReq() {
        return req;
    }
    public void setReq(String req) {
        this.req = req;
    }

    public Requirement() {
        this.req = "";
        this.type = -1;
    }

    public Requirement(String req, int type) {
        this.req = req;
        this.type = type;
    }

    public String reqToText() {
        String str = "";

        switch (this.type) {
            case 0:
                str = this.req + " Type";
                break;

            case 1:
                str = this.req + " Region";
                break;

            case 2:
                
                break;

            case 3:

                break;

            case 4:
                str = this.req;
                break;
        }

        return str;
    }
}
