%module supcat
%include "cstring.i"
%include "std_string.i"
using namespace std;
%{
#define SWIG_FILE_WITH_INIT
extern bool InitSeg();
extern bool QuitSeg();
extern std::string SegWord(const char* word, int len);
extern void SegWordNew(char *&s, const char* word, int len);
%}

extern bool InitSeg();
extern bool QuitSeg();
extern string SegWord(const char* word, int len);
%cstring_output_allocate(char *&s, free(*$1));
extern void SegWordNew(char *&s, const char* word, int len);
