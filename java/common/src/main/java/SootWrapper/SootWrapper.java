package SootWrapper;

import soot.*;
import soot.jimple.toolkits.callgraph.CallGraph;
import soot.jimple.toolkits.callgraph.Edge;

import java.io.File;
import java.nio.file.Path;
import java.util.*;

public class SootWrapper {
    public static final String ERR_NO_ENTRY_POINTS = "Error: Found no entry points. Do path(s) to user code contain compiled user code?";

    private static final String[] skipClassesStartingWith = {"java.", "javax.", "jdk.internal.", "sun.", "soot.dummy.InvokeDynamic"};

    public static AnalysisResult doAnalysis(Iterable<Path> pathToClassFiles, Iterable<Path> pathToLibs) {
        G.reset(); // Reset to start fresh in case we do several analyses

        ArrayList<String> argsList = new ArrayList<>(Arrays.asList(
                "--whole-program"           // Whole program mode, required to generate call graphs
                ,"--no-bodies-for-excluded" // Don't analyse default classes (java.* etc.) Significantly reduces running time, but means we lose out on calls that go from JDK and into code to analyse
                ,"--output-format", "none"  // We don't care about the output
                ,"--keep-line-number"       // Keep line numbers
        ));
        for (Path p : pathToClassFiles) {
            argsList.add("--process-path"); // Process the pathToClassFiles dirs
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

        Collection<SootClass> entryClasses = new HashSet<>();
        Map<TargetSignature, Set<SourceSignature>> calls = new HashMap<>();
        Map<SootMethod, Set<SootMethod>> analysedMethods = new HashMap<>();
        Map<SootMethod, TargetSignature> targetSignatureLookup = new HashMap<>();
        for (SootMethod m : Scene.v().getEntryPoints()) {
            if (m.isJavaLibraryMethod()) {
                continue;
            }
            analyseMethod(calls, cg, m, analysedMethods, targetSignatureLookup, m, null, -1);
            entryClasses.add(m.getDeclaringClass());
        }
        if (entryClasses.isEmpty()) {
            throw new RuntimeException(ERR_NO_ENTRY_POINTS);
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

    private static void analyseMethod(
            Map<TargetSignature, Set<SourceSignature>> calls,
            CallGraph cg,
            SootMethod m,
            Map<SootMethod, Set<SootMethod>> analysedMethods,
            Map<SootMethod, TargetSignature> targetSignatureLookup,
            SootMethod originatingMethod,
            SootMethod firstDependencyMethod,
            int lineNumberFirstDependencyMethod) {
        // Mark this combination of method and originating method as analysed
        if (!analysedMethods.containsKey(m)) {
            analysedMethods.put(m, new HashSet<>());
        }
        analysedMethods.get(m).add(originatingMethod);

        // Create a lookup entry to we can find this targetSignature in the future
        if (targetSignatureLookup.get(m) == null) {
            targetSignatureLookup.put(m, getFormattedTargetSignature(m));
        }

        TargetSignature formattedTarget = targetSignatureLookup.get(m);
        formattedTarget.getShortcutInfos().add(new ShortcutInfo(getSignatureString(originatingMethod), getFormattedSourceSignature(firstDependencyMethod, lineNumberFirstDependencyMethod)));
        // If we have already analysed this target from some other root, we don't need to build relations, only add shortcut info
        if (!calls.containsKey(formattedTarget)) {
            Set<SourceSignature> sourceSignatures = new HashSet<>();
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
                SourceSignature sourceSignature = getFormattedSourceSignature(sourceMethod, e.srcStmt() == null ? -1 : e.srcStmt().getJavaSourceStartLineNumber());
                sourceSignatures.add(sourceSignature);
            }
            calls.put(formattedTarget, sourceSignatures);
        }

        Iterator<Edge> edgesOut = cg.edgesOutOf(m);
        while (edgesOut.hasNext()) {
            Edge e = edgesOut.next();
            MethodOrMethodContext target = e.getTgt();
            SootMethod targetMethod = target instanceof MethodContext ? target.method() : (SootMethod) target;
            if (!(analysedMethods.containsKey(targetMethod) && analysedMethods.get(targetMethod).contains(originatingMethod))) {
                if (firstDependencyMethod == null) {
                    // This is the first dependency method
                    analyseMethod(calls, cg, targetMethod, analysedMethods, targetSignatureLookup, originatingMethod, targetMethod, e.srcStmt() == null ? -1 : e.srcStmt().getJavaSourceStartLineNumber());
                } else {
                    analyseMethod(calls, cg, targetMethod, analysedMethods, targetSignatureLookup, originatingMethod, firstDependencyMethod, lineNumberFirstDependencyMethod);
                }
            }
        }
    }

    private static SourceSignature getFormattedSourceSignature(SootMethod method, int lineNumber) {
        return method == null
                ? new SourceSignature("-", -1)
                : new SourceSignature(getSignatureString(method), lineNumber);
    }

    private static TargetSignature getFormattedTargetSignature(SootMethod method) {
        return new TargetSignature(
                getSignatureString(method),
                method.getDeclaringClass().isApplicationClass(),
                method.getDeclaringClass().isJavaLibraryClass(),
                method.getDeclaringClass().getName(),
                getProbableName(method.getDeclaringClass()),
                method.getJavaSourceStartLineNumber(),
                -1, // todo source end line number
                new HashSet<>()
        );
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
        return jarsPath.isEmpty() ? jarsPath : jarsPath.substring(0, jarsPath.length()-1);
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
