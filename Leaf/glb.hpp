/*

TODO: Add color coding for unix.


*/
#pragma once
#include <iostream>
#include <vector>
#include <map>
#include <string>
#include <regex>
#if defined(_WIN64) || defined(_WIN32)
#define WINDOWS
#define CON_RED 12
#define CON_PURPLE 13
#define CON_WHITE 15
#include <Windows.h>
#endif

// This is just a way to show that this function is a generator.
#define GENERATOR(X) X
#define RANGE(X,Y) (size_t (X)=0; (X) < (Y); (X)++)

#define uchar unsigned char
#define ushort unsigned short
#define uint unsigned int
#define ulong unsigned long

#define LOG(X) std::cout << X << std::endl
#define S_LOG(X) std::cout << (X) << std::endl

#define string_t std::string
#define list_t std::vector


template <class T>
const void LOG_V(list_t<T> v) {
    std::cout << '[';
    for (T i: v) {
        std::cout << i << ", ";
    }
    std::cout << ']' << std::endl;
}

// Old string_t and list_t {
    /*
    class string_t {
    public:
        char* ptr;
        size_t length;
        size_t rsp;
        string_t() : ptr(nullptr), length(0), rsp(0) {};
        string_t(size_t size) : ptr((char*)malloc(size*sizeof(char))),
                            length(size),
                            rsp(0) {};
        string_t(char* s) : ptr(s),
                            length(sizeof(s)),
                            rsp(this->length) {};
        string_t(const char* s) : ptr((char*)s),
                                length(sizeof(s)),
                                rsp(this->length) {};

        string_t(const string_t& other) {
            delete[] this->ptr;
            this->ptr = (char*)realloc(this->ptr, other.length);
            memcpy(this->ptr, other.ptr, other.length);
            this->length = other.length;
            this->rsp = other.rsp;
        }
    */
        /**
         * @brief Add an object at the end of the list (rsp)
         * @note Don't be worried about allocating too much memory or something like this, you're ok !
         * 
         * @param object
         */
    /*
        void append(char object) {
            if (this->rsp == this->length) {
                delete[] this->ptr;
                this->ptr = (char*) realloc(this->ptr, ++this->length);
                this->ptr[this->rsp] = object;
                this->rsp++;
            } else {
                this->ptr[this->rsp] = object;
                this->rsp++;
            }
        }

        char pop() {
            return this->ptr[--this->rsp];
        }

        void extend(char* objects, size_t size) {
            if (this->rsp+size >= this->length) {
                this->length += this->rsp+size-this->length;
                this->ptr = (char*) realloc(this->ptr, this->length);
                this->rsp = length;
            } else {
                memcpy(this->ptr+this->rsp, objects, size);
                this->rsp+=size;
            }
        }

        string_t copy() {
            string_t buf = *this;
            return buf;
        }

        inline void operator+=(string_t other) {
            this->extend(other.ptr, other.rsp);
        }

        inline void operator+=(char* other) {
            this->extend(other, (size_t)sizeof(other));
        }
        
        inline void operator+=(char other) {
            this->append(other);
        }

        inline char& operator[](size_t index) {
            return this->ptr[index];
        }

        char& operator[](signed int index) {
            if (index < 0) {
                index = this->size()+index;
            }
            return this->ptr[index];
        }

        void operator=(string_t other) {
            delete[] this->ptr;
            this->ptr = (char*)realloc(this->ptr, other.length);
            memcpy(this->ptr, other.ptr, other.length);
            this->length = other.length;
            this->rsp = other.rsp;
        }

        inline bool is_filled() {
            return this->rsp >= this->length;
        }

        void substr(int offset, int size) {
            char* keep = this->ptr;
            this->ptr = (char*)realloc(this->ptr, size);
            for (int i=0; i < size; i++) {
                ptr[i] = keep[i+offset];
            }
            delete[] keep;
        }

        void set_from_return(string_t other) {
            this->ptr = other.ptr;
            this->length = other.length;
            this->rsp = other.rsp;
        }
        
        template <class ...T>
        string_t format(T ...args) {
            snprintf(this->ptr, this->rsp, this->ptr, args...);
            return *this;
        }

        inline size_t size() {
            return this->rsp;
        }

        inline void extend(string_t ls) {
            // extend only to rsp because the part after index rsp doesn't really exist
            this->extend(ls.ptr, ls.rsp);
        }

        ~string_t() {
            delete[] ptr;
        }
    };
    */
    /*
    template <class T>
    class list_t {
    public:
        T* ptr;
        size_t length;
        size_t rsp;
        list_t() : length(0), rsp(0) {};
        list_t(size_t size) : ptr((T*)malloc(size*sizeof(T))),
                            length(size),
                            rsp(0) {};
    */ 
        /**
         * @brief Add an object at the end of the list (rsp)
         * @note Don't be worried about allocating too much memory or something like this, you're ok !
         * 
         * @param object
         */
    /*
        void append(T object) {
            if (this->rsp == this->length) {
                this->ptr = (T*) realloc(this->ptr, ++this->length);
                this->ptr[this->rsp] = object;
                this->rsp++;
            } else {
                this->ptr[this->rsp] = object;
                this->rsp++;
            }
        }

        T pop() {
            return this->ptr[--this->rsp];
        }

        void extend(T* objects, size_t size) {
            if (this->rsp+size >= this->length) {
                this->length += this->rsp+size-this->length;
                this->ptr = (T*) realloc(this->ptr, this->length);
                this->rsp = length;
            } else {
                memcpy(this->ptr+this->rsp, objects, size);
                this->rsp+=size;
            }
        }

        inline T& operator[](size_t index) {
            return this->ptr[index];
        }

        std::string toString() {
            std::string s = "[";
            for (size_t i=0; i < this->rsp; i++) {
                s += std::to_string(this->ptr[i]) + ", ";
            }
            s += ']';
            return s;
        }

        inline size_t size() {
            return this->rsp;
        }

        inline void extend(list_t ls) {
            // extend only to rsp because the part after index rsp doesn't really exist
            this->extend(ls.ptr, ls.rsp);
        }

        ~list_t() {
            delete[] ptr;
        }
    };
    */
