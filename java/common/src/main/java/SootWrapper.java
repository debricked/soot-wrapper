import soot.*;
import soot.jimple.toolkits.callgraph.CallGraph;
import soot.jimple.toolkits.callgraph.Edge;

import java.io.File;
import java.nio.file.Path;
import java.util.*;

public class SootWrapper {
    private static final String[] skipClassesStartingWith = {"java.", "javax.", "jdk.internal.", "sun.", "soot.dummy.InvokeDynamic"};

    public static AnalysisResult doAnalysis(Collection<Path> pathToClassFiles, Collection<Path> pathToLibs) {
        G.reset(); // Reset to start fresh in case we do several analyses

        ArrayList<String> argsList = new ArrayList<>(Arrays.asList(
                "--whole-program"           // Whole program mode, required to generate call graphs
                ,"--no-bodies-for-excluded" // Don't analyse default classes (java.* etc.) Significantly reduces running time, but means we lose out on calls that go from JDK and into code to analyse
                ,"--output-format", "none"  // We don't care about the output
                ,"--keep-line-number"       // Keep line numbers
                ,"--process-path"           // Process the pathToClassFiles dirs
        ));
        for (Path p : pathToClassFiles) {
            argsList.add(p.toAbsolutePath().toString());
        }

        Scene.v().getSootClassPath(); // Needs to be evaluated prior to being extended
        for (Path p : pathToClassFiles) {
            Scene.v().extendSootClassPath(p.toAbsolutePath().toString());
        }
        for (Path p : pathToLibs) {
            Scene.v().extendSootClassPath(p.toAbsolutePath().toString());
            Scene.v().extendSootClassPath(getJarsInFoldersAndSubfolders(p));
        }
//        System.out.println("Soot class path: " + Scene.v().getSootClassPath());

        PhaseOptions.v().setPhaseOption("cg", "verbose:true"); // Supposedly lets us know when it makes unsound assumptions re. reflection
        PhaseOptions.v().setPhaseOption("cg", "all-reachable:true"); // Analyse entry-points other than main

        Main.main(argsList.toArray(new String[0])); // Do analysis

        CallGraph cg = Scene.v().getCallGraph();

        Set<SootClass> entryClasses = new HashSet<>();
        Map<String[], Set<String[]>> calls = new HashMap<>();
        Set<SootMethod> analysedMethods = new HashSet<>();
        for (SootMethod m : Scene.v().getEntryPoints()) {
            analyseMethod(calls, cg, m, analysedMethods);
            entryClasses.add(m.getDeclaringClass());
        }

        Set<String> phantoms = new HashSet<>();
        Set<String> badPhantoms = new HashSet<>();
        for (SootClass phantom : Scene.v().getPhantomClasses()) {
            boolean shouldSkip = false;
            for (String s : skipClassesStartingWith) {
                if (phantom.toString().startsWith(s)) {
                    shouldSkip = true;
                    break;
                }
            }
            if (shouldSkip) continue;
            if (entryClasses.contains(phantom)) {
                badPhantoms.add(phantom.toString());
            } else {
                phantoms.add(phantom.toString());
            }
        }

        return new AnalysisResult(calls, phantoms, badPhantoms);
    }

    private static void analyseMethod(Map<String[], Set<String[]>> calls, CallGraph cg, SootMethod m, Set<SootMethod> analysedMethods) {
        analysedMethods.add(m);
        Set<String[]> sourceSignatures = new HashSet<>();
        Iterator<Edge> edgesInto = cg.edgesInto(m);
        while (edgesInto.hasNext()) {
            Edge e = edgesInto.next();
            MethodOrMethodContext source = e.getSrc();
            SootMethod sourceMethod;
            if (source instanceof MethodContext) {
                sourceMethod = source.method();
            } else {
                sourceMethod = (SootMethod) source;
            }
            String[] sourceSignature = getFormattedSourceSignature(sourceMethod, e.srcStmt() == null ? -1 : e.srcStmt().getJavaSourceStartLineNumber());
            sourceSignatures.add(sourceSignature);
        }
        calls.put(getFormattedTargetSignature(m), sourceSignatures);

        Iterator<Edge> edgesOut = cg.edgesOutOf(m);
        while (edgesOut.hasNext()) {
            Edge e = edgesOut.next();
            MethodOrMethodContext target = e.getTgt();
            SootMethod targetMethod;
            if (target instanceof MethodContext) {
                targetMethod = target.method();
            } else {
                targetMethod = (SootMethod) target;
            }
            if (!analysedMethods.contains(targetMethod)) {
                analyseMethod(calls, cg, targetMethod, analysedMethods);
            }
        }
    }

    private static String[] getFormattedSourceSignature(SootMethod method, int lineNumber) {
        return new String[] { getSignatureString(method), Integer.toString(lineNumber) };
    }

    private static String[] getFormattedTargetSignature(SootMethod method) {
        return new String[] {
                getSignatureString(method),
                method.getDeclaringClass().isApplicationClass() ? "true" : "false",
                method.getDeclaringClass().isJavaLibraryClass() ? "true" : "false",
                method.getDeclaringClass().getName(),
                getProbableName(method.getDeclaringClass()),
                Integer.toString(method.getJavaSourceStartLineNumber()),
                "-1", // todo source end line number
        };
    }

    private static String getSignatureString(SootMethod method) {
        StringBuilder sb = new StringBuilder();
        sb.append(method.getDeclaringClass());
        sb.append(".");
        sb.append(method.getName());
        sb.append("(");
        if (method.getParameterCount() > 0) {
            sb.append(getParameterClass(method.getParameterType(0)));
            for (int i = 1; i < method.getParameterCount(); i++) {
                sb.append(", ");
                sb.append(getParameterClass(method.getParameterType(i)));
            }
        }
        sb.append(")");
        return sb.toString();
    }

    private static String getProbableName(SootClass c) {
        if (c.isJavaLibraryClass()) {
            return "-";
        }
        String className = c.getName();
        int innerClassIndex = className.indexOf('$');
        if (innerClassIndex != -1) {
            // private or anonymous class
            className = className.substring(0, innerClassIndex);
        }
        className = className.replace('.', '/') + ".java";
        return className;
    }

    private static String getParameterClass(Type parameter) {
        String[] paramType = parameter.toString().split("\\.");
        return paramType[paramType.length-1];
    }

    public static String getJarsInFoldersAndSubfolders(Path p) {
        Set<String> jars = getJarsInFoldersAndSubfolders(p, new HashSet<>());
        StringBuilder sb = new StringBuilder();
        for (String jar : jars) {
            sb.append(jar);
            sb.append(":");
        }
        String jarsPath = sb.toString();
        return jarsPath.equals("") ? jarsPath : jarsPath.substring(0, jarsPath.length()-1);
    }

    private static Set<String> getJarsInFoldersAndSubfolders(Path p, Set<String> set) {
        File f = p.toFile();
        if (f.isDirectory()) {
            for (File ff : Objects.requireNonNull(f.listFiles())) {
                set.addAll(getJarsInFoldersAndSubfolders(ff.toPath(), set));
            }
        } else if (f.isFile()) {
            if (f.toString().endsWith(".jar")) {
                set.add(f.getAbsolutePath());
            }
        }
        return set;
    }

}
