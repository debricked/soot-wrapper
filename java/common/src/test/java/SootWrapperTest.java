import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;

import java.io.FileNotFoundException;
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
        Map<TargetSignature, Set<SourceSignature>> calls = res.getCallGraph();
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
        for (TargetSignature key : calls.keySet()) {
            for (String unwantedSignature : unwantedSignatures) {
                assertNotEquals(unwantedSignature, key.getMethod());
                for (SourceSignature value : calls.get(key)) {
                    assertNotEquals(unwantedSignature, value.getMethod());
                }
            }
        }
    }

    @Test
    public void testInheritance() {
        AnalysisResult res = SootWrapper.doAnalysis(
                Collections.singletonList(Paths.get(basePath + "testInheritance/userCode")),
                Collections.singletonList(Paths.get(basePath + "testInheritance/dependencies")));
        Map<TargetSignature, Set<SourceSignature>> calls = res.getCallGraph();
        assertTrue(res.getBadPhantoms().isEmpty(),
                String.format("Expected no bad phantoms. Was: %s", res.getBadPhantoms().toString()));
        assertTrue(res.getPhantoms().isEmpty(),
                String.format("Expected no phantoms. Was: %s", res.getPhantoms().toString()));
        boolean[] founds = { false, false, false, false };
        for (TargetSignature callee : calls.keySet()) {
            switch (callee.getMethod()) {
                case "Main.method()":
                    assertTrue(callee.isApplicationClass());
                    assertFalse(callee.isJavaLibraryClass());
                    assertEquals("Main", callee.getClassName());
                    assertEquals("Main.java", callee.getFileName());
                    assertEquals(2, callee.getStartLineNumber());
                    assertEquals(-1, callee.getEndLineNumber());
                    assertEquals("Main.method()", callee.getUserCodeMethod());
                    founds[0] = true;
                    break;
                case "Child.<init>()":
                    assertFalse(callee.isApplicationClass());
                    assertFalse(callee.isJavaLibraryClass());
                    assertEquals("Child", callee.getClassName());
                    assertEquals("Child.java", callee.getFileName());
                    assertEquals(0, callee.getStartLineNumber());
                    assertEquals(-1, callee.getEndLineNumber());
                    assertEquals("Main.method()", callee.getUserCodeMethod());
                    founds[1] = true;
                    break;
                case "Parent.publicParentMethod()":
                    assertFalse(callee.isApplicationClass());
                    assertFalse(callee.isJavaLibraryClass());
                    assertEquals("Parent", callee.getClassName());
                    assertEquals("Parent.java", callee.getFileName());
                    assertEquals(2, callee.getStartLineNumber());
                    assertEquals(-1, callee.getEndLineNumber());
                    assertEquals("Main.method()", callee.getUserCodeMethod());
                    founds[2] = true;
                    break;
                case "Parent.privateParentMethod()":
                    assertFalse(callee.isApplicationClass());
                    assertFalse(callee.isJavaLibraryClass());
                    assertEquals("Parent", callee.getClassName());
                    assertEquals("Parent.java", callee.getFileName());
                    assertEquals(5, callee.getStartLineNumber());
                    assertEquals(-1, callee.getEndLineNumber());
                    assertEquals("Main.method()", callee.getUserCodeMethod());
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
        Map<TargetSignature, Set<SourceSignature>> calls = res.getCallGraph();
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

    @Test
    public void testSeveralPaths() {
        AnalysisResult res = SootWrapper.doAnalysis(
                Arrays.asList(Paths.get(basePath + "testSeveralPaths/firstUserCode"), Paths.get(basePath + "testSeveralPaths/secondUserCode")),
                Arrays.asList(Paths.get(basePath + "testSeveralPaths/firstLibraryCode"), Paths.get(basePath + "testSeveralPaths/secondLibraryCode")));
        Map<TargetSignature, Set<SourceSignature>> calls = res.getCallGraph();
        assertTrue(res.getBadPhantoms().isEmpty(),
                String.format("Expected no bad phantoms. Was: %s", res.getBadPhantoms().toString()));
        assertTrue(res.getPhantoms().isEmpty(),
                String.format("Expected no phantoms. Was: %s", res.getPhantoms().toString()));

        assertMethodIsCalledByMethods(calls, "OneLibraryClass.libraryMethod()", new String[]{
                "FirstUserCode.oneMethod()",
                "SecondUserCode.oneMethod()",
        });
        assertMethodIsCalledByMethods(calls, "OneLibraryClass.privateLibraryMethod()", new String[]{
                "OneLibraryClass.libraryMethod()",
        });
        assertMethodIsCalledByMethods(calls, "java.io.PrintStream.println(String)", new String[]{
                "OneLibraryClass.privateLibraryMethod()",
                "TwoLibraryClass.privateLibraryMethod()",
        });
        assertMethodIsCalledByMethods(calls, "TwoLibraryClass.libraryMethod()", new String[]{
                "FirstUserCode.oneMethod()",
                "SecondUserCode.oneMethod()",
        });
        assertMethodIsCalledByMethods(calls, "TwoLibraryClass.privateLibraryMethod()", new String[]{
                "TwoLibraryClass.libraryMethod()",
        });
    }

    @Test
    public void testHandlesBadArguments() {
        Cli cli = new Cli();
        ArrayList<Path> paths = new ArrayList<>();
        paths.add(Paths.get(basePath + "emptyFolder"));
        cli.userCodePaths = paths;
        cli.libraryCodePaths = paths;
        boolean thrown = false;
        try {
            cli.call();
        } catch (RuntimeException e) {
            assertEquals("Error: Found no entry points. Do path(s) to user code contain compiled user code?", e.getMessage());
            thrown = true;
        } catch (Throwable e) {
            fail(e.getMessage());
        }
        assertTrue(thrown);

        thrown = false;
        paths.clear();
        paths.add(Paths.get("nonexistent"));
        cli.userCodePaths = paths;
        try {
            cli.call();
        } catch (FileNotFoundException e) {
            assertEquals("Error: nonexistent can't be found", e.getMessage());
            thrown = true;
        } catch (Throwable e) {
            fail(e.getMessage());
        }
        assertTrue(thrown);

        thrown = false;
        paths.clear();
        paths.add(Paths.get("/dev/null"));
        cli.userCodePaths = paths;
        try {
            cli.call();
        } catch (IllegalArgumentException e) {
            assertEquals("Error: /dev/null is not a directory", e.getMessage());
            thrown = true;
        } catch (Throwable e) {
            fail(e.getMessage());
        }
        assertTrue(thrown);
    }

    // This test takes too long to run in the pipeline
    @Test @Disabled
    public void testGetCallGraphSelf() {
        try {
            // remember to run `mvn package` and `mvn dependency:copy-dependencies -DoutputDirectory="target/dependency"` to populate the below folders
            AnalysisResult res = SootWrapper.doAnalysis(
                    Collections.singletonList(Paths.get("target/classes")),
                    Collections.singletonList(Paths.get("target/dependency")));
            Map<TargetSignature, Set<SourceSignature>> calls = res.getCallGraph();
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

    private void assertMethodIsCalledByMethods(Map<TargetSignature, Set<SourceSignature>> calls, String callee, String[] callers) {
        boolean found = false;
        TargetSignature index = null;
        for (TargetSignature callGraphCallee : calls.keySet()) {
            if (callGraphCallee.getMethod().equals(callee)) {
                found = true;
                index = callGraphCallee;
                break;
            }
        }
        if (!found) {
            StringBuilder callees = new StringBuilder();
            for (TargetSignature callerString : calls.keySet()) {
                callees.append(callerString.getMethod()).append(", ");
            }
            fail(String.format("Failed asserting that %s is a callee. Callees: %s\n", callee, callees));
        }
        assertNotNull(index);
        for (String caller : callers) {
            found = false;
            for (SourceSignature calledBy : calls.get(index)) {
                if (calledBy.getMethod().equals(caller)) {
                    found = true;
                    break;
                }
            }
            if (!found) {
                StringBuilder sourcesString = new StringBuilder();
                for (SourceSignature sourceString : calls.get(index)) {
                    sourcesString.append(sourceString.getMethod()).append(", ");
                }
                fail(String.format("Failed asserting that %s is called by %s. Set of calling methods: %s\n", callee, caller, sourcesString));
            }
        }
    }
}
