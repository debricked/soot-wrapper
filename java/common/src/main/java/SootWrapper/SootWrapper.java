package SootWrapper;

import org.json.JSONArray;
import org.json.JSONWriter;
import soot.*;
import soot.jimple.toolkits.callgraph.CallGraph;
import soot.jimple.toolkits.callgraph.Edge;

import java.io.File;
import java.nio.file.Path;
import java.util.*;

public class SootWrapper {
    public static final String ERR_NO_ENTRY_POINTS = "Error: Found no entry points. Do path(s) to user code contain compiled user code?";

    private static final String[] skipClassesStartingWith = {"java.", "javax.", "jdk.internal.", "sun.", "soot.dummy.InvokeDynamic"};

    public static AnalysisResult writeAnalysis(JSONWriter jwriter, Iterable<? extends Path> pathToClassFiles, Iterable<? extends Path> pathToLibs) {
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
        long startNano = System.nanoTime();
        System.out.println("Analyses started on " + new Date());

        CallGraph cg = Scene.v().getCallGraph();

        Collection<SootClass> entryClasses = new HashSet<>();
        Collection<SootMethod> analysedMethods = new HashSet<>();
        Deque<SootMethod> methodsToAnalyse = new ArrayDeque<>();
        for (SootMethod m : Scene.v().getEntryPoints()) {
            if (m.isJavaLibraryMethod()) {
                continue;
            }
            methodsToAnalyse.add(m);
            entryClasses.add(m.getDeclaringClass());
        }
        if (entryClasses.isEmpty()) {
            throw new RuntimeException(ERR_NO_ENTRY_POINTS);
        }
        while (!methodsToAnalyse.isEmpty()) {
            SootMethod methodToAnalyse = methodsToAnalyse.pop();
            if (analysedMethods.contains(methodToAnalyse)) {
                continue;
            }
            analysedMethods.add(methodToAnalyse);

            jwriter.value(getSignatureJSONArray(methodToAnalyse, cg, pathToClassFiles));

            Iterator<Edge> edgesOut = cg.edgesOutOf(methodToAnalyse);
            while (edgesOut.hasNext()) {
                Edge e = edgesOut.next();
                MethodOrMethodContext target = e.getTgt();
                SootMethod targetMethod = target instanceof MethodContext ? target.method() : (SootMethod) target;
                if (!analysedMethods.contains(targetMethod)) {
                    methodsToAnalyse.push(targetMethod);
                }
            }
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

        long runtime = (System.nanoTime() - startNano) / 1000000L;
        System.out.println("Analysis finished on " + new Date());
        System.out.println("Analysis has run for " + runtime / 60000L + " min. " + runtime % 60000L / 1000L + " sec.");

        return new AnalysisResult(phantoms, badPhantoms);
    }

    private static JSONArray getSignatureJSONArray(SootMethod methodToAnalyse, CallGraph cg, Iterable<? extends Path> pathToClassFiles) {
        TargetSignature targetSignature = getFormattedTargetSignature(methodToAnalyse);
        JSONArray callee = new JSONArray();
        callee.put(targetSignature.getMethod());
        callee.put(targetSignature.isApplicationClass());
        callee.put(targetSignature.isJavaLibraryClass());
        callee.put(targetSignature.getClassName());
        callee.put(targetSignature.getFileName());
        callee.put(targetSignature.getStartLineNumber());
        callee.put(targetSignature.getEndLineNumber());

        JSONArray callers = new JSONArray();
        Iterator<Edge> edgesInto = cg.edgesInto(methodToAnalyse);
        while (edgesInto.hasNext()) {
            Edge e = edgesInto.next();
            MethodOrMethodContext source = e.getSrc();
            SootMethod sourceMethod = source instanceof MethodContext ? source.method() : (SootMethod) source;
            SourceSignature sourceSignature = getFormattedSourceSignature(
                sourceMethod,
                e.srcStmt() == null ? -1 : e.srcStmt().getJavaSourceStartLineNumber(),
                pathToClassFiles
            );
            JSONArray caller = new JSONArray();
            caller.put(sourceSignature.getMethod());
            caller.put(sourceSignature.getLineNumber());
            caller.put(sourceSignature.getFileName());
            callers.put(caller);
        }
        callee.put(callers);

        return callee;
    }

    private static SourceSignature getFormattedSourceSignature(SootMethod method, int lineNumber, Iterable<? extends Path> pathToClassFiles) {
        return method == null
                ? new SourceSignature("-", -1, "-")
                : new SourceSignature(
                    getSignatureString(method),
                    lineNumber,
                    getProbableSourceName(method, pathToClassFiles)
                );
    }

    private static TargetSignature getFormattedTargetSignature(SootMethod method) {
        return new TargetSignature(
                getSignatureString(method),
                method.getDeclaringClass().isApplicationClass(),
                method.getDeclaringClass().isJavaLibraryClass(),
                method.getDeclaringClass().getName(),
                getProbableName(method.getDeclaringClass()),
                method.getJavaSourceStartLineNumber(),
                -1 // todo source end line number
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

    private static String getModuleString(SootMethod method) {
        StringBuilder sb = new StringBuilder();
        String classString = method.getDeclaringClass().toString();
        boolean foundDot = false;
        for (int i = 0; i < classString.length(); i++) {
            char c = classString.charAt(i);
            if (c != '.') {
                sb.append(c);
            } else {
                foundDot = true;
                break;
            }
        }
        if (!foundDot) {
            return "";
        }
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

    private static String getProbableSourceName(SootMethod method, Iterable<? extends Path> pathToClassFiles) {
        String moduleName = getModuleString(method);
        String onlyDeclaringClassName = method.getDeclaringClass().getName().replaceFirst(moduleName + ".", "/");
        if (moduleName.length() == 0) {
            return "<unknown>";
        }
        for (Path path : pathToClassFiles) {
            if (path.toString().endsWith(moduleName)) {
                return path.toString() + onlyDeclaringClassName + ".java";
            }
        }
        return "-";
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
