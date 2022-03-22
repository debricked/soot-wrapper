package SootWrapper;

import java.util.Set;

public class AnalysisResult {
    private final Set<String> phantoms;
    private final Set<String> badPhantoms;

    public AnalysisResult(Set<String> phantoms, Set<String> badPhantoms) {
        this.phantoms = phantoms;
        this.badPhantoms = badPhantoms;
    }

    public Set<String> getPhantoms() {
        return phantoms;
    }

    public Set<String> getBadPhantoms() {
        return badPhantoms;
    }
}
