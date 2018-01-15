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
GetDictHandle	pDictionary��������������ڱ���ʵ���	����0����ʾ�ɹ�
����-1����ʾʧ��	��ôʵ���
*/
EXPORTDLL long GetDictHandle(void* &pDictionary);

/*
FreeDictHandle	pDictionary�����������
��Ǵ��ͷŵĴʵ���	����0	�ͷŴʵ���
*/
EXPORTDLL long FreeDictHandle(void* pDictionary);

/*
GetSegHandle	pDictionary���������������ѳɹ���ȡ�Ĵʵ���
pHnd��������������ڱ���ִʾ��	����0����ʾ�ɹ�
����-1����ʾʧ��	��ȡ�ִʾ��
*/
EXPORTDLL long GetSegHandle(void* pDictionary, void* &pHnd);

/*
FreeSegHandle	pHnd�������������Ǵ��ͷŵķִʾ��	����0	�ͷŷִʾ��
*/
EXPORTDLL long FreeSegHandle(void* pHnd);

/*
HCSegBuf	szInBuf��������������ִ��ַ���
lInBufLen��������������ִ��ַ�������
szOutBuf���������������ִʽ��
lOutBufLen���������������ַ���szOutBuf �ĳ���
pHnd������������ִʾ��	���طִʽ����szOutBuf�ĳ��ȣ�����-1��ʾʧ��	���ڶ��ַ���szInBuf���зִʣ������ִʽ�����浽szOutBuf����
weight_flag�����������Ϊ��ʱ���дʽ����Ȩ��ֵ�����Ϊ��ʱ���дʽ������Ȩ��ֵ���Ĭ��Ϊ�٣�������Ȩ�ء�
newmode_flag��Ĭ�ϲ�����Ĭ��Ϊ0ʱ������֮ǰ�ķִʷ�ʽ���ԡ���ɫõ�塱Ϊ�����ʿ����С���ɫ������õ�塱������ɫõ�塱���дʽ��Ϊ����ɫõ�塱��
			  Ϊ1ʱ���дʽ��Ϊ����ɫ���͡�õ�塱��
ע�⣬�����szOutBuf�Ĵ�С���������봮szOutBuf������
*/
/*(weight_flag����0ʱ����ӡȨ�ز���ӡ���ʣ�Ϊ1ʱ��ӡΪ-1��Ȩ�أ�Ϊ2ʱ��ӡ����Ȩ�ء�Right_All_flagΪ0ʱΪ��������дʣ�Ϊ1ʱΪȫ�д�)*/
EXPORTDLL long HCSegBuf(char* szInBuf, long lInBufLen, char* szOutBuf, long lOutBufLen, void* pHnd, int weight_flag = 0, bool Right_All_flag = 0, bool newmode_flag = 0);
//ֻ��ӡȨ��Ϊ-1��Ȩ��ֵ
EXPORTDLL long HCSegBuf_exe(char* szInBuf, long lInBufLen, char* szOutBuf, long lOutBufLen, void* pHnd, bool weight_flag = 0, bool newmode_flag = 0);
//�����д�
EXPORTDLL long HCSegBuf_S(char* szInBuf, long lInBufLen, char* szOutBuf, long lOutBufLen, void* pHnd, bool weight_flag = 0, bool newmode_flag = 0);

/*
HCSegFile	szInFile��������������ִ��ļ���
szOutFile���������������ִʽ���ļ���
pHnd������������ִʾ��	����0����ʾ�ɹ�
����-1����ʾʧ��	���ڶ��ı��ļ�szInFile���зִʣ������ִʽ�����浽szOutFile��
*/
EXPORTDLL long HCSegFile(char* szInFile, char* szOutFile, void* pHnd);

/*
ChangeDictFormat	sSrcName�������������ת���ʵ��ļ���
sDesName�����������ת����ʵ��ļ���	����0	�����Ĵʵ��ʽת��Ϊ���ṹ�Ķ����Ƹ�ʽ
ע�⣬ת����Ԫ�ʵ�ʱ��Դ�ļ���������BinaryDict.txt
*/
EXPORTDLL long ChangeDictFormat(const char *sSrcName, const char *sDesName);

#ifdef __cplusplus
}
#endif

#endif
