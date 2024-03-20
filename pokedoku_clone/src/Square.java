public class Square {
    public Requirement req1;
    public Requirement req2;

    public void setReq1(String req, int type) {
        this.req1 = new Requirement(req, type);
    }
    public void setReq2(String req, int type) {
        this.req2 = new Requirement(req, type);
    }

    public Square() {
        this.req1 = new Requirement();
        this.req2 = new Requirement();
    }
}
