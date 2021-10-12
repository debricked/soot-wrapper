public class TwoLibraryClass {
    public static void libraryMethod() {
        privateLibraryMethod();
    }

    private static void privateLibraryMethod() {
        System.out.println("second");
    }
}