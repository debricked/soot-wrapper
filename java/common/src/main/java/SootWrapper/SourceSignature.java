package SootWrapper;

public class SourceSignature {
    private final String method;

    private final int lineNumber;

    public SourceSignature(String method, int lineNumber) {
        this.method = method;
        this.lineNumber = lineNumber;
    }

    public String getMethod() {
        return method;
    }

    public int getLineNumber() {
        return lineNumber;
    }
}
