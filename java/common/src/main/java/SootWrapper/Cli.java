package SootWrapper;

import org.json.JSONWriter;
import picocli.CommandLine;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.util.*;
import java.util.concurrent.Callable;

@CommandLine.Command(name = "SootWrapper")
class Cli implements Callable<Integer> {
    @CommandLine.Option(names = {"-u", "--user-code"}, description = "Path(s) to user code", required = true)
    Collection<Path> userCodePaths;

    @CommandLine.Option(names = {"-l", "--library-code"}, description = "Path(s) to library code", required = true)
    Collection<Path> libraryCodePaths;

    @CommandLine.Option(names = {"-o", "-f", "--output-file"}, description = "Path to output file for the call graph. Default is stdout")
    File outputFile;

    public static void main(String[] args) {
        System.err.printf("Running SootWrapper version %s%n", getFullVersion());

        CommandLine.IExecutionExceptionHandler errorHandler = (e, commandLine, parseResult) -> {
            commandLine.getErr().println(e.getMessage());
            commandLine.usage(commandLine.getErr());
            return commandLine.getCommandSpec().exitCodeOnExecutionException();
        };
        int exitCode = new CommandLine(new Cli()).setExecutionExceptionHandler(errorHandler).execute(args);
        System.exit(exitCode);
    }

    @Override
    public Integer call() throws Exception {
        checkExistsAndIsDir(userCodePaths, true);
        checkExistsAndIsDir(libraryCodePaths, false);
        BufferedWriter writer;
        if (outputFile != null) {
            if (outputFile.isDirectory()) {
                throw new IllegalArgumentException(String.format("Error: output file %s is a directory", outputFile.getAbsolutePath()));
            }
            if (!outputFile.createNewFile() && !outputFile.canWrite()) {
                throw new IllegalArgumentException(String.format("Error: output file %s can't be written to", outputFile.getAbsolutePath()));
            }
            writer = new BufferedWriter(new FileWriter(outputFile, StandardCharsets.UTF_8));
        } else {
            writer = new BufferedWriter(new OutputStreamWriter(System.out, StandardCharsets.UTF_8));
        }

        JSONWriter jwriter = new JSONWriter(writer);
        jwriter.object();
        jwriter.key("version").value(getCallGraphVersion());
        jwriter = jwriter.key("data").array();

        AnalysisResult res = SootWrapper.writeAnalysis(jwriter, userCodePaths, libraryCodePaths);

        jwriter.endArray().endObject();
        writer.close();

        int exitCode = 0;
        Set<String> phantoms = res.getPhantoms();
        Set<String> badPhantoms = res.getBadPhantoms();
        if (!phantoms.isEmpty() || !badPhantoms.isEmpty()) {
            System.err.println("NOTICE: Phantom classes detected! " +
                    "Phantom classes will not be analysed, make sure they are not meant to be. " +
                    "Phantom classes can be analysed by passing the path to their implementation " +
                    "to the library code option.");
        }
        if (!phantoms.isEmpty()) {
            System.err.println("The following classes are phantoms:");
            for (String phantom : phantoms) {
                System.err.println(phantom);
            }
        }
        if (!badPhantoms.isEmpty()) {
            exitCode = 2;
            System.err.println("WARNING: Important classes are phantoms! These are:");
            for (String badPhantom : badPhantoms) {
                System.err.println(badPhantom);
            }
        }

        return exitCode;
    }

    private static void checkExistsAndIsDir(Iterable<? extends Path> paths, boolean checkJar) throws FileNotFoundException {
        for (Path p : paths) {
            File f = p.toFile();
            if (!f.exists()) {
                throw new FileNotFoundException(String.format("Error: %s can't be found", p));
            }
            if (!f.isDirectory()) {
                // Check for .jar file
                if (checkJar) {
                    String fileName = f.getName();
                    int index = fileName.lastIndexOf('.');
                    if (index > 0) {
                        String extension = fileName.substring(index+1);
                        if (extension.equals("jar")) {
                            return;
                        }
                    }
                }

                throw new IllegalArgumentException(String.format("Error: %s is not a directory", p));
            }
        }
    }

    private static String getFullVersion() {
        String versionFromJar = Cli.class.getPackage().getImplementationVersion();
        return versionFromJar == null ? "?.?" : versionFromJar;
    }

    private static String getCallGraphVersion() {
        return getFullVersion().split("\\.")[0];
    }

}
