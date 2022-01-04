public class ShortcutInfo {

    private final String userCodeMethod;

    private final SourceSignature firstDependencyCall;

    public ShortcutInfo(String userCodeMethod, String firstDependencyCall, int lineNumberFirstDependencyCall) {
        this.userCodeMethod = userCodeMethod;
        this.firstDependencyCall = new SourceSignature(firstDependencyCall, lineNumberFirstDependencyCall);
    }

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
