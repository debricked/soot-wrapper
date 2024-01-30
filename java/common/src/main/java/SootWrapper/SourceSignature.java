package SootWrapper;

public class SourceSignature {
    private final String method;

    private final int lineNumber;

    private final String fileName;

    public SourceSignature(String method, int lineNumber, String fileName) {
        this.method = method;
        this.lineNumber = lineNumber;
        this.fileName = fileName;
    }

    public String getMethod() {
        return method;
    }

    public int getLineNumber() {
        return lineNumber;
    }

    public String getFileName() {
        return fileName;
    }
}
