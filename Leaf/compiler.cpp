#include "split_n_compile.hpp"

const char HELP[] = "leaf <file|(install,uninstall,config,help)> [params,...]";

const char HELP_DESCR[] = "file : The file that needs to be compiled.\n"
"install : Install a package, a module or a library.\n"
"uninstall : Uninstall a package, a module or a library.\n"
"config : Edit configuration file.\n"
"help | -h : Show this help\n"
"Compilation:\n"
"\t-toC : Only translate to C\n"
"\t-C X : Set C version to X\n"
"\t-O X : Set optimization level of Leaf and C compiler to X\n"
"\t-o X : Set output file.\n";

int main(int argc, char const *argv[])
{   
    atexit(context::empty_garbage);
    switch (argc) {
    case 1:
        traceback(
            "No file or command specified !",
            "You need to specify something to me if you want me to do something.",
            HELP
        );
        break;
    case 2: {
        if (argv[1] == "help") {
            std::cout << HELP_DESCR << std::endl;
        } else {
            rfile = fopen(argv[1], "r");
            if (!rfile) {
                traceback(
                    "Specified file doesn't exist.",
                    "Please try again with a correct file path."
                );
            }
            LOG("Compilation starts...");
            rfile_name = argv[1];
            nline = 1;
            top_compiler();
            LOG("Compilation done !");
            fclose(rfile);
        }
        break;
    }
    }


    return 0;
}

