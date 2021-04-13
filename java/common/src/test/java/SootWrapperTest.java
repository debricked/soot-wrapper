import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;

import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.*;

import static org.junit.jupiter.api.Assertions.*;

public class SootWrapperTest {
    private static final String basePath = "src/test/resources/";

    @Test
    public void testGetJarsInFoldersAndSubfolders() {
        String libraryPath = basePath + "testGetJarsInFoldersAndSubfolders";
        String path = SootWrapper.getJarsInFoldersAndSubfolders(Path.of(libraryPath));
        String[] paths = path.split(":");
        Arrays.sort(paths);
        assertTrue(paths[0].endsWith(libraryPath + "/dummy.jar"),
                String.format("Expected to find %s/subfolder/dummy.jar in paths[0], was %s", libraryPath, paths[0]));
        assertTrue(paths[1].endsWith(libraryPath + "/subfolder/dummy.jar"),
                String.format("Expected to find %s/dummy.jar in paths[1], was %s", libraryPath, paths[1]));
    }

    @Test
    public void testDependencyTracesAreIncludedAndUnusedUserCodeMethodsAreIncludedAndUnusedDependencyMethodsAreNotIncluded() {
        AnalysisResult res = SootWrapper.doAnalysis(
                Collections.singletonList(Paths.get(basePath + "testDependencyTracesAreIncluded/userCode")),
                Collections.singletonList(Paths.get(basePath + "testDependencyTracesAreIncluded/dependencies")));
        Map<String, Set<String>> calls = res.getCallGraph();
        assertTrue(res.getBadPhantoms().isEmpty(),
                String.format("Expected no bad phantoms. Was: %s", res.getBadPhantoms().toString()));
        assertTrue(res.getPhantoms().isEmpty(),
                String.format("Expected no phantoms. Was: %s", res.getPhantoms().toString()));
        assertMethodCallsMethods(calls, "Main.main(String[])", new String[]{
                "classDependency.ClassDependency.<init>()"
                ,"classDependency.ClassDependency.dependencyMethodCalledFromMain()"
                ,"jarDependency.JarDependency.<init>()"
                ,"jarDependency.JarDependency.dependencyMethodCalledFromMain()"
        });
        assertMethodCallsMethods(calls, "classDependency.ClassDependency.dependencyMethodCalledFromMain()", new String[]{
                "classDependency.ClassDependency.nestedMethodCalledFromMethodCalledFromMain()"
        });
        assertMethodCallsMethods(calls, "jarDependency.JarDependency.dependencyMethodCalledFromMain()", new String[]{
                "jarDependency.JarDependency.nestedMethodCalledFromMethodCalledFromMain()"
        });
        assertMethodCallsMethods(calls, "Main.unusedUserCodeMethod()", new String[]{
                "classDependency.ClassDependency.<init>()"
                ,"classDependency.ClassDependency.dependencyMethodCalledFromNotMain()"
                ,"jarDependency.JarDependency.<init>()"
                ,"jarDependency.JarDependency.dependencyMethodCalledFromNotMain()"
        });
        assertMethodCallsMethods(calls, "classDependency.ClassDependency.dependencyMethodCalledFromNotMain()", new String[]{
                "classDependency.ClassDependency.nestedMethodCalledFromMethodCalledFromNotMain()"
        });
        assertMethodCallsMethods(calls, "jarDependency.JarDependency.dependencyMethodCalledFromNotMain()", new String[]{
                "jarDependency.JarDependency.nestedMethodCalledFromMethodCalledFromNotMain()"
        });
        String[] unwantedSignatures = new String[]{
                "classDependency.ClassDependency.nestedMethodOnlyCalledFromDependencyMethodNotCalled()"
                ,"classDependency.ClassDependency.dependencyMethodNotCalled()"
                ,"jarDependency.JarDependency.nestedMethodOnlyCalledFromDependencyMethodNotCalled()"
                ,"jarDependency.JarDependency.dependencyMethodNotCalled()"
        };
        for (String key : calls.keySet()) {
            for (String unwantedSignature : unwantedSignatures) {
                assertNotEquals(unwantedSignature, key);
                assertFalse(calls.get(key).contains(unwantedSignature));
            }
        }
    }

