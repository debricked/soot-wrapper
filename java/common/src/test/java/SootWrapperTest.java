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
        Map<String[], Set<String[]>> calls = res.getCallGraph();
        assertTrue(res.getBadPhantoms().isEmpty(),
                String.format("Expected no bad phantoms. Was: %s", res.getBadPhantoms().toString()));
        assertTrue(res.getPhantoms().isEmpty(),
                String.format("Expected no phantoms. Was: %s", res.getPhantoms().toString()));
        assertMethodIsCalledByMethods(calls, "classDependency.ClassDependency.<init>()", new String[]{
                "Main.main(String[])"
                ,"Main.unusedUserCodeMethod()"
        });
        assertMethodIsCalledByMethods(calls, "classDependency.ClassDependency.dependencyMethodCalledFromMain()", new String[]{
                "Main.main(String[])"
        });
        assertMethodIsCalledByMethods(calls, "jarDependency.JarDependency.<init>()", new String[]{
                "Main.main(String[])"
                ,"Main.unusedUserCodeMethod()"
        });
        assertMethodIsCalledByMethods(calls, "jarDependency.JarDependency.dependencyMethodCalledFromMain()", new String[]{
                "Main.main(String[])"
        });
        assertMethodIsCalledByMethods(calls, "classDependency.ClassDependency.nestedMethodCalledFromMethodCalledFromMain()", new String[]{
                "classDependency.ClassDependency.dependencyMethodCalledFromMain()"
        });
        assertMethodIsCalledByMethods(calls, "jarDependency.JarDependency.nestedMethodCalledFromMethodCalledFromMain()", new String[]{
                "jarDependency.JarDependency.dependencyMethodCalledFromMain()"
        });
        assertMethodIsCalledByMethods(calls, "classDependency.ClassDependency.dependencyMethodCalledFromNotMain()", new String[]{
                "Main.unusedUserCodeMethod()"
        });
        assertMethodIsCalledByMethods(calls, "jarDependency.JarDependency.dependencyMethodCalledFromNotMain()", new String[]{
                "Main.unusedUserCodeMethod()"
        });
        assertMethodIsCalledByMethods(calls, "classDependency.ClassDependency.nestedMethodCalledFromMethodCalledFromNotMain()", new String[]{
                "classDependency.ClassDependency.dependencyMethodCalledFromNotMain()"
        });
        assertMethodIsCalledByMethods(calls, "jarDependency.JarDependency.nestedMethodCalledFromMethodCalledFromNotMain()", new String[]{
                "jarDependency.JarDependency.dependencyMethodCalledFromNotMain()"
        });
        String[] unwantedSignatures = new String[]{
                "classDependency.ClassDependency.nestedMethodOnlyCalledFromDependencyMethodNotCalled()"
                ,"classDependency.ClassDependency.dependencyMethodNotCalled()"
                ,"jarDependency.JarDependency.nestedMethodOnlyCalledFromDependencyMethodNotCalled()"
                ,"jarDependency.JarDependency.dependencyMethodNotCalled()"
        };
        for (String[] key : calls.keySet()) {
            for (String unwantedSignature : unwantedSignatures) {
                assertNotEquals(unwantedSignature, key[3]);
                for (String[] value : calls.get(key)) {
                    assertNotEquals(unwantedSignature, value[1]);
                }
            }
        }
    }

    @Test
    public void testInheritance() {
        AnalysisResult res = SootWrapper.doAnalysis(
                Collections.singletonList(Paths.get(basePath + "testInheritance/userCode")),
                Collections.singletonList(Paths.get(basePath + "testInheritance/dependencies")));
        Map<String[], Set<String[]>> calls = res.getCallGraph();
        assertTrue(res.getBadPhantoms().isEmpty(),
                String.format("Expected no bad phantoms. Was: %s", res.getBadPhantoms().toString()));
        assertTrue(res.getPhantoms().isEmpty(),
                String.format("Expected no phantoms. Was: %s", res.getPhantoms().toString()));
        boolean[] founds = { false, false, false, false };
        for (String[] caller : calls.keySet()) {
            switch (caller[0]) {
                case "Main.method()":
                    assertEquals("true", caller[1]);
                    assertEquals("false", caller[2]);
                    assertEquals("Main", caller[3]);
                    assertEquals("Main.java", caller[4]);
                    assertEquals("2", caller[5]);
                    assertEquals("-1", caller[6]);
                    assertEquals("Main.method()", caller[7]);
                    founds[0] = true;
                    break;
                case "Child.<init>()":
                    assertEquals("false", caller[1]);
                    assertEquals("false", caller[2]);
                    assertEquals("Child", caller[3]);
                    assertEquals("Child.java", caller[4]);
                    assertEquals("0", caller[5]);
                    assertEquals("-1", caller[6]);
                    assertEquals("Main.method()", caller[7]);
                    founds[1] = true;
                    break;
                case "Parent.publicParentMethod()":
                    assertEquals("false", caller[1]);
                    assertEquals("false", caller[2]);
                    assertEquals("Parent", caller[3]);
                    assertEquals("Parent.java", caller[4]);
                    assertEquals("2", caller[5]);
                    assertEquals("-1", caller[6]);
                    assertEquals("Main.method()", caller[7]);
                    founds[2] = true;
                    break;
                case "Parent.privateParentMethod()":
                    assertEquals("false", caller[1]);
                    assertEquals("false", caller[2]);
                    assertEquals("Parent", caller[3]);
                    assertEquals("Parent.java", caller[4]);
                    assertEquals("5", caller[5]);
                    assertEquals("-1", caller[6]);
                    assertEquals("Main.method()", caller[7]);
                    founds[3] = true;
                    break;
            }
        }
        for (boolean found : founds) {
            assertTrue(found);
        }
        assertMethodIsCalledByMethods(calls, "Parent.publicParentMethod()", new String[]{"Main.method()"});
        assertMethodIsCalledByMethods(calls, "Parent.privateParentMethod()", new String[]{"Parent.publicParentMethod()"});
    }

    @Test @Disabled
    public void testParameterization() {
        // todo test that parameterized method parameters (eg. Class.method(List<String>)) and
        //  parameterized classes (eg. package.Class<Type>.add(Type)) look the way we want them to
    }

    @Test
    public void testPrivateAndAnonymousClasses() {
        AnalysisResult res = SootWrapper.doAnalysis(
                Collections.singletonList(Paths.get(basePath + "testPrivateAndAnonymousClasses/userCode")),
                Collections.singletonList(Paths.get(basePath + "testPrivateAndAnonymousClasses/dependencies")));
        Map<String[], Set<String[]>> calls = res.getCallGraph();
        assertTrue(res.getBadPhantoms().isEmpty(),
                String.format("Expected no bad phantoms. Was: %s", res.getBadPhantoms().toString()));
        assertTrue(res.getPhantoms().isEmpty(),
                String.format("Expected no phantoms. Was: %s", res.getPhantoms().toString()));
        assertMethodIsCalledByMethods(calls, "Dependency.<init>()", new String[]{
                "UserCode.main(String[])"
        });
        assertMethodIsCalledByMethods(calls, "Dependency.method()", new String[]{
                "UserCode.main(String[])"
        });
        assertMethodIsCalledByMethods(calls, "Dependency$1PrivateClass.<init>(Dependency)", new String[]{
                "Dependency.method()"
        });
        assertMethodIsCalledByMethods(calls, "Dependency$1PrivateClass.interfaceMethod()", new String[]{
                "Dependency.method()"
        });
        assertMethodIsCalledByMethods(calls, "Dependency$1.<init>(Dependency)", new String[]{
                "Dependency.method()"
        });
        assertMethodIsCalledByMethods(calls, "Dependency$1.interfaceMethod()", new String[]{
                "Dependency.method()"
        });
        assertMethodIsCalledByMethods(calls, "Dependency$1PrivateClass.privateClassMethod()", new String[]{
                "Dependency$1PrivateClass.interfaceMethod()"
        });
        assertMethodIsCalledByMethods(calls, "Dependency$1.anonymousClassMethod()", new String[]{
                "Dependency$1.interfaceMethod()"
        });
    }

    // This test takes too long to run in the pipeline
    @Test @Disabled
    public void testGetCallGraphSelf() {
        try {
            // remember to run `mvn package` and `mvn dependency:copy-dependencies -DoutputDirectory="target/dependency"` to populate the below folders
            AnalysisResult res = SootWrapper.doAnalysis(
                    Collections.singletonList(Paths.get("target/classes")),
                    Collections.singletonList(Paths.get("target/dependency")));
            Map<String[], Set<String[]>> calls = res.getCallGraph();
            assertTrue(res.getBadPhantoms().isEmpty(),
                    String.format("Expected no bad phantoms. Was: %s", res.getBadPhantoms().toString()));
            assertMethodIsCalledByMethods(calls, "picocli.CommandLine.<init>(Object)", new String[]{
                    "Cli.main(String[])"
            });
            assertMethodIsCalledByMethods(calls, "java.io.File.exists()", new String[]{
                    "Cli.checkExistsAndIsDir(Collection)"
            });
            assertMethodIsCalledByMethods(calls, "soot.G.reset()", new String[]{
                    "SootWrapper.doAnalysis(Collection, Collection)"
            });
            assertMethodIsCalledByMethods(calls, "soot.jimple.toolkits.callgraph.CallGraph$TargetsOfMethodIterator.<init>(CallGraph, MethodOrMethodContext)", new String[]{ // todo Is this how we want subclass signatures to look?
                    "soot.jimple.toolkits.callgraph.CallGraph.edgesOutOf(MethodOrMethodContext)"
            });
            assertMethodIsCalledByMethods(calls, "soot.Main.run(String[])", new String[]{
                    "soot.Main.main(String[])"
            });
            assertMethodIsCalledByMethods(calls, "soot.Timers.v()", new String[]{
                    "soot.Main.run(String[])"
            });
            assertMethodIsCalledByMethods(calls, "soot.SootMethod.getDeclaringClass()", new String[]{
                    "SootWrapper.getFormattedTargetSignature(SootMethod, SootMethod)"
                    ,"SootWrapper.doAnalysis(Collection, Collection)"
                    ,"SootWrapper.getSignatureString(SootMethod)"
            });
        } catch (Exception e) {
            fail(e.getMessage());
        }
    }

    private void assertMethodIsCalledByMethods(Map<String[], Set<String[]>> calls, String callee, String[] callers) {
        boolean found = false;
        String[] index = null;
        for (String[] callGraphCaller : calls.keySet()) {
            if (callGraphCaller[0].equals(callee)) {
                found = true;
                index = callGraphCaller;
                break;
            }
        }
        if (!found) {
            StringBuilder callees = new StringBuilder();
            for (String[] callerString : calls.keySet()) {
                callees.append(callerString[0]).append(", ");
            }
            fail(String.format("Failed asserting that %s is a callee. Callees: %s\n", callee, callees));
        }
        assertNotNull(index);
        for (String caller : callers) {
            found = false;
            for (String[] calledBy : calls.get(index)) {
                if (calledBy[0].equals(caller)) {
                    found = true;
                    break;
                }
            }
            if (!found) {
                StringBuilder sourcesString = new StringBuilder();
                for (String[] sourceString : calls.get(index)) {
                    sourcesString.append(sourceString[0]).append(", ");
                }
                fail(String.format("Failed asserting that %s is called by %s. Set of calling methods: %s\n", callee, caller, sourcesString));
            }
        }
    }
}