// }

template <class T>
void swap(T& a, T& b) {
    T buf = a;
    a = b;
    b = buf;
}

template <class T, class lambda>
void bubbleSort(list_t<T> arr, lambda access_func)
{
   int i, j;
   for (i = 0; i < arr.size()-1; i++) for (j = 0; j < arr.size()-i-1; j++) if (access_func(arr[j]) > access_func(arr[j+1])) swap(arr[j], arr[j+1]);
}

string_t join(list_t<string_t> ls, string_t sep=" ") {
    if (ls.size() == 0) return "";
    string_t ret = ls[0];
    for (size_t i = 1; i < ls.size(); i++) {
        ret += sep + ls[i];
    }
    return ret;
}

string_t sliceOfString(string_t base, int start, int end=0) {
    string_t ret = base;
    if (end < 0) {
        end = base.size() + end;
    }
    ret.substr(start,end-start);
    return ret;
}

std::regex __cleanListOfString_trash("\\s+");
list_t<string_t> cleanListOfString(list_t<string_t> ls) {
    list_t<string_t> ret;
    for (string_t i: ls) {
        if (i.size() == 0 || std::regex_search(i, __cleanListOfString_trash)) {
            continue;
        }
        ret.push_back(i);
    }
    return ret;
}

string_t uncoverString(string_t s) {
    size_t count = 0;
    for (char i: s) {
        if (i == '(')
            count++;
        else
            break;
    }
    string_t ret;
    // Coherence of parenthesis already verified with splitText and splitLine.
    ret.reserve(s.size()-count*2);
    ret.insert(ret.cbegin(), s.cbegin()+count, s.cend()-count);
    return ret;
}

