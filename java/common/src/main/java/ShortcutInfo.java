public class ShortcutInfo {

    private final String userCodeMethod;

    private final SourceSignature firstDependencyCall;

    public ShortcutInfo(String userCodeMethod, SourceSignature firstDependencyCall) {
        this.userCodeMethod = userCodeMethod;
        this.firstDependencyCall = firstDependencyCall;
    }

    public String getUserCodeMethod() {
        return userCodeMethod;
    }

    public SourceSignature getFirstDependencyCall() {
        return firstDependencyCall;
    }
}
