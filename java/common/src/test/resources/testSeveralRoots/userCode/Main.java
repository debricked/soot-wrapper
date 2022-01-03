public class Main {
    public void userFunctionA() {
        new Dependency().dependencyFunctionOne();
    }

    public void userFunctionB() {
        new Dependency().dependencyFunctionOne();
    }

    public void userFunctionC() {
        new Dependency().dependencyFunctionThree();
    }
}