bool is_alphanum(string_t s) {
    for (char i: s) {
        if (i < 48 || (i > 57 && i < 65) || (i > 90 && i < 97) || i > 122)
            return false;
    }
    return true;
}
bool is_alphanum(char i) {
    return !(i < 48 || (i > 57 && i < 65) || (i > 90 && i < 97) || i > 122);
}
bool is_namesyntax(string_t s) {
    size_t number_count = 0;
    for (char i: s) {
        if (i < 48 || (i > 57 && i < 65) || (i > 90 && i < 97) || i > 122 || i != 95)
            return false;
        else if (i < 58)
            number_count++;
    }
    if (number_count == s.size())
        return false;
    return true;
}


int nline = -1;
FILE* rfile;
string_t rfile_name;
string_t c_output;
#ifdef WINDOWS
HANDLE hConsole = GetStdHandle(STD_OUTPUT_HANDLE);
#endif

string_t readLineN(FILE* file, int line) {
    // Don't forget to rewind the file before using it here !!!
    string_t ret;
    ret.reserve(256);
    int i_ret=0;
    while (line > 0) {
        if (ret[i_ret] = getc(file) == '\n') {
            line--;
            i_ret = 0;
        } else {
            i_ret++;
        }
    }
    return ret;
}

/**
 * @brief Return the next line with the line ending.
 * @param file The given file to pull out a line from
*/
string_t read_line(FILE* file) {
    string_t ret;
    ret.reserve(256);
    int rchar = getc(file);
    for (int i_ret=0; rchar != '\n' && rchar != EOF; i_ret++) {
        ret.push_back(rchar);
        rchar = getc(file);
    }
    if (rchar == '\n') {
        ret.push_back(rchar);
    } else if (rchar == EOF) {
        LOG("FILE END");
    }
    return ret;
}

string_t readfile(FILE* file) {
    string_t ret;
    fseek(file, 0, SEEK_END); // seek to end of file
    const size_t size = ftell(file); // get current file pointer
    fseek(file, 0, SEEK_SET);
    ret.reserve(size);
    int rchar;
    while ((rchar = getc(file)) != EOF)
        ret.push_back(rchar);
    return ret;
}

void traceback(string_t title, string_t description, const char* syntax = nullptr) {
    #ifdef WINDOWS
    SetConsoleTextAttribute(hConsole, CON_RED);
    #endif
    std::cerr << title << '\n';
    #ifdef WINDOWS
    SetConsoleTextAttribute(hConsole, CON_WHITE);
    #endif
    if (nline > -1) {
        std::cerr << rfile_name << ':' << nline << ":\n";
    }
    std::cerr << '\t' << "Info:" << '\n';
    std::cerr << "\t\t" << description << '\n';
    if (nline > -1) {
        std::cerr << '\t' << "Text:" << '\n';
        rewind(rfile);
        std::cerr << "\t\t" << readLineN(rfile, nline) << '\n';
    }
    if (syntax != nullptr) {
        std::cerr << '\t' << "Syntax:" << '\n';
        std::cerr << "\t\t" << syntax << '\n';
    }
}

void warning(string_t title, string_t description) {
    LOG("Deprecated usage of warning.");
    throw std::exception();
    #ifdef WINDOWS
    SetConsoleTextAttribute(hConsole, CON_PURPLE);
    #endif
    std::cout << title << '\n';
    #ifdef WINDOWS
    SetConsoleTextAttribute(hConsole, CON_WHITE);
    #endif
    if (nline > -1) {
        std::cout << rfile_name << ':' << nline << ":\n";
    }
    std::cout << '\t' << "Info:" << '\n';
    std::cout << "\t\t" << description << '\n';
    if (nline > -1) {
        std::cout << '\t' << "Text:" << '\n';
        std::cout << "\t\t" << readLineN(rfile, nline) << '\n';
    }
}