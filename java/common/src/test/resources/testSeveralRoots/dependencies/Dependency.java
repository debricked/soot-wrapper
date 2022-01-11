public class Dependency {
    public void dependencyFunctionOne() {
        dependencyFunctionTwo();
    }

    public void dependencyFunctionTwo() {
        dependencyFunctionThree();
    }

    public void dependencyFunctionThree() {
        dependencyFunctionFour();
    }

    public void dependencyFunctionFour() {
        dependencyFunctionFive();
    }

    public void dependencyFunctionFive() {
        System.out.println("End of chain");
    }
}
