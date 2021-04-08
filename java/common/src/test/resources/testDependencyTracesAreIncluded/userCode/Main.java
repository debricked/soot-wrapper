import classDependency.ClassDependency;
import jarDependency.JarDependency;

public class Main {
    public static void main(String[] args) {
        System.out.println(new ClassDependency().dependencyMethodCalledFromMain());
        System.out.println(new JarDependency().dependencyMethodCalledFromMain());
    }

    public static void unusedUserCodeMethod() {
        System.out.println(new ClassDependency().dependencyMethodCalledFromNotMain());
        System.out.println(new JarDependency().dependencyMethodCalledFromNotMain());
    }
}
