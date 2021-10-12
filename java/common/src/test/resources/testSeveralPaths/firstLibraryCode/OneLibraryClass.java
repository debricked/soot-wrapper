public class OneLibraryClass {
    public static void libraryMethod() {
        privateLibraryMethod();
    }

    private static void privateLibraryMethod() {
        System.out.println("first");
    }
}