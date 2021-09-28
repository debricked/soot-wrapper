public class TargetSignature {
    private final String method;

    private final boolean isApplicationClass;

    private final boolean isJavaLibraryClass;

    private final String className;

    private final String fileName;

    private final int startLineNumber;

    private final int endLineNumber;

    private final String userCodeMethod;

    private final SourceSignature firstDependencyCall;

    public TargetSignature(
            String method,
            boolean isApplicationClass,
            boolean isJavaLibraryClass,
            String className,
            String fileName,
            int startLineNumber,
            int endLineNumber,
            String userCodeMethod,
            SourceSignature firstDependencyCall
    ) {
        this.method = method;
        this.isApplicationClass = isApplicationClass;
        this.isJavaLibraryClass = isJavaLibraryClass;
        this.className = className;
        this.fileName = fileName;
        this.startLineNumber = startLineNumber;
        this.endLineNumber = endLineNumber;
        this.userCodeMethod = userCodeMethod;
        this.firstDependencyCall = firstDependencyCall;
    }

    public String getMethod() {
        return method;
    }

    public boolean isApplicationClass() {
        return isApplicationClass;
    }

    public boolean isJavaLibraryClass() {
        return isJavaLibraryClass;
    }

    public String getClassName() {
        return className;
    }

    public String getFileName() {
        return fileName;
    }

    public int getStartLineNumber() {
        return startLineNumber;
    }

    public int getEndLineNumber() {
        return endLineNumber;
    }

    public String getUserCodeMethod() {
        return userCodeMethod;
    }

    public SourceSignature getFirstDependencyCall() {
        return firstDependencyCall;
    }
}
