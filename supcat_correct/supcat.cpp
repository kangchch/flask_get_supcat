#include <iostream>
#include "HCSegDll.h"
#include <string>
#include <cstdlib>
#include <cstring>

using namespace std;

void* pDict = NULL;
void* pHnd = NULL;

bool InitSeg(){
    bool ret = GetDictHandle(pDict);
    if (0 == ret)
        ret = GetSegHandle(pDict, pHnd);

    if (0 == ret)
        return true;

    return false;
}

bool QuitSeg(){
    if (pHnd)
        FreeSegHandle(pHnd);

    if (pDict)
        FreeDictHandle(pDict);

    pHnd = NULL;
    pDict = NULL;
}

string SegWord(const char* word, int len){
    if (pHnd){
        char outBuf[2000] = {0};
        HCSegBuf((char*)word, len, outBuf, 1999, pHnd, 1, 1, 0);
        return string(outBuf);
    }
    return NULL;
}

void SegWordNew(char *&s, const char* word, int len){
    if (pHnd){
        s = (char*)malloc(2000);
        memset(s, 0, 2000);
        HCSegBuf((char*)word, len, s, 1999, pHnd, 1, 1, 0);
    }
}

int main(){
    InitSeg();

    if (pHnd){
        string in = "Ä¢¹½³äÆø³Ç±¤";
        string result = SegWord(in.c_str(), in.size());
        cout << result << endl;

        char* s = NULL;
        SegWordNew(s, in.c_str(), in.size());
        cout << s << endl;
        
    }

    QuitSeg();
    return 0;
}
