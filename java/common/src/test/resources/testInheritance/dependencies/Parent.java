public abstract class Parent {
    public void publicParentMethod() {
        privateParentMethod();
    }

    private void privateParentMethod() {}
}
