# ver 1.2
#2019/04/05 19:40
# ver 1.1 : 190521, PLM update 이후 DB column 이름 변경 반영
# ver 1.1 : 190522, 삼성 단말 버전명 괄호 제거(G977N AP_CP 변경에 따른 기존 버전 ()안에 CP 버전 입력)

# % matplotlib inline
import pandas as pd
import matplotlib as mpl
import matplotlib.pylab as plt
# import seaborn as sns  ## matplotlib 쓰기 어려우므로 간결한 사용가능함.
import numpy as np
import os
import shutil


# pd.set_option('display.height', 1000)
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


# Function
# 특정 문자 들어간 컬럼 찾기
def search_column(table, str):
    val = []
    for col in table.columns:
        if str in col:
            val.append(col)
    return val


# pd.read_csv?

def StartMakeDb():

    #마지막 폴더 찾기
    filepath = "data"
    lastdate = max([filepath +"/"+ f for f in os.listdir(filepath)], key=os.path.getctime)
    print(lastdate)

    ### PLM 사이트 IOT/MR/OSU Excel 다운로드 파일 open
    ### 크롤링을 통해 추가 개선 필요
    # swver = pd.read_csv('swver_20190228.csv', encoding='cp949' )
    iot = pd.read_excel(os.path.join(os.getcwd(),lastdate,"iot.xls"))
    mr = pd.read_excel(os.path.join(os.getcwd(),lastdate,"mr.xls"))
    osu = pd.read_excel(os.path.join(os.getcwd(),lastdate,"osu.xls"))

    ### 망연동 타입 구분
    iot["Type"] = 'IOT'
    mr["Type"] = 'MR'
    osu["Type"] = 'OSU'

    swver = pd.concat([iot, osu, mr])
    # swver = swver.sort_values(by="생성일", ascending=True)
    print(swver.shape)
    swver.head()

    # merge 이후 reindex 해줘야 대입 가능해짐
    swver = swver.reset_index()
    swver = swver.drop("index", 1)

    # swver = pd.read_excel("data/iot/IOT_2019-03-11 12_31_41_단말시험 목록.xls")

    print(swver.shape)
    swver.head()

    # 예외 모델명 정리
    swver.loc[swver["모델명"] == "S10-5G(SM-G977N)", "모델명"] = "SM-G977N"
    swver.loc[swver["모델명"] == "V50(LM-V500N)", "모델명"] = "LM-V500N"

    swver.loc[swver["모델명"].str.contains("\("), "모델명"].unique()

    ### 망연동 생성일 기준 정렬
    swver = swver.sort_values(by="생성일", ascending=True)
    print(swver.shape)
    swver.head()

    swver["모델명"].unique().size

    swver.loc[swver["모델명"].str.contains("\("), "모델명"].unique()

    ### 모델명 정리, 괄호 제거
    swver["모델명_clear"] = swver["모델명"].str.replace(r"\(.*\)", "")
    swver.loc[swver["모델명"].str.contains("\("), ["모델명", "모델명_clear"]].head()

    swver["모델명_clear"].unique().size

    swver[swver["모델명_clear"] == 'SHV-E250S'].head()

    ### 출시여부 구분
    swver["출시"] = False
    swver.loc[swver["검증진행상태"].str.contains(" 합격"), "출시"] = True
    swver.loc[swver["검증진행상태"].str.contains("조건부합격"), "출시"] = True
    # swver.loc[swver["진행상태"].str.contains("불합격"), "출시"] = False
    swver[swver["출시"] != True].head()

    swver["검증진행상태"].unique()

    # ### 망연동 타입 구분
    # swver.loc[swver["검증진행상태"].str.contains("출시"), "Type"] = 'IOT'
    # swver.loc[swver["검증진행상태"].str.contains("MR"), "Type"] = 'MR'
    # swver.loc[swver["검증진행상태"].str.contains("OS"), "Type"] = 'OSU'
    # # swver.loc[swver["Type"].isnull()]

    # SW 버전 예외처리
    swver.loc[(swver["모델명_clear"].str.startswith("LGM-")) & (~swver["SW버전"].str.startswith("v")), "SW버전"] = 'v' + swver["SW버전"]
    swver.loc[(swver["모델명_clear"] == "LGM-G600S")]

    ### SW 버전 정리
    ###   삼성 : 3자리, G977 단말 부터 AP_CP 형식으로 변경
    ###   LG : 모델명 + 버전명
    ###   Alcatel : 그대로 사용
    swver['UA_ver'] = swver['SW버전']
    swver.loc[(swver['제조사'] == 'Alcatel'), 'UA_ver'] = swver['SW버전']
    #삼성
    swver.loc[(swver['제조사'] == '삼성전자'), 'UA_ver'] = swver['SW버전'].str.replace(r"\(.*\)","")  # 괄호 및 괄호 안 내용 제거
    swver.loc[((swver['제조사'] == '삼성전자') & (~swver['SW버전'].str.contains("_"))), 'UA_ver'] = swver['UA_ver'].str[-3:]
    #LG
    swver.loc[(swver['제조사'] == 'LG전자') & (swver['SW버전'].str.lower().str[0:1] == 'v'), 'UA_ver'] = \
        swver['모델명_clear'].str.split('-').str[1] + swver['SW버전'].str.lower().str[1:]

    swver.loc[(swver['제조사'] == 'TG&Co.') & (swver['모델명']== 'TG-L900S'), 'UA_ver'] = swver['SW버전'].str[8:]
    swver.head()

    #리스트 정렬하고 가장큰 값 반환
    def compare_date_group_return_largedate(group):
        list = group.values.tolist()
        list = [x for x in list if str(x) != 'nan'] #nan 제거
        if(len(list) >= 1):
            return max(list)
        return ""

    #동일 버전 제거 (SW버전 통합, 출시 OR 조건)
    swver1 = swver.groupby(['제조사', '모델명_clear', 'UA_ver'])['SW버전'].apply('/'.join).reset_index() #SW버전 통합, 연결
    swver2 = swver.groupby(['제조사', '모델명_clear', 'UA_ver'])['출시'].apply(any).reset_index() #출시 통합, OR 조건
    swver2_1 = swver.groupby(['제조사', '모델명_clear', 'UA_ver'])['승인일'].apply(compare_date_group_return_largedate).reset_index()  # 출시 통합, OR 조건
    swver2 = pd.merge(swver2, swver2_1)

    swver3 = pd.merge(swver1, swver2, on=['제조사', '모델명_clear', 'UA_ver'])

    #중복 제거
    swver = swver.drop_duplicates(subset=['제조사', '모델명_clear', 'UA_ver'], keep='first')
    #통합 Data 연결
    swver4 = pd.merge(swver, swver3, on=['제조사', '모델명_clear', 'UA_ver'])
    swver4['SW버전'] = swver4['SW버전_y']
    swver4['출시'] = swver4['출시_y']
    swver4['승인일'] = swver4['승인일_y']
    swver = swver4.drop(['SW버전_x', 'SW버전_y', '출시_x', '출시_y',  '승인일_x', '승인일_y'], axis=1)

    swver.loc[swver["모델명"].str.contains("F800")].head(3)

    #ongoing (검증진행 중)
    swver["ongoing"] = False
    swver.loc[swver["검증진행상태"].str.contains(" 시작"), "ongoing"] = True
    swver.loc[swver["검증진행상태"].str.contains(" 요청"), "ongoing"] = True
    swver.loc[swver["검증진행상태"].str.contains(" 대기"), "ongoing"] = True
    swver.loc[swver["검증진행상태"].str.contains(" 대기"), "ongoing"] = True

    swver["OS버전"].unique()

    swver.loc[swver["OS버전"].isnull(), "OS버전"] = '-'

    swver.loc[swver["OS버전"].str.startswith("Android OS"), "OS_Type"] = "Android"
    swver.loc[swver["OS버전"].str.startswith("Android OS"), "OS_ver"] = swver["OS버전"].str.split(" ").str[2]

    swver.loc[swver["OS버전"].str.startswith("Android Wear"), "OS_Type"] = "Android Wear"
    swver.loc[swver["OS버전"].str.startswith("Android Wear"), "OS_ver"] = swver["OS버전"].str.split(" ").str[2]

    swver.loc[swver["OS버전"].str.startswith("Windows"), "OS_Type"] = "Windows"
    swver.loc[swver["OS버전"].str.startswith("Windows"), "OS_ver"] = swver["OS버전"].str.split("Windows").str[1]

    swver.loc[swver["OS버전"].str.startswith("Bada"), "OS_Type"] = "Bada"
    swver.loc[swver["OS버전"].str.startswith("Bada"), "OS_ver"] = swver["OS버전"].str.split(" ").str[2]

    swver.loc[swver["OS버전"].str.startswith("Tizen"), "OS_Type"] = "Tizen"

    swver.head()

    # Android 버전별 Code Nmae 통합

    oscode = pd.read_excel("ref_data/Android_Code_Names.xlsx")

    print(oscode.shape)
    oscode


    def verget(ver, t=1):
        if "–" not in ver:
            return ver

        elif t == 1:  # start version
            return ver.split("–")[0].strip()
        elif t == 2:  # end version
            return ver.split("–")[1].strip()


    verget('1–3', 2)

    oscode["Code name_clear"] = oscode['Code name'].str.replace(r"\[.*\]", "")
    oscode["ver_start"] = oscode['Version number'].astype(str).apply(verget, t=1)
    oscode["ver_end"] = oscode['Version number'].astype(str).apply(verget, t=2)
    oscode

    list(range(0, oscode.index.size))


    # SW 버전에 Android CodeName 통합

    def mergeCodeName(ver):
        ver = str(ver)
        for i in range(0, oscode.index.size):
            if ver >= oscode.loc[i, 'ver_start'] and ver <= oscode.loc[i, 'ver_end']:
                return oscode.loc[i, "Code name_clear"]


    mergeCodeName("8.0")

    swver.loc[swver["OS_Type"] == "Android", "CodeName"] = swver["OS_ver"].apply(mergeCodeName)
    swver.loc[swver["OS_Type"] == "Android", "CodeName"].unique()

    swver.loc[swver["모델명_clear"].str.contains("LG")].head()

    # spec = pd.read_excel(os.path.join(os.getcwd(),lastdate,"spec.xlsx"), header=None)
    #
    #
    #
    # print(spec.shape)
    # spec.head()
    #
    # # 여러개의 multi column을 통합
    # spec.iloc[0:2] = spec.iloc[0:3].fillna(method='ffill', axis=1)
    #
    # spec.iloc[0:3] = spec.iloc[0:3].fillna('')
    #
    # spec.columns = spec.iloc[0:3].apply(lambda x: '.'.join([y for y in x if y]), axis=0)
    #
    # spec = spec.iloc[3:]
    # spec.index = range(0, len(spec.index))
    #
    # print(spec.shape)
    # spec.head()
    #
    # # spec.columns
    #
    # column = search_column(spec, "모델명")
    #
    # spec['모델명.모델명'] = spec['모델명.모델명'].str.replace("\t", "")
    # # Spec 예외 처리
    # # 갤럭시 그랜드 (SAMSUNG GALAXY GRAND) (SHV-E275S) 추가 필요
    #
    #
    # spec.head()
    #
    # ##Spec column 정보 추출
    # sample_model = ["SM-G977N", "LM-V500N"]
    # ss = spec["모델명.모델명"] == sample_model[0]
    # lg = spec["모델명.모델명"] == sample_model[1]
    # t = spec.loc[ss | lg].T
    # t.columns = sample_model
    #
    # print("## Spec column 정보 저장")
    # file_name = os.path.join(os.getcwd(), lastdate, "spec_column_" + lastdate.split("/")[1] + ".xls")
    # t.to_excel(file_name)
    # print("Write Success : " + file_name)
    #
    #
    # # SW버전에 Pet Name 통합
    #
    # def mergePetName(model):
    #     model = str(model)
    #
    #
    #     for y in range(0, spec.index.size):
    #         if model == spec.loc[y, '모델명.모델명']:
    #             return spec.loc[y, "애칭.Pet Name(영문)"]
    #
    #
    # mergePetName("SM-R815N")
    #
    #
    # def mergeOwner(model):
    #     model = str(model)
    #
    #     for y in range(0, spec.index.size):
    #         if model == spec.loc[y, '모델명.모델명']:
    #             return spec.loc[y, "담당자.망연동 담당자"]
    #
    #
    # mergeOwner("SM-J415N")

    # swver["PetName"] = swver["모델명_clear"].apply(mergePetName)
    # swver["PetName"] = swver["모델명"].apply(mergePetName)
    swver["PetName"] = swver["Petname(애칭)"]

    # swver["owner"] = swver["모델명_clear"].apply(mergeOwner)
    # swver["owner"] = swver["모델명"].apply(mergeOwner)
    swver["owner"] = swver["승인담당자"]
    # swver[swver["모델명_clear"].str.contains("SHV-E470")].head()

    # 모델명 예외처리
    swver.loc[swver["모델명_clear"] == "LGM-G600SP", 'PetName'] = "LG G6 Plus"
    swver.loc[swver["모델명_clear"] == "LGM-X600SP", 'PetName'] = "LG Q6 Plus"

    # UA 모델명 예외 처리
    swver["ua_model"] = swver["모델명_clear"]
    swver.loc[swver["ua_model"] == "LGM-X600SP", 'ua_model'] = 'LGM-X600S'
    swver.loc[((swver["ua_model"] == "LGM-G600SP") & ~(swver["SW버전"].str.startswith("v3"))), 'ua_model'] = 'LGM-G600S'  #G6 Q-OS 부터는 모델명 전체 추가됨
    swver.loc[swver["PetName"] == "LG G6 Plus"].head()

    # G6 Pro 모델 추가
    g6pro = swver.loc[swver["PetName"] == "LG G6 Plus"]
    g6pro.loc[:, "모델명"] = 'LGM-G600SR'
    g6pro.loc[:, "모델명_clear"] = 'LGM-G600SR'
    g6pro.loc[:, 'Petname(애칭)'] = "LG G6 Pro"
    g6pro.loc[:, "UA_ver"] = g6pro["UA_ver"].str.replace("SP", "SR")
    g6pro.loc[:, "ua_model"] = g6pro["ua_model"].str.replace("SP", "SR")
    # g6pro.loc[:, "승인담당자"] = ""
    swver1 = pd.concat([swver, g6pro])

    # LG 출시 모델 버전 추가
    lge = swver1.loc[(swver1["제조사"] == "LG전자") & (swver1["SW버전"].str.startswith("v")) & (swver1["OS_Type"].str.startswith("Android"))]
    lge.loc[:, "UA_ver"] = "ver" + lge["SW버전"].str[1:] # v10a -> ver10a (LGU, OMD 모델)
    lge.loc[:, "승인담당자"] = ""
    lge.loc[:, "생성일"] = ""
    swver1 = pd.concat([swver1, lge])

    swver1 = swver1.sort_values(by="생성일", ascending=True)
    swver1 = swver1.reindex()
    print(swver1.shape)
    swver1.loc[swver1["ua_model"] == "LGM-G600S"].head(3)


    ## SW 버전 파일 저장
    column = ['제조사', 'Petname(애칭)', '모델명_clear', 'SW버전', 'ua_model', 'UA_ver', 'TYPE', '생성일', '승인일', '출시', "ongoing", 'Type', 'OS_Type', 'OS_ver', 'CodeName', "승인담당자", 'owner']
    swver1 = swver1[column]
    swver1.columns = ['manufacturer', 'pet_name', 'model', 'sw_ver', 'ua_model', 'ua_ver', 'ue_type', 'creation_date', 'acceptance_date',
                      'release_sw', "ongoing", 'release_type', 'os_type', 'os_ver', 'codeName', 'manager', 'owner']
    #Data 연동 공개 범위 지정
    cvs_columns = ['manufacturer', 'pet_name', 'model', 'sw_ver', 'ua_model', 'ua_ver', 'ue_type', 'creation_date',
                      'acceptance_date', 'release_sw', "ongoing", 'release_type', 'os_type', 'os_ver', 'codeName']

    print("## SW 버전 파일 저장")
    file_name = os.path.join(os.getcwd(),lastdate,"plm_swver_DataWarehouse_" + lastdate.split("/")[1] + ".xls")
    file_name2 = os.path.join(os.getcwd(),lastdate,"plm_swver_DataWarehouse.xls")
    file_name_csv1 = os.path.join(os.getcwd(), lastdate, "plm_swver_" + lastdate.split("/")[1].split("_")[0] + ".csv") ##update 날짜 표시
    # file_name_csv2 = os.path.join(os.getcwd(), lastdate, "plm_swver_" + lastdate.split("/")[1] + ".csv")
    swver1.to_excel(file_name, index=False)
    shutil.copy2(file_name, file_name2)
    swver1[cvs_columns].to_csv(file_name_csv1, mode='w')
    # swver1.to_csv(file_name_csv2, mode='w')
    print("Write Success : " + file_name)

    try:
        file_name = os.path.join("O:\\","2.전송파일함(PC - myDesk)","plm_swver_DataWarehouse_" + lastdate.split("/")[1] + ".xls")
        swver1.to_excel(file_name, index=False)
        print("Write Success : " + file_name)
    except Exception as ex:
        print("Write Fail : Can't access O: drive;" + str(ex))

    # ## spec 모델 list 저장
    #
    # column = ['제조사.제조사', '애칭.Pet Name(애칭)', '애칭.Pet Name(영문)', '모델명.모델명', '형태.단말형태', '출시일.출시일']
    # spec1 = spec[column]
    # column_new = ['manufacturer', 'pet_name_kor', 'pet_name_eng', 'model', 'ue_type', 'ue_release_date']
    # spec1.columns = column_new

    print("## 모델 list 저장")
    file_name = os.path.join(os.getcwd(),lastdate,"plm_ue_list_DataWarehouse_" + lastdate.split("/")[1] + ".xls")
    file_name_csv1 = os.path.join(os.getcwd(), lastdate, "plm_ue_list_" + lastdate.split("/")[1].split("_")[0] + ".csv") ##update 날짜 표시
    # file_name_csv2 = os.path.join(os.getcwd(), lastdate, "plm_ue_list_" + lastdate.split("/")[1] + ".csv") ##update 날짜 + 시간까지 표시
    # spec1.to_excel(file_name, index=False)
    swver1.to_csv(file_name_csv1)
    # swver1.to_csv(file_name_csv2)
    print("Write Success : " + file_name)

    # try:
    #     file_name = os.path.join("O:\\","2.전송파일함(PC - myDesk)","plm_ue_list_DataWarehouse_" + lastdate.split("/")[1] + ".xls")
    #     spec1.to_excel(file_name, index=False)
    #     print("Write Success : " + file_name)
    # except Exception as ex:
    #     print("Write Fail : Can't access O: drive;" + str(ex))
    #
    # print("Completed!!")


## Start
if __name__ == "__main__":
    StartMakeDb()
