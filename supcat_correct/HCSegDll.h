#ifndef _HCSEGDLL_H_
#define _HCSEGDLL_H_

#ifdef WIN32
#define EXPORTDLL __declspec(dllexport)
#else
#define EXPORTDLL
#endif

#ifdef __cplusplus
extern "C"{
#endif

/*
GetDictHandle	pDictionary，输出参数，用于保存词典句柄	返回0，表示成功
返回-1，表示失败	获得词典句柄
*/
EXPORTDLL long GetDictHandle(void* &pDictionary);

/*
FreeDictHandle	pDictionary，输入参数，
标记待释放的词典句柄	返回0	释放词典句柄
*/
EXPORTDLL long FreeDictHandle(void* pDictionary);

/*
GetSegHandle	pDictionary，输入参数，标记已成功获取的词典句柄
pHnd，输出参数，用于保存分词句柄	返回0，表示成功
返回-1，表示失败	获取分词句柄
*/
EXPORTDLL long GetSegHandle(void* pDictionary, void* &pHnd);

/*
FreeSegHandle	pHnd，输入参数，标记待释放的分词句柄	返回0	释放分词句柄
*/
EXPORTDLL long FreeSegHandle(void* pHnd);

/*
HCSegBuf	szInBuf，输入参数，待分词字符串
lInBufLen，输入参数，待分词字符串长度
szOutBuf，输出参数，保存分词结果
lOutBufLen，输入参数，标记字符串szOutBuf 的长度
pHnd，输入参数，分词句柄	返回分词结果串szOutBuf的长度，返回-1表示失败	用于对字符串szInBuf进行分词，并将分词结果保存到szOutBuf串中
weight_flag，输入参数，为真时，切词结果带权重值输出，为假时，切词结果不带权重值输出默认为假，即不带权重。
newmode_flag，默认参数，默认为0时，采用之前的分词方式，以“红色玫瑰”为例，词库中有“红色”、“玫瑰”、“红色玫瑰”，切词结果为“红色玫瑰”；
			  为1时，切词结果为“红色”和“玫瑰”。
注意，输出串szOutBuf的大小至少是输入串szOutBuf的两倍
*/
/*(weight_flag等于0时不打印权重不打印辅词，为1时打印为-1的权重，为2时打印所有权重。Right_All_flag为0时为逆向最大切词，为1时为全切词)*/
EXPORTDLL long HCSegBuf(char* szInBuf, long lInBufLen, char* szOutBuf, long lOutBufLen, void* pHnd, int weight_flag = 0, bool Right_All_flag = 0, bool newmode_flag = 0);
//只打印权重为-1的权重值
EXPORTDLL long HCSegBuf_exe(char* szInBuf, long lInBufLen, char* szOutBuf, long lOutBufLen, void* pHnd, bool weight_flag = 0, bool newmode_flag = 0);
//单字切词
EXPORTDLL long HCSegBuf_S(char* szInBuf, long lInBufLen, char* szOutBuf, long lOutBufLen, void* pHnd, bool weight_flag = 0, bool newmode_flag = 0);

/*
HCSegFile	szInFile，输入参数，待分词文件名
szOutFile，输入参数，保存分词结果文件名
pHnd，输入参数，分词句柄	返回0，表示成功
返回-1，表示失败	用于对文本文件szInFile进行分词，并将分词结果保存到szOutFile中
*/
EXPORTDLL long HCSegFile(char* szInFile, char* szOutFile, void* pHnd);

/*
ChangeDictFormat	sSrcName，输入参数，待转换词典文件名
sDesName，输入参数，转换后词典文件名	返回0	将明文词典格式转换为树结构的二进制格式
注意，转换二元词典时，源文件名必须是BinaryDict.txt
*/
EXPORTDLL long ChangeDictFormat(const char *sSrcName, const char *sDesName);

#ifdef __cplusplus
}
#endif

#endif
