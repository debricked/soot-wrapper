package jarDependency;

public class JarDependency {

    public JarDependency() {}

    public int dependencyMethodCalledFromMain() {
        return this.nestedMethodCalledFromMethodCalledFromMain();
    }

    private int nestedMethodCalledFromMethodCalledFromMain() {
        return 5;
    }

    public int dependencyMethodCalledFromNotMain() {
        return nestedMethodCalledFromMethodCalledFromNotMain();
    }

    private int nestedMethodCalledFromMethodCalledFromNotMain() {
        return 6;
    }

    public int dependencyMethodNotCalled() {
        return nestedMethodOnlyCalledFromDependencyMethodNotCalled();
    }

    private int nestedMethodOnlyCalledFromDependencyMethodNotCalled() {
        return 7;
    }
}
