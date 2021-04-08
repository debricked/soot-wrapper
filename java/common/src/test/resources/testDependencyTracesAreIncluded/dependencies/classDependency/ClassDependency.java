package classDependency;

public class ClassDependency {

    public ClassDependency() {}

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