    @Test
    public void testInheritance() {
        AnalysisResult res = SootWrapper.doAnalysis(
                Collections.singletonList(Paths.get(basePath + "testInheritance/userCode")),
                Collections.singletonList(Paths.get(basePath + "testInheritance/dependencies")));
        Map<String, Set<String>> calls = res.getCallGraph();
        assertTrue(res.getBadPhantoms().isEmpty(),
                String.format("Expected no bad phantoms. Was: %s", res.getBadPhantoms().toString()));
        assertTrue(res.getPhantoms().isEmpty(),
                String.format("Expected no phantoms. Was: %s", res.getPhantoms().toString()));
        assertMethodCallsMethods(calls, "Main.method()", new String[]{"Parent.publicParentMethod()"});
        assertMethodCallsMethods(calls, "Parent.publicParentMethod()", new String[]{"Parent.privateParentMethod()"});
        assertMethodCallsMethods(calls, "Parent.privateParentMethod()", new String[]{});
    }

    @Test @Disabled
    public void testParameterization() {
        // todo test that parameterized method parameters (eg. Class.method(List<String>)) and
        //  parameterized classes (eg. package.Class<Type>.add(Type)) look the way we want them to
    }

    // This test takes too long to run in the pipeline
    @Test @Disabled
    public void testGetCallGraphSelf() {
        try {
            // remember to run `mvn package` to populate the below folders
            AnalysisResult res = SootWrapper.doAnalysis(
                    Collections.singletonList(Paths.get("target/classes")),
                    Collections.singletonList(Paths.get("target/dependency")));
            Map<String, Set<String>> calls = res.getCallGraph();
            assertTrue(res.getBadPhantoms().isEmpty(),
                    String.format("Expected no bad phantoms. Was: %s", res.getBadPhantoms().toString()));
            assertMethodCallsMethods(calls, "Cli.main(String[])", new String[]{
                    "picocli.CommandLine.<init>(Object)"
            });
            assertMethodCallsMethods(calls, "Cli.checkExistsAndIsDir(Collection)", new String[]{
                    "java.io.File.exists()"
                    ,"java.io.FileNotFoundException.<init>(String)"
                    ,"java.io.File.isDirectory()"
                    ,"java.lang.IllegalArgumentException.<init>(String)"
            });
            assertMethodCallsMethods(calls, "SootWrapper.doAnalysis(Collection, Collection)", new String[]{
                    "soot.G.reset()"
                    ,"soot.Scene.v()"
                    ,"soot.Scene.getSootClassPath()"
                    ,"soot.Scene.extendSootClassPath(String)"
                    ,"soot.PhaseOptions.setPhaseOption(String, String)"
                    ,"soot.Main.main(String[])"
            });
            assertMethodCallsMethods(calls, "soot.jimple.toolkits.callgraph.CallGraph.edgesOutOf(MethodOrMethodContext)", new String[]{
                    "soot.jimple.toolkits.callgraph.CallGraph$TargetsOfMethodIterator.<init>(CallGraph, MethodOrMethodContext)" // todo Is this how we want subclass signatures to look?
            });
            assertMethodCallsMethods(calls, "soot.Main.main(String[])", new String[]{
                    "soot.Main.v()"
                    ,"soot.Main.run(String[])"
            });
            assertMethodCallsMethods(calls, "soot.Main.run(String[])", new String[]{
                    "java.lang.System.nanoTime()"
                    ,"soot.Timers.v()"
                    ,"soot.Timer.start()"
            });
        } catch (Exception e) {
            fail(e.getMessage());
        }
    }

    private void assertMethodCallsMethods(Map<String, Set<String>> calls, String caller, String[] callees) {
        assertTrue(calls.containsKey(caller), String.format("Failed asserting that %s is a caller. Callers: %s\n", caller, calls.keySet().toString()));
        for (String callee : callees) {
            assertTrue(calls.get(caller).contains(callee), String.format("Failed asserting that %s calls %s. Set of called methods: %s\n", caller, callee, calls.get(caller).toString()));
        }
    }
}
