package SootWrapper;

public class TargetSignature {
    private final String method;

    private final boolean isApplicationClass;

    private final boolean isJavaLibraryClass;

    private final String className;

    private final String fileName;

    private final int startLineNumber;

    private final int endLineNumber;

    public TargetSignature(
            String method,
            boolean isApplicationClass,
            boolean isJavaLibraryClass,
            String className,
            String fileName,
            int startLineNumber,
            int endLineNumber
    ) {
        this.method = method;
        this.isApplicationClass = isApplicationClass;
        this.isJavaLibraryClass = isJavaLibraryClass;
        this.className = className;
        this.fileName = fileName;
        this.startLineNumber = startLineNumber;
        this.endLineNumber = endLineNumber;
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
}
