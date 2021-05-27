import java.util.Map;
import java.util.Set;

public class AnalysisResult {
    private final Map<String[], Set<String[]>> callGraph;
    private final Set<String> phantoms;
    private final Set<String> badPhantoms;

    public AnalysisResult(Map<String[], Set<String[]>> callGraph, Set<String> phantoms, Set<String> badPhantoms) {
        this.callGraph = callGraph;
        this.phantoms = phantoms;
        this.badPhantoms = badPhantoms;
    }

    public Map<String[], Set<String[]>> getCallGraph() {
        return callGraph;
    }

    public Set<String> getPhantoms() {
        return phantoms;
    }

    public Set<String> getBadPhantoms() {
        return badPhantoms;
    }
}
