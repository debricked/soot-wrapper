import picocli.CommandLine;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.util.*;
import java.util.concurrent.Callable;

@CommandLine.Command(name = "SootWrapper")
class Cli implements Callable<Integer> {
    private static final int VERSION = 1;

    @CommandLine.Option(names = {"-u", "--user-code"}, description = "Path(s) to user code", required = true)
    ArrayList<Path> userCodePaths;

    @CommandLine.Option(names = {"-l", "--library-code"}, description = "Path(s) to library code", required = true)
    ArrayList<Path> libraryCodePaths;

    @CommandLine.Option(names = {"-f", "--output-file"}, description = "Path to output file for the call graph. Default is stdout")
    File outputFile;

    public static void main(String[] args) {
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
        checkExistsAndIsDir(userCodePaths);
        checkExistsAndIsDir(libraryCodePaths);
        if (outputFile != null) {
            if (outputFile.isDirectory()) {
                throw new IllegalArgumentException(String.format("Error: output file %s is a directory", outputFile.getAbsolutePath()));
            }
            if (!outputFile.createNewFile() && !outputFile.canWrite()) {
                throw new IllegalArgumentException(String.format("Error: output file %s can't be written to", outputFile.getAbsolutePath()));
            }
        }

        StringBuilder sb = new StringBuilder("{\n\t\"version\": ");
        sb.append(VERSION);
        sb.append(",\n\t\"data\":\n\t[");

        AnalysisResult res = SootWrapper.doAnalysis(userCodePaths, libraryCodePaths);
        Map<String[], Set<String[]>> calls = res.getCallGraph();
        int i = 0;
        for (String[] from : calls.keySet()) {
            sb.append("\n\t\t[\n\t\t\t\"").append(from[0]);
            sb.append("\",\n\t\t\t").append(from[1]);
            sb.append(",\n\t\t\t").append(from[2]);
            sb.append(",\n\t\t\t\"").append(from[3]);
            sb.append("\",\n\t\t\t").append(from[4]);
            sb.append(",\n\t\t\t").append(from[5]);
            sb.append(",\n\t\t\t[");
            int j = 0;
            for (String[] to : calls.get(from)) {
                sb.append("\n\t\t\t\t[\n\t\t\t\t\t\"").append(to[0]);
                sb.append("\",\n\t\t\t\t\t").append(to[1]).append("\n\t\t\t\t]");
                if (++j < calls.get(from).size()) {
                    sb.append(",");
                }
            }
            sb.append("\n\t\t\t]\n\t\t]");
            if (++i < calls.size()) {
                sb.append(",");
            }
        }
        sb.append("\n\t]");
        sb.append("\n}");

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

        if (outputFile == null) {
            System.out.println(sb.toString());
        } else {
            new FileOutputStream(outputFile).write(sb.toString().getBytes(StandardCharsets.UTF_8));
        }

        return exitCode;
    }

    private static void checkExistsAndIsDir(Collection<Path> paths) throws FileNotFoundException {
        for (Path p : paths) {
            File f = p.toFile();
            if (!f.exists()) {
                throw new FileNotFoundException(String.format("Error: %s can't be found", p.toString()));
            }
            if (!f.isDirectory()) {
                throw new IllegalArgumentException(String.format("Error: %s is not a directory", p.toString()));
            }
        }
    }

}
